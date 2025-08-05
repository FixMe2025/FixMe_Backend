from hanspell import spell_checker
from typing import List, Tuple
import logging

from app.models.spellcheck import Correction

logger = logging.getLogger(__name__)

class SpellCheckService:
    def check_spelling(self, text: str) -> Tuple[str, List[Correction]]:
        try:
            spelled_sent = spell_checker.check(text)

            corrected_text = spelled_sent.checked
            corrections = []
            for error in spelled_sent.errors:
                corrections.append(
                    Correction(
                        original=error.original,
                        corrected=error.words[0] if error.words else error.original, # 교정 단어가 없는 경우 원본 사용
                        type=error.msg
                    )
                )

            return corrected_text, corrections

        except Exception as e:
            logger.error(f"Error in spell checking with hanspell: {e}")
            raise

    def is_healthy(self) -> bool:
        # py-hanspell은 외부 API를 사용하므로, 간단한 테스트로 상태 확인
        try:
            spell_checker.check("안녕")
            return True
        except Exception:
            return False

# 싱글톤 인스턴스
spell_check_service = SpellCheckService()