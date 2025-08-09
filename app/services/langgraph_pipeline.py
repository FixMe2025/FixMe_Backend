from __future__ import annotations

from typing import Dict, Any, List, Optional, TypedDict
import logging
import re
import unicodedata
import torch

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
)

from langgraph.graph import StateGraph, END

from app.models.spellcheck import Correction
from app.core.config import get_settings
from app.utils.text_utils import calculate_text_similarity


logger = logging.getLogger(__name__)
settings = get_settings()


class PipelineState(TypedDict, total=False):
    input_text: str
    step1_text: str
    final_text: str
    corrections_step1: List[Correction]
    corrections_final: List[Correction]


class LangGraphSpellPipeline:
    """
    j5ng/et5-typos-corrector (1차 타이포/띄어쓰기) → theSOL1/kogrammar-base (2차 문법/자연스러움)
    순차 파이프라인을 LangGraph로 구성
    """

    def __init__(self) -> None:
        self.device: str = "cuda" if torch.cuda.is_available() and settings.use_gpu else "cpu"

        # 1차 모델 (ET5)
        self.typo_tokenizer = None
        self.typo_model = None

        # 2차 모델 (KoGrammar)
        self.grammar_tokenizer = None
        self.grammar_model = None

        self._graph = None

        # lazy-load: 최초 호출 시 모델/그래프 빌드
        # self._load_models()
        # self._build_graph()

    def _load_models(self) -> None:
        try:
            # 1차: et5-typos-corrector
            logger.info(f"Loading step1 model: {settings.secondary_model_name}")
            self.typo_tokenizer = AutoTokenizer.from_pretrained(
                settings.secondary_model_name,
                cache_dir=settings.model_cache_dir,
            )
            self.typo_model = AutoModelForSeq2SeqLM.from_pretrained(
                settings.secondary_model_name,
                cache_dir=settings.model_cache_dir,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
            )
            if self.device == "cpu":
                self.typo_model = self.typo_model.to(self.device)

            # 2차: kogrammar-base
            logger.info(f"Loading step2 model: {settings.grammar_model_name}")
            self.grammar_tokenizer = AutoTokenizer.from_pretrained(
                settings.grammar_model_name,
                cache_dir=settings.model_cache_dir,
            )
            self.grammar_model = AutoModelForSeq2SeqLM.from_pretrained(
                settings.grammar_model_name,
                cache_dir=settings.model_cache_dir,
                torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
                device_map="auto" if self.device == "cuda" else None,
            )
            if self.device == "cpu":
                self.grammar_model = self.grammar_model.to(self.device)

            logger.info("LangGraph pipeline models loaded")
        except Exception as e:
            logger.error(f"Failed to load pipeline models: {e}")
            self.typo_model = None
            self.typo_tokenizer = None
            self.grammar_model = None
            self.grammar_tokenizer = None

    def _build_graph(self) -> None:
        graph = StateGraph(PipelineState)

        def step1_typos(state: PipelineState) -> PipelineState:
            if not self.typo_model or not self.typo_tokenizer:
                state["step1_text"] = state["input_text"]
                state["corrections_step1"] = []
                return state

            corrected = self._generate_seq2seq(
                tokenizer=self.typo_tokenizer,
                model=self.typo_model,
                text=state["input_text"],
                num_beams=4,
                do_sample=False,
                max_length=512,
            )
            state["step1_text"] = corrected if corrected else state["input_text"]
            state["corrections_step1"] = self._extract_corrections(state["input_text"], state["step1_text"], "타이포/띄어쓰기")
            return state

        def step2_grammar(state: PipelineState) -> PipelineState:
            base_text = state.get("step1_text") or state["input_text"]
            if not self.grammar_model or not self.grammar_tokenizer:
                state["final_text"] = base_text
                state["corrections_final"] = []
                return state

            prompt = self._build_grammar_prompt(base_text)
            corrected_raw = self._generate_seq2seq(
                tokenizer=self.grammar_tokenizer,
                model=self.grammar_model,
                text=prompt,
                num_beams=6,
                do_sample=False,
                max_length=512,
            )
            corrected = self._force_single_sentence(self._clean_output(corrected_raw, base_text))
            # 공백만 변경되었거나 변화가 없으면 강한 지시 + 샘플링으로 재시도
            if (
                self._is_only_spacing_change(base_text, corrected)
                or corrected == base_text
                or self._looks_like_prompt_echo(corrected)
                or not self._is_semantically_close(base_text, corrected)
            ):
                corrected_retry_raw = self._generate_seq2seq(
                    tokenizer=self.grammar_tokenizer,
                    model=self.grammar_model,
                    text=self._build_grammar_prompt_stronger(base_text),
                    num_beams=8,
                    do_sample=True,
                    temperature=0.7,
                    top_p=0.9,
                    max_length=512,
                )
                corrected_retry = self._force_single_sentence(self._clean_output(corrected_retry_raw, base_text))
                if (
                    corrected_retry
                    and corrected_retry != base_text
                    and not self._looks_like_prompt_echo(corrected_retry)
                    and self._is_semantically_close(base_text, corrected_retry)
                ):
                    corrected = corrected_retry
                else:
                    corrected = base_text
            state["final_text"] = corrected if corrected else base_text
            state["corrections_final"] = self._extract_corrections(base_text, state["final_text"], "문법/자연스러움")
            return state

        graph.add_node("step1_typos", step1_typos)
        graph.add_node("step2_grammar", step2_grammar)
        graph.add_edge("step1_typos", "step2_grammar")
        graph.add_edge("step2_grammar", END)
        graph.set_entry_point("step1_typos")

        self._graph = graph.compile()

    def run(self, text: str) -> Dict[str, Any]:
        if self.typo_model is None or self.grammar_model is None:
            self._load_models()
        if self._graph is None:
            self._build_graph()
        state: PipelineState = {"input_text": text}
        result: PipelineState = self._graph.invoke(state)

        # 통합 교정 리스트 구성
        corrections: List[Correction] = []
        corrections.extend(result.get("corrections_step1", []))
        for corr in result.get("corrections_final", []):
            if corr not in corrections:
                corrections.append(corr)

        return {
            "original_text": text,
            "corrected_text": result.get("final_text") or result.get("step1_text") or text,
            "corrections": [c.dict() for c in corrections],
            "stage_texts": {
                "step1": result.get("step1_text") or text,
                "final": result.get("final_text") or result.get("step1_text") or text,
            },
        }

    @staticmethod
    def _extract_corrections(original: str, corrected: str, kind: str) -> List[Correction]:
        corrections: List[Correction] = []
        if not original or not corrected or original == corrected:
            return corrections
        corrections.append(Correction(original=original, corrected=corrected, type=kind))
        return corrections

    def is_healthy(self) -> bool:
        try:
            if self.typo_model is None or self.grammar_model is None:
                self._load_models()
            return all([
                self.typo_model is not None,
                self.typo_tokenizer is not None,
                self.grammar_model is not None,
                self.grammar_tokenizer is not None,
            ])
        except Exception:
            return False

    # --- Helpers ---
    def _generate_seq2seq(
        self,
        tokenizer,
        model,
        text: str,
        num_beams: int = 4,
        do_sample: bool = False,
        temperature: float = 1.0,
        top_p: float = 1.0,
        max_length: int = 512,
    ) -> str:
        inputs = tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=max_length,
            padding=True,
        )
        inputs = {k: v for k, v in inputs.items() if k != "token_type_ids"}
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        gen_kwargs: Dict[str, Any] = dict(
            max_length=min(max_length, int(inputs["input_ids"].shape[1] * 1.5)),
            num_beams=num_beams,
            early_stopping=True,
            pad_token_id=tokenizer.eos_token_id,
            no_repeat_ngram_size=2,
        )
        if do_sample:
            gen_kwargs.update(dict(do_sample=True, temperature=temperature, top_p=top_p))
        else:
            gen_kwargs.update(dict(do_sample=False))

        with torch.no_grad():
            outputs = model.generate(**inputs, **gen_kwargs)
        text_out = tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
        # 기본 공백 정리
        text_out = re.sub(r"\s+", " ", text_out).strip()
        return text_out

    def _build_grammar_prompt(self, text: str) -> str:
        # 의미 보존, 자연스러움, 결과만 출력. 모델이 프롬프트를 복창해도 정답만 추출할 수 있도록 '정답:' 마커 사용
        return (
            "아래 문장의 모든 맞춤법, 오타, 문법을 교정하고 더 자연스럽게 바꾸세요. "
            "의미는 보존하고, 결과만 한 문장으로 출력하세요.\n"
            f"문장: {text}\n정답:"
        )

    def _build_grammar_prompt_stronger(self, text: str) -> str:
        # 강한 지시 + 간단 예시(few-shot)
        return (
            "다음 작업을 수행하세요: (1) 오타/철자/맞춤법/띄어쓰기/문법 오류를 모두 교정, (2) 의미는 보존, (3) 결과만 출력.\n"
            "예시) 입력: 오늘 날씨가말다. -> 출력: 오늘 날씨가 맑다.\n"
            "입력: " + text + "\n출력:"
        )

    def _is_only_spacing_change(self, a: str, b: str) -> bool:
        if a == b:
            return False
        return "".join(a.split()) == "".join(b.split())

    def _looks_like_prompt_echo(self, text: str) -> bool:
        patterns = [
            r"아래 문장의 모든 맞춤법",
            r"다음 작업을 수행하세요",
            r"문장:\s*",
            r"입력:\s*",
            r"정답:\s*",
            r"출력:\s*",
        ]
        return any(re.search(p, text) for p in patterns)

    def _clean_output(self, text: str, original: str) -> str:
        # 1) 프롬프트 잔여 제거: 정답:/출력:/문장:/입력: 등 이후만 남김
        for marker in ["정답:", "출력:"]:
            if marker in text:
                text = text.split(marker, 1)[-1]
        # 문장:, 입력:은 앞부분 제거
        for marker in ["문장:", "입력:"]:
            if marker in text:
                text = text.split(marker, 1)[-1]
        # 2) 알려진 안내문 제거
        text = re.sub(r"아래 문장의 모든 맞춤법[^\n]*", "", text).strip()
        text = re.sub(r"다음 작업을 수행하세요[^\n]*", "", text).strip()
        # 3) 제어문자/결합부호 제거
        text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
        # 4) 허용 문자만 유지(한글/영문/숫자/일부 구두점)
        text = re.sub(r"[^가-힣a-zA-Z0-9\s.,!?'\"()\-]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        # 5) 공백만 변경되었거나 너무 짧으면 원문 사용
        if not text:
            return original
        return text

    def _is_semantically_close(self, a: str, b: str) -> bool:
        try:
            sim = calculate_text_similarity(a, b)
        except Exception:
            # 간단 fallback: 공백 제거 문자열 유사도 근사
            from difflib import SequenceMatcher
            sim = SequenceMatcher(None, "".join(a.split()), "".join(b.split())).ratio()
        if sim < 0.5:
            return False
        return self._content_coverage_ok(a, b)

    def _content_coverage_ok(self, base: str, out: str) -> bool:
        def tokens(s: str) -> List[str]:
            return [t for t in re.split(r"\W+", s) if t and len(t) >= 2]
        base_tokens = tokens(base)
        if not base_tokens:
            return True
        covered = sum(1 for t in set(base_tokens) if t in out)
        return covered / max(1, len(set(base_tokens))) >= 0.5

    def _force_single_sentence(self, text: str) -> str:
        # 첫 문장만 유지
        parts = re.split(r"(?<=[.!?])\s+", text)
        first = parts[0].strip() if parts else text.strip()
        return first


_pipeline_instance: Optional[LangGraphSpellPipeline] = None


def get_langgraph_pipeline() -> LangGraphSpellPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = LangGraphSpellPipeline()
    return _pipeline_instance
