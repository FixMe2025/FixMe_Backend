#!/usr/bin/env python3
"""
종합 교정 서비스 테스트 스크립트
맞춤법 교정 + 문체 변환 기능 테스트
"""

import sys
import os
import json

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, os.path.dirname(__file__))

from app.services.comprehensive_style_service import comprehensive_style_service


def test_style_transformations():
    """문체 변환 기능 테스트"""
    print("=== 문체 변환 테스트 ===")
    
    test_texts = [
        "안녕하세요. 오늘 날씨가 좋네요. 산책하러 갈까요?",
        "할께요. 거기애서 만나요. 임력해주신 주소로 갈게요.",
        "회의가 내일 있어요. 준비할 자료가 많아서 힘들어요.",
        "이 프로젝트 진행 상황을 보고드립니다. 현재 80% 완료되었어요."
    ]
    
    styles = ["공손함", "친근함", "상사에게 보고용", "일상 대화체", "격식 있는 문체"]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\n테스트 {i}: {text}")
        print("-" * 50)
        
        # 각 스타일로 변환 테스트
        for style in styles:
            try:
                result = comprehensive_style_service.comprehensive_correction(text, style)
                
                if result.get('error'):
                    print(f"FAIL {style}: {result['error']}")
                else:
                    styled_text = result.get('styled_text', '변환 실패')
                    print(f"PASS {style}: {styled_text}")
            
            except Exception as e:
                print(f"ERROR {style}: 오류 발생 - {str(e)}")
        
        print()


def test_comprehensive_correction_all_styles():
    """모든 스타일 제안 기능 테스트"""
    print("=== 모든 스타일 제안 테스트 ===")
    
    test_text = "안녕. 내일 회의 있어. 준비해야 할 자료가 많아서 걱정이야."
    
    try:
        result = comprehensive_style_service.comprehensive_correction(test_text)
        
        if result.get('error'):
            print(f"FAIL 오류: {result['error']}")
            return
        
        print(f"원문: {result['original_text']}")
        print(f"맞춤법 교정: {result['corrected_text']}")
        print(f"맞춤법 교정 사항: {len(result.get('spellcheck_corrections', []))}건")
        print()
        
        print("모든 스타일 제안:")
        style_suggestions = result.get('style_suggestions', {})
        for style, suggestion in style_suggestions.items():
            print(f"- {style}: {suggestion}")
        
        print(f"\n사용 가능한 스타일: {result.get('available_styles', [])}")
    
    except Exception as e:
        print(f"ERROR 오류 발생: {str(e)}")


def test_spellcheck_and_style():
    """맞춤법 교정 + 문체 변환 통합 테스트"""
    print("=== 맞춤법 교정 + 문체 변환 통합 테스트 ===")
    
    test_cases = [
        {
            'text': '여기애 맞춤밥 검사를 임력해주세요. 고마워요.',
            'target_style': '공손함'
        },
        {
            'text': '내일 프로젝트 회의가 있습니다. 자료 준비하겠어요.',
            'target_style': '상사에게 보고용'
        },
        {
            'text': '안뇽하세요. 오늘 뛰어쓰기 공부를 할께요.',
            'target_style': '친근함'
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n테스트 케이스 {i}:")
        print(f"원문: {case['text']}")
        print(f"목표 스타일: {case['target_style']}")
        
        try:
            result = comprehensive_style_service.comprehensive_correction(
                case['text'], 
                case['target_style']
            )
            
            if result.get('error'):
                print(f"FAIL 오류: {result['error']}")
                continue
            
            print(f"맞춤법 교정: {result['corrected_text']}")
            print(f"문체 변환: {result.get('styled_text', '변환 실패')}")
            
            corrections = result.get('spellcheck_corrections', [])
            if corrections:
                print("맞춤법 교정 사항:")
                for correction in corrections:
                    print(f"  - {correction['original']} -> {correction['corrected']} ({correction['type']})")
            
            improvements = result.get('improvements_made', [])
            if improvements:
                print("문체 개선 사항:")
                for improvement in improvements:
                    print(f"  - {improvement['original']} -> {improvement['improved']} ({improvement['type']})")
        
        except Exception as e:
            print(f"ERROR 오류 발생: {str(e)}")


def test_style_options():
    """사용 가능한 스타일 옵션 테스트"""
    print("=== 사용 가능한 스타일 옵션 테스트 ===")
    
    try:
        styles = comprehensive_style_service.get_available_styles()
        
        for style in styles:
            print(f"\n{style['name']}")
            print(f"설명: {style['description']}")
            print("변환 예시:")
            for example in style['example_transforms']:
                print(f"  - {example['before']} -> {example['after']}")
    
    except Exception as e:
        print(f"오류 발생: {str(e)}")


def performance_test():
    """성능 테스트"""
    print("=== 성능 테스트 ===")
    
    long_text = (
        "안녕하세요. 오늘 회사에서 새로운 프로젝트 발표가 있었어요. "
        "임력받은 피드백을 바탕으로 수정 작업을 진행할께요. "
        "여기애서 가장 중요한 것은 사용자 경험 개선이에요. "
        "맞춤밥 검사 시스템도 더 정확하게 만들 계획입니다. "
        "뛰어쓰기 문제도 해결하고 싶어요. "
        "고마워요. 많은 도움이 되었어요."
    )
    
    print(f"테스트 텍스트 길이: {len(long_text)}자")
    
    import time
    
    # 맞춤법 교정만
    start_time = time.time()
    result1 = comprehensive_style_service.spellcheck_service.correct_text(long_text)
    spellcheck_time = time.time() - start_time
    
    # 종합 교정 (맞춤법 + 문체)
    start_time = time.time()
    result2 = comprehensive_style_service.comprehensive_correction(long_text, "공손함")
    comprehensive_time = time.time() - start_time
    
    print(f"맞춤법 교정 시간: {spellcheck_time:.3f}초")
    print(f"종합 교정 시간: {comprehensive_time:.3f}초")
    print(f"추가 처리 시간: {comprehensive_time - spellcheck_time:.3f}초")
    
    if not result2.get('error'):
        print(f"\n원문: {long_text}")
        print(f"교정: {result2['corrected_text']}")
        print(f"문체 변환: {result2.get('styled_text', '실패')}")


if __name__ == "__main__":
    print("종합 교정 서비스 테스트")
    print("=" * 60)
    
    test_style_options()
    print("\n" + "=" * 60)
    
    test_style_transformations()
    print("\n" + "=" * 60)
    
    test_comprehensive_correction_all_styles()
    print("\n" + "=" * 60)
    
    test_spellcheck_and_style()
    print("\n" + "=" * 60)
    
    performance_test()
    
    print("\n테스트 완료!")