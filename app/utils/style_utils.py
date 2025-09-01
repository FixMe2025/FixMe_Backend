import re
from enum import Enum
from typing import Dict

class StyleTone(Enum):
    """문체 톤 정의"""
    POLITE = "공손함"          # 정중하고 예의바른 문체
    FRIENDLY = "친근함"        # 친근하고 편안한 문체
    BUSINESS = "상사에게 보고용"  # 업무용, 격식 있는 문체
    CASUAL = "일상 대화체"      # 편안한 일상 대화체
    FORMAL = "격식 있는 문체"    # 공식적이고 격식 있는 문체


class StyleTransformer:
    """문체 변환 규칙을 관리하는 클래스"""
    
    # 문체별 변환 규칙
    STYLE_RULES = {
        StyleTone.POLITE: {
            # 존댓말 변환
            '해': '해요',
            '이다': '입니다',
            '있다': '있습니다',
            '없다': '없습니다',
            '한다': '합니다',
            '된다': '됩니다',
            '간다': '갑니다',
            '온다': '옵니다',
            '본다': '봅니다',
            '말하다': '말씀드리다',
            '주다': '드리다',
            '받다': '받습니다',
            '하겠다': '하겠습니다',
            '할게': '하겠습니다',
            '할거야': '할 예정입니다',
            '그래': '그렇습니다',
            '맞아': '맞습니다',
            '아니야': '아닙니다',
            '좋아': '좋습니다',
            '나쁘다': '좋지 않습니다',
            '싫다': '곤란합니다',
            '모르겠다': '잘 모르겠습니다',
            '고마워': '감사합니다',
            '미안해': '죄송합니다',
            '잠깐': '잠시만요',
            '괜찮아': '괜찮습니다',
        },
        
        StyleTone.FRIENDLY: {
            # 친근한 문체 변환
            '합니다': '해요',
            '입니다': '이에요',
            '습니다': '어요',
            '됩니다': '돼요',
            '갑니다': '가요',
            '옵니다': '와요',
            '봅니다': '봐요',
            '좋습니다': '좋아요',
            '아닙니다': '아니에요',
            '감사합니다': '고마워요',
            '죄송합니다': '미안해요',
            '괜찮습니다': '괜찮아요',
            '잠시만요': '잠깐만요',
            '말씀드리다': '말해요',
            '드리다': '줘요',
            '하겠습니다': '할게요',
            '예정입니다': '거예요',
            '곤란합니다': '어려워요',
        },
        
        StyleTone.BUSINESS: {
            # 업무용 격식 있는 문체
            '해요': '합니다',
            '이에요': '입니다',
            '돼요': '됩니다',
            '가요': '갑니다',
            '와요': '옵니다',
            '봐요': '봅니다',
            '좋아요': '좋습니다',
            '아니에요': '아닙니다',
            '고마워요': '감사드립니다',
            '미안해요': '죄송드립니다',
            '괜찮아요': '괜찮습니다',
            '할게요': '하겠습니다',
            '거예요': '예정입니다',
            '어려워요': '어렵습니다',
            '말해요': '말씀드리겠습니다',
            '줘요': '드리겠습니다',
            '생각해': '생각합니다',
            '보고': '보고드리며',
            '확인': '확인하여',
            '진행': '진행하겠습니다',
            '검토': '검토하겠습니다',
            '완료': '완료하였습니다',
            '시작': '시작하겠습니다',
            '계획': '계획입니다',
            '결과': '결과입니다',
            '문제': '문제사항입니다',
        },
        
        StyleTone.CASUAL: {
            # 편안한 일상 대화체
            '합니다': '해',
            '입니다': '야',
            '됩니다': '돼',
            '갑니다': '가',
            '옵니다': '와',
            '봅니다': '봐',
            '좋습니다': '좋아',
            '아닙니다': '아니야',
            '감사드립니다': '고마워',
            '죄송드립니다': '미안해',
            '괜찮습니다': '괜찮아',
            '하겠습니다': '할게',
            '예정입니다': '거야',
            '어렵습니다': '어려워',
            '말씀드리겠습니다': '말할게',
            '드리겠습니다': '줄게',
        },
        
        StyleTone.FORMAL: {
            # 공식적이고 격식 있는 문체
            '해요': '합니다',
            '이에요': '입니다',
            '돼요': '됩니다',
            '가요': '갑니다',
            '와요': '옵니다',
            '봐요': '봅니다',
            '좋아요': '좋습니다',
            '아니에요': '아닙니다',
            '고마워요': '감사드립니다',
            '미안해요': '사과드립니다',
            '괜찮아요': '괜찮습니다',
            '할게요': '하겠습니다',
            '거예요': '것입니다',
            '어려워요': '곤란합니다',
            '말해요': '말씀드립니다',
            '줘요': '제공해드립니다',
            '하자': '하겠습니다',
            '그래': '그렇습니다',
            '맞아': '정확합니다',
            '틀렸어': '잘못되었습니다',
        }
    }
    
    # 문장 연결어 개선
    CONJUNCTION_IMPROVEMENTS = {
        '그런데': '하지만',
        '근데': '그런데',
        '그래서': '따라서',
        '그러므로': '그러므로',
        '그리고': '또한',
        '또': '또한',
        '그냥': '',  # 불필요한 경우 제거
        '막': '',    # 불필요한 경우 제거
        '진짜': '정말',
        '완전': '매우',
        '엄청': '매우',
        '되게': '매우',
        '많이': '매우',
        '좀': '조금',
        '약간': '다소',
    }
    
    # 비속어나 부적절한 표현 순화
    REFINEMENT_RULES = {
        '짜증나': '불편하다',
        '짜증': '불편함',
        '빡쳐': '화가 난다',
        '열받아': '화가 난다',
        '답답해': '답답하다',
        '귀찮아': '번거롭다',
        '귀찮': '번거로움',
        '싫어': '좋지 않다',
        '무서워': '두렵다',
        '무섭': '두려움',
        '지겨워': '지루하다',
        '지겨움': '지루함',
        '힘들어': '어렵다',
        '힘듦': '어려움',
        '쉬워': '간단하다',
        '쉬움': '간단함',
    }

    @classmethod
    def transform_style(cls, text: str, target_tone: StyleTone) -> str:
        """지정된 톤으로 문체를 변환"""
        transformed_text = text
        
        # 1. 기본 문체 변환
        if target_tone in cls.STYLE_RULES:
            style_rules = cls.STYLE_RULES[target_tone]
            for original, replacement in style_rules.items():
                # 단어 경계를 고려한 정확한 치환
                pattern = r'\b' + re.escape(original) + r'\b'
                transformed_text = re.sub(pattern, replacement, transformed_text)
        
        # 2. 연결어 개선 (모든 톤에 공통 적용)
        for original, replacement in cls.CONJUNCTION_IMPROVEMENTS.items():
            if replacement:  # 빈 문자열이 아닌 경우만
                pattern = r'\b' + re.escape(original) + r'\b'
                transformed_text = re.sub(pattern, replacement, transformed_text)
            else:
                # 불필요한 단어 제거
                pattern = r'\b' + re.escape(original) + r'\s*'
                transformed_text = re.sub(pattern, '', transformed_text)
        
        # 3. 표현 순화 (정중한 톤과 업무용 톤에만 적용)
        if target_tone in [StyleTone.POLITE, StyleTone.BUSINESS, StyleTone.FORMAL]:
            for original, replacement in cls.REFINEMENT_RULES.items():
                pattern = r'\b' + re.escape(original) + r'\b'
                transformed_text = re.sub(pattern, replacement, transformed_text)
        
        # 4. 문장 정리 (중복 공백 제거, 문장부호 정리)
        transformed_text = re.sub(r'\s+', ' ', transformed_text)  # 중복 공백 제거
        transformed_text = re.sub(r'\s+([.!?,:;])', r'\1', transformed_text)  # 구두점 앞 공백 제거
        transformed_text = transformed_text.strip()
        
        return transformed_text

    @classmethod
    def get_style_suggestions(cls, text: str) -> Dict[str, str]:
        """모든 문체 톤으로 변환한 결과를 반환"""
        suggestions = {}
        
        for tone in StyleTone:
            transformed = cls.transform_style(text, tone)
            suggestions[tone.value] = transformed
        
        return suggestions