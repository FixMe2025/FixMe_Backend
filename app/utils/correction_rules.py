import re
from typing import Dict, List, Union


class CorrectionRules:
    """한국어 맞춤법 및 띄어쓰기 교정 규칙을 관리하는 클래스"""
    
    # 한국어 맞춤법 및 띄어쓰기 교정 사전
    COMPREHENSIVE_CORRECTIONS: Dict[str, Union[str, List[str]]] = {
        # 맞춤법 교정 (우선 적용)
        '재대로': '제대로',
        '지연되서': '지연돼서',
        '되서': '돼서',  
        '되요': '돼요',
        '됬': '됐',
        
        # 과거완료형 → 단순과거형 교정
        '했었는데': '했는데',
        '했었다': '했다',
        '했었던': '했던',
        '갔었는데': '갔는데', 
        '갔었다': '갔다',
        '갔었던': '갔던',
        '왔었는데': '왔는데',
        '왔었다': '왔다', 
        '왔었던': '왔던',
        '봤었는데': '봤는데',
        '봤었다': '봤다',
        '봤었던': '봤던',
        '도착했었다': '도착했다',
        '준비했었던': '준비했던',
        
        # 숫자 띄어쓰기
        '한시간': '한 시간',
        '두시간': '두 시간', 
        '세시간': '세 시간',
        '한달': '한 달',
        '두달': '두 달',
        '일주일': '일 주일',
        
        # 자주 틀리는 표현들
        '못할까봐': '못할까 봐',
        '좀더': '좀 더',
        '더욱더': '더욱',
        '그리고또': '그리고 또',
        '그런데또': '그런데 또',
        '하지만또': '하지만 또',
        '또한또': '또한',
    }
    
    # 기본 띄어쓰기 패턴들
    SPACING_PATTERNS = [
        # 부사 + 동사는 띄어쓰기 (우선 적용)
        (r'많이와서', '많이 와서'),  # "많이와서" → "많이 와서"
        (r'빨리와서', '빨리 와서'),
        (r'천천히가서', '천천히 가서'),
        (r'조용히해서', '조용히 해서'),
        
        # 잘못된 띄어쓰기 수정
        (r'회사 에서', '회사에서'),  # "회사 에서" → "회사에서"
        (r'한 시간 이나', '한 시간이나'),  # "한 시간 이나" → "한 시간이나"
        
        # 숫자 + 단위 (이미 분리된 것은 그대로)
        (r'([0-9]+|한|두|세|네|다섯|여섯|일곱|여덟|아홉|열)시간이나', r'\1 시간이나'),
        (r'([0-9]+|한|두|세|네|다섯|여섯|일곱|여덟|아홉|열)달동안', r'\1 달 동안'),
        (r'([0-9]+|한|두|세|네|다섯|여섯|일곱|여덟|아홉|열)주일전', r'\1 주일 전'),
    ]
    
    @classmethod
    def apply_comprehensive_corrections(cls, text: str) -> str:
        """포괄적인 사전 기반 교정"""
        corrected = text
        
        # 1. 먼저 사전 기반 교정 적용 (맞춤법 우선)
        for wrong_form, correct_form in cls.COMPREHENSIVE_CORRECTIONS.items():
            corrected = corrected.replace(wrong_form, correct_form)
        
        # 2. 그 다음 패턴 기반 띄어쓰기 적용
        for pattern, replacement in cls.SPACING_PATTERNS:
            corrected = re.sub(pattern, replacement, corrected)
        
        return corrected