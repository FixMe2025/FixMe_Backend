import torch
from typing import List, Dict
from ..models.state_models import GraphState
from ..utils.text_processor import TextProcessor
from ..utils.korean_validator import KoreanValidator
from ..utils.correction_rules import CorrectionRules
from ..config import settings
import traceback


class WorkflowNodes:
    """LangGraph 워크플로우 노드들을 관리하는 클래스"""
    
    def __init__(self, tokenizer_base, model_base, pipe_lm, device, dmp):
        self.tokenizer_base = tokenizer_base
        self.model_base = model_base
        self.pipe_lm = pipe_lm
        self.device = device
        self.dmp = dmp

    def smart_text_splitting(self, state: GraphState) -> GraphState:
        """0단계: 텍스트를 문맥을 보존하며 스마트하게 분할"""
        print("Running smart text splitting...")
        original_text = state["original_text"]
        
        # 텍스트 길이 검증
        if len(original_text) > settings.MAX_LENGTH:
            return {
                **state,
                "error": f"텍스트가 최대 길이({settings.MAX_LENGTH}자)를 초과했습니다.",
                "text_chunks": [],
                "processed_chunks": []
            }
        
        text_chunks = TextProcessor.smart_split_text(original_text)
        print(f"Text split into {len(text_chunks)} chunks")
        
        return {
            **state,
            "text_chunks": text_chunks,
            "processed_chunks": [],
        }

    def initial_correction(self, state: GraphState) -> GraphState:
        """1단계: kogrammar-base 모델을 사용한 기본 교정"""
        print("Running initial correction...")
        text_chunks = state.get("text_chunks", [])
        
        if not text_chunks:
            # 분할되지 않은 경우 원본 텍스트 사용
            original_text = state["original_text"]
            text_chunks = TextProcessor.smart_split_text(original_text)

        if not self.model_base:
            return {
                **state,
                "processed_chunks": text_chunks,
                "corrected_text": " ".join(text_chunks),
                "error": "Base model not loaded.",
            }

        processed_chunks = []
        for chunk in text_chunks:
            # 1-1. 사전 기반 교정
            text_after_dict = CorrectionRules.apply_comprehensive_corrections(chunk)

            # 1-2. 모델 기반 교정
            try:
                # 입력 텍스트에 적절한 프롬프트 추가 (kogrammar-base 모델용)
                model_input = text_after_dict
                
                inputs = self.tokenizer_base.encode(
                    model_input, 
                    return_tensors="pt",
                    max_length=300,
                    truncation=True
                ).to(self.device)
                
                with torch.no_grad():
                    outputs = self.model_base.generate(
                        inputs,
                        max_new_tokens=len(model_input) + 50,  # 입력 길이 기반으로 제한
                        num_beams=3,
                        early_stopping=True,
                        do_sample=False,
                        pad_token_id=self.tokenizer_base.pad_token_id,
                        eos_token_id=self.tokenizer_base.eos_token_id,
                        no_repeat_ngram_size=2,
                        repetition_penalty=1.2,  # 반복 페널티 추가
                    )
                
                corrected_chunk = self.tokenizer_base.decode(
                    outputs[0], skip_special_tokens=True
                ).strip()
                
                # 출력 검증: 한국어 텍스트 범위 및 길이 체크
                if not KoreanValidator.is_valid_korean_output(corrected_chunk, text_after_dict):
                    print(f"Invalid model output detected, using preprocessed text")
                    corrected_chunk = text_after_dict
                
                processed_chunks.append(corrected_chunk)
                
            except Exception as e:
                print(f"Error processing chunk: {e}")
                # 모델 처리 실패시 전처리된 텍스트 사용
                processed_chunks.append(text_after_dict)

        # 청크들을 자연스럽게 재조합
        corrected_text = TextProcessor.rejoin_chunks(processed_chunks)
        return {
            **state, 
            "processed_chunks": processed_chunks,
            "corrected_text": corrected_text
        }

    def refine_correction(self, state: GraphState) -> GraphState:
        """2단계: LLM을 사용한 상세 교정"""
        print("Running refinement with LLM...")
        text_to_refine = state["corrected_text"]

        # LLM 모델이 로드되지 않았거나 문제가 있으면 스킵
        if not self.pipe_lm:
            print("LLM not available, skipping refinement")
            return {**state}

        try:
            # 텍스트가 너무 길면 청크별로 처리
            if len(text_to_refine) > 300:
                print("Text too long for LLM, using previous result")
                return {**state}
            
            sequences = self.pipe_lm(
                text_to_refine,
                max_new_tokens=400,
                num_beams=3,
                early_stopping=True,
                do_sample=False,
                temperature=1.0,
                pad_token_id=self.pipe_lm.tokenizer.pad_token_id,
            )
            refined_text = sequences[0]["generated_text"].strip()
            
            # 결과가 너무 다르면 이전 결과 사용
            if len(refined_text) < len(text_to_refine) * 0.7:
                print("LLM output too short, keeping previous result")
                refined_text = text_to_refine

        except Exception as e:
            print(f"LLM refinement error: {e}")
            traceback.print_exc()
            refined_text = text_to_refine

        return {**state, "corrected_text": refined_text}

    def generate_suggestions(self, state: GraphState) -> GraphState:
        """3단계: 더 나은 문장 표현 제안"""
        print("Generating style suggestions...")
        corrected_text = state["corrected_text"]
        
        # 기본 문장 개선 규칙
        suggestions = []
        
        # 1. 간결함 개선 제안
        if "그런데" in corrected_text:
            suggestions.append({
                "type": "간결함",
                "original": "그런데",
                "suggestion": "하지만",
                "reason": "더 간결한 표현"
            })
        
        # 2. 정중한 표현 제안
        if corrected_text.count("이다") > 0:
            suggestions.append({
                "type": "정중함",
                "original": "이다",
                "suggestion": "입니다",
                "reason": "더 정중한 표현"
            })
        
        # 3. 반복 표현 감지
        words = corrected_text.split()
        word_counts = {}
        for word in words:
            if len(word) > 1:  # 한 글자 단어는 제외
                word_counts[word] = word_counts.get(word, 0) + 1
        
        for word, count in word_counts.items():
            if count > 2:  # 3번 이상 반복
                suggestions.append({
                    "type": "반복성",
                    "original": word,
                    "suggestion": f"'{word}' 반복 사용",
                    "reason": f"'{word}'이(가) {count}번 반복됩니다. 다양한 표현을 고려해보세요."
                })
        
        # 4. 문장 길이 개선 제안
        sentences = [s.strip() for s in corrected_text.split('.') if s.strip()]
        for sentence in sentences:
            if len(sentence) > 100:  # 100자 이상인 긴 문장
                suggestions.append({
                    "type": "가독성",
                    "original": sentence[:50] + "...",
                    "suggestion": "문장 분리 권장",
                    "reason": "긴 문장을 여러 개의 짧은 문장으로 나누면 가독성이 향상됩니다."
                })
        
        return {**state, "suggestions": suggestions}

    def generate_diff(self, state: GraphState) -> GraphState:
        """최종 교정본과 원본을 비교하여 교정 목록 생성"""
        print("Generating diff...")
        original = state["original_text"]
        corrected = state["corrected_text"]

        diffs = self.dmp.diff_main(original, corrected)
        self.dmp.diff_cleanupSemantic(diffs)

        corrections = []
        original_word = ""
        corrected_word = ""

        for op, data in diffs:
            if op == self.dmp.DIFF_DELETE:
                original_word += data
            elif op == self.dmp.DIFF_INSERT:
                corrected_word += data
            elif op == self.dmp.DIFF_EQUAL:
                if original_word or corrected_word:
                    if original_word.strip() or corrected_word.strip():
                        correction_type = (
                            "띄어쓰기"
                            if original_word.replace(" ", "")
                            == corrected_word.replace(" ", "")
                            else "맞춤법"
                        )
                        corrections.append(
                            {
                                "original": original_word,
                                "corrected": corrected_word,
                                "type": correction_type,
                            }
                        )
                    original_word = ""
                    corrected_word = ""

        if original_word or corrected_word:
            if original_word.strip() or corrected_word.strip():
                correction_type = (
                    "띄어쓰기"
                    if original_word.replace(" ", "") == corrected_word.replace(" ", "")
                    else "맞춤법"
                )
                corrections.append(
                    {
                        "original": original_word,
                        "corrected": corrected_word,
                        "type": correction_type,
                    }
                )

        return {**state, "corrections": corrections}