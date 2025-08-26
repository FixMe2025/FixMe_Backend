import re
from typing import Set


class KoreanValidator:
    """한국어 텍스트 검증을 담당하는 유틸리티 클래스"""
    
    @staticmethod
    def is_valid_korean_output(output: str, original: str) -> bool:
        """모델 출력이 유효한 한국어 교정문인지 검증"""
        if not output or not output.strip():
            return False
        
        # 길이 체크: 원본의 50%~150% 범위
        if len(output) < len(original) * 0.5 or len(output) > len(original) * 1.5:
            return False
        
        # 한국어 문자 비율 체크 (최소 70%)
        korean_chars = len(re.findall(r'[가-힣]', output))
        total_chars = len(re.sub(r'\s', '', output))
        if total_chars > 0 and korean_chars / total_chars < 0.7:
            return False
        
        # 이상한 문자 패턴 체크 (노이즈 감지)
        suspicious_patterns = [
            r'[^\s가-힣0-9a-zA-Z.,!?()[\]{}""''""\'\'·…-]',  # 허용된 문자 외
            r'[a-zA-Z]{10,}',  # 연속된 영문자 10자 이상
            r'[0-9]{10,}',     # 연속된 숫자 10자 이상
            r'[.,!?]{3,}',     # 구두점 3개 이상 연속
            r'같은말같은말같은말',  # 명백한 반복
        ]
        
        for pattern in suspicious_patterns:
            if re.search(pattern, output):
                return False
        
        # 원본과 완전히 다른 내용인지 체크 (최소 30% 유사도)
        common_chars: Set[str] = set(original.replace(' ', '')) & set(output.replace(' ', ''))
        original_chars: Set[str] = set(original.replace(' ', ''))
        if len(common_chars) < len(original_chars) * 0.3:
            return False
        
        return True