from typing import List, Dict, Tuple, Optional
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from app.models.spellcheck import Correction
from app.services.model_service import spell_check_service
from app.services.improvement_service import improvement_service
from app.services.typo_corrector_service import typo_corrector_service

logger = logging.getLogger(__name__)

class IntegratedCorrectionService:
    """
    theSOL1/kogrammar-base와 j5ng/et5-typos-corrector를 통합한 
    맞춤법 교정 및 문장 개선 서비스
    """
    
    def __init__(self):
        self.primary_service = spell_check_service
        self.improvement_service = improvement_service
        self.typo_service = typo_corrector_service

    def comprehensive_check(self, text: str, include_improvement: bool = True, 
                          style: str = "formal") -> Dict:
        """
        종합적인 텍스트 검사 및 개선
        
        Args:
            text: 검사할 텍스트
            include_improvement: 문장 개선 추천 포함 여부
            style: 개선 스타일 (formal, casual, academic, business)
            
        Returns:
            Dict: 교정 결과 및 개선 추천
        """
        try:
            result = {
                "original_text": text,
                "corrected_text": text,
                "corrections": [],
                "improvements": None,
                "status": "success"
            }
            
            # 병렬로 맞춤법 검사 수행
            futures = []
            with ThreadPoolExecutor(max_workers=2) as executor:
                # 주요 모델로 맞춤법 검사
                future1 = executor.submit(self._safe_spell_check, text)
                futures.append(("primary", future1))
                
                # 보조 모델로 타이포 검사 (모델이 로드되어 있는 경우만)
                if self.typo_service.model is not None:
                    future2 = executor.submit(self._safe_typo_check, text)
                    futures.append(("typo", future2))
                
                # 결과 수집
                spell_results = {}
                for service_name, future in futures:
                    try:
                        corrected_text, corrections = future.result(timeout=30)
                        spell_results[service_name] = (corrected_text, corrections)
                    except Exception as e:
                        logger.error(f"Error in {service_name} service: {e}")
                        spell_results[service_name] = (text, [])
            
            # 결과 통합
            if "primary" in spell_results:
                result["corrected_text"], result["corrections"] = spell_results["primary"]
            
            # 보조 모델 결과가 있으면 추가 정보로 활용
            if "typo" in spell_results:
                typo_text, typo_corrections = spell_results["typo"]
                # 보조 모델의 추가 교정사항이 있으면 추가
                for correction in typo_corrections:
                    if correction not in result["corrections"]:
                        correction.type = f"{correction.type} (보조)"
                        result["corrections"].append(correction)
            
            # 문장 개선 추천
            if include_improvement:
                try:
                    # 교정된 텍스트를 기반으로 개선 추천
                    improvement_result = self.improvement_service.improve_text(
                        result["corrected_text"], style
                    )
                    result["improvements"] = improvement_result
                except Exception as e:
                    logger.error(f"Error in improvement service: {e}")
                    result["improvements"] = {
                        "error": str(e),
                        "original_text": result["corrected_text"],
                        "improved_text": result["corrected_text"],
                        "suggestions": []
                    }
            
            return result
            
        except Exception as e:
            logger.error(f"Error in comprehensive check: {e}")
            return {
                "original_text": text,
                "corrected_text": text,
                "corrections": [],
                "improvements": None,
                "status": "error",
                "error": str(e)
            }

    def _safe_spell_check(self, text: str) -> Tuple[str, List[Correction]]:
        """안전한 맞춤법 검사"""
        try:
            return self.primary_service.check_spelling(text)
        except Exception as e:
            logger.error(f"Primary spell check failed: {e}")
            return text, []

    def _safe_typo_check(self, text: str) -> Tuple[str, List[Correction]]:
        """안전한 타이포 검사"""
        try:
            return self.typo_service.correct_typos(text)
        except Exception as e:
            logger.error(f"Typo check failed: {e}")
            return text, []

    def quick_spell_check(self, text: str) -> Dict:
        """빠른 맞춤법 검사 (주요 모델만 사용)"""
        try:
            corrected_text, corrections = self.primary_service.check_spelling(text)
            return {
                "original_text": text,
                "corrected_text": corrected_text,
                "corrections": [correction.dict() for correction in corrections],
                "status": "success"
            }
        except Exception as e:
            logger.error(f"Error in quick spell check: {e}")
            return {
                "original_text": text,
                "corrected_text": text,
                "corrections": [],
                "status": "error",
                "error": str(e)
            }

    def quick_improvement(self, text: str, style: str = "formal") -> Dict:
        """빠른 문장 개선"""
        try:
            return self.improvement_service.improve_text(text, style)
        except Exception as e:
            logger.error(f"Error in quick improvement: {e}")
            return {
                "original_text": text,
                "improved_text": text,
                "suggestions": [],
                "style_applied": style,
                "error": str(e)
            }

    def is_healthy(self) -> Dict[str, bool]:
        """모든 서비스의 상태 확인"""
        return {
            "primary_spell_check": self.primary_service.is_healthy(),
            "improvement_service": self.improvement_service.is_healthy(),
            "typo_corrector": self.typo_service.is_healthy()
        }

# 싱글톤 인스턴스
integrated_service = IntegratedCorrectionService()