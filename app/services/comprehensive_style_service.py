"""
종합 교정 서비스 - 문체 변환 및 고급 교정
맞춤법 교정을 넘어서 문체를 다양한 톤으로 변환하는 서비스
"""

from typing import Dict, List, Optional
from .advanced_spellcheck_service import advanced_spellcheck_service
from app.utils.style_utils import StyleTone, StyleTransformer


class ComprehensiveStyleService:
    """종합 교정 서비스 - 맞춤법 교정 + 문체 변환"""
    
    def __init__(self):
        self.spellcheck_service = advanced_spellcheck_service
        self.style_transformer = StyleTransformer()
    
    def comprehensive_correction(self, text: str, target_style: Optional[str] = None) -> Dict:
        """종합 교정 실행: 맞춤법 교정 + 문체 변환"""
        try:
            # 1단계: 기본 맞춤법 교정
            spellcheck_result = self.spellcheck_service.correct_text(text)
            
            if 'error' in spellcheck_result:
                return {
                    'error': f'맞춤법 교정 실패: {spellcheck_result["error"]}'
                }
            
            corrected_text = spellcheck_result['corrected_text']
            spellcheck_corrections = spellcheck_result.get('corrections', [])
            
            # 2단계: 문체 변환
            if target_style:
                # 특정 문체로 변환
                try:
                    target_tone = None
                    for tone in StyleTone:
                        if tone.value == target_style:
                            target_tone = tone
                            break
                    
                    if target_tone:
                        styled_text = self.style_transformer.transform_style(corrected_text, target_tone)
                        
                        return {
                            'original_text': text,
                            'corrected_text': corrected_text,
                            'styled_text': styled_text,
                            'target_style': target_style,
                            'spellcheck_corrections': spellcheck_corrections,
                            'style_applied': True,
                            'improvements_made': self._get_style_improvements(corrected_text, styled_text)
                        }
                    else:
                        return {
                            'error': f'지원하지 않는 문체입니다: {target_style}'
                        }
                        
                except Exception as e:
                    return {
                        'error': f'문체 변환 실패: {str(e)}'
                    }
            
            else:
                # 모든 문체 옵션 제공
                style_suggestions = self.style_transformer.get_style_suggestions(corrected_text)
                
                return {
                    'original_text': text,
                    'corrected_text': corrected_text,
                    'spellcheck_corrections': spellcheck_corrections,
                    'style_suggestions': style_suggestions,
                    'available_styles': [tone.value for tone in StyleTone],
                    'style_applied': False
                }
        
        except Exception as e:
            return {
                'error': f'종합 교정 처리 중 오류 발생: {str(e)}'
            }
    
    def _get_style_improvements(self, original: str, styled: str) -> List[Dict]:
        """문체 변환에서 개선된 부분들을 찾아서 반환"""
        improvements = []
        
        # 간단한 차이점 찾기 (실제로는 더 정교한 알고리즘 필요)
        original_words = original.split()
        styled_words = styled.split()
        
        if len(original_words) == len(styled_words):
            for i, (orig, styled_word) in enumerate(zip(original_words, styled_words)):
                if orig != styled_word:
                    improvements.append({
                        'original': orig,
                        'improved': styled_word,
                        'type': '문체 변환',
                        'position': i
                    })
        
        return improvements
    
    def get_available_styles(self) -> List[Dict]:
        """사용 가능한 문체 목록과 설명 반환"""
        styles = []
        
        style_descriptions = {
            StyleTone.POLITE: "정중하고 예의바른 존댓말로 변환합니다. 고객 응대나 공식적인 상황에 적합합니다.",
            StyleTone.FRIENDLY: "친근하고 편안한 문체로 변환합니다. 동료나 친구와의 대화에 적합합니다.",
            StyleTone.BUSINESS: "업무용 격식 있는 문체로 변환합니다. 상사 보고나 공식 문서에 적합합니다.",
            StyleTone.CASUAL: "편안한 일상 대화체로 변환합니다. 가족이나 친한 사람과의 대화에 적합합니다.",
            StyleTone.FORMAL: "공식적이고 격식 있는 문체로 변환합니다. 공문서나 학술 문서에 적합합니다."
        }
        
        for tone in StyleTone:
            styles.append({
                'name': tone.value,
                'description': style_descriptions.get(tone, "문체 변환을 수행합니다."),
                'example_transforms': self._get_example_transforms(tone)
            })
        
        return styles
    
    def _get_example_transforms(self, tone: StyleTone) -> List[Dict]:
        """각 문체의 변환 예시를 반환"""
        examples = []
        
        # 각 문체별 대표적인 변환 예시들
        tone_examples = {
            StyleTone.POLITE: [
                {'before': '해', 'after': '해요'},
                {'before': '좋아', 'after': '좋습니다'},
                {'before': '고마워', 'after': '감사합니다'}
            ],
            StyleTone.FRIENDLY: [
                {'before': '합니다', 'after': '해요'},
                {'before': '감사합니다', 'after': '고마워요'},
                {'before': '죄송합니다', 'after': '미안해요'}
            ],
            StyleTone.BUSINESS: [
                {'before': '할게요', 'after': '하겠습니다'},
                {'before': '고마워요', 'after': '감사드립니다'},
                {'before': '확인', 'after': '확인하여'}
            ],
            StyleTone.CASUAL: [
                {'before': '합니다', 'after': '해'},
                {'before': '좋습니다', 'after': '좋아'},
                {'before': '하겠습니다', 'after': '할게'}
            ],
            StyleTone.FORMAL: [
                {'before': '해요', 'after': '합니다'},
                {'before': '고마워요', 'after': '감사드립니다'},
                {'before': '할게요', 'after': '하겠습니다'}
            ]
        }
        
        return tone_examples.get(tone, [])


# 싱글톤 인스턴스
comprehensive_style_service = ComprehensiveStyleService()