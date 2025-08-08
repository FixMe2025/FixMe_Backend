from __future__ import annotations

from typing import Dict, Any, List, Optional, TypedDict
import logging
import torch

from transformers import (
    AutoTokenizer,
    AutoModelForSeq2SeqLM,
)

from langgraph.graph import StateGraph, END

from app.models.spellcheck import Correction
from app.core.config import get_settings


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

        self._load_models()
        self._build_graph()

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

            inputs = self.typo_tokenizer(
                state["input_text"],
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True,
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = self.typo_model.generate(
                    **inputs,
                    max_length=min(512, int(inputs['input_ids'].shape[1] * 1.5)),
                    num_beams=4,
                    early_stopping=True,
                    do_sample=False,
                    pad_token_id=self.typo_tokenizer.eos_token_id,
                )
            corrected = self.typo_tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
            state["step1_text"] = corrected if corrected else state["input_text"]
            state["corrections_step1"] = self._extract_corrections(state["input_text"], state["step1_text"], "타이포/띄어쓰기")
            return state

        def step2_grammar(state: PipelineState) -> PipelineState:
            base_text = state.get("step1_text") or state["input_text"]
            if not self.grammar_model or not self.grammar_tokenizer:
                state["final_text"] = base_text
                state["corrections_final"] = []
                return state

            inputs = self.grammar_tokenizer(
                base_text,
                return_tensors="pt",
                truncation=True,
                max_length=512,
                padding=True,
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            with torch.no_grad():
                outputs = self.grammar_model.generate(
                    **inputs,
                    max_length=min(512, int(inputs['input_ids'].shape[1] * 1.5)),
                    num_beams=4,
                    early_stopping=True,
                    do_sample=False,
                    pad_token_id=self.grammar_tokenizer.eos_token_id,
                )
            corrected = self.grammar_tokenizer.decode(outputs[0], skip_special_tokens=True).strip()
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
            return all([
                self.typo_model is not None,
                self.typo_tokenizer is not None,
                self.grammar_model is not None,
                self.grammar_tokenizer is not None,
            ])
        except Exception:
            return False


_pipeline_instance: Optional[LangGraphSpellPipeline] = None


def get_langgraph_pipeline() -> LangGraphSpellPipeline:
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = LangGraphSpellPipeline()
    return _pipeline_instance


