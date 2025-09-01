#!/usr/bin/env python3
"""
실제 모델을 사용한 긴 한국어 텍스트 교정 테스트
AdvancedSpellCheckService의 complete workflow 테스트
"""

import sys
import os
import json

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, os.path.dirname(__file__))

from app.services.advanced_spellcheck_service import advanced_spellcheck_service


def test_model_based_correction():
    """실제 모델을 사용한 긴 텍스트 교정 테스트"""
    print("=== 실제 모델 기반 긴 텍스트 교정 테스트 ===")
    
    # 모델 로드 확인
    if not advanced_spellcheck_service.is_model_loaded():
        print("FAIL 모델이 로드되지 않았습니다. 서버를 먼저 시작해주세요.")
        return []
    
    print(f"PASS 모델 로드됨 (디바이스: {advanced_spellcheck_service.get_device_info()})")
    print()
    
    # 테스트 케이스 1: 일반적인 오타가 많은 텍스트 (약 500자)
    test_case_1 = (
        "여기애 한국어 맞춤밥 검사 시스템을 임력해보세요. 이 도구는 사용자가 임력한 텍스트에서 "
        "오타와 맞춤법 오류를 찾아서 교정해줍니다. 또한 뛰어쓰기 규칙도 적용하여 더 자연스러운 "
        "문장으로 만들어줍니다. 거기애 있는 기능들은 AI 모델과 규칙 기반 시스템을 결합하여 "
        "구현되었습니다. 사용자는 최대 이천자까지의 긴 텍스트도 교정할 수 있으며, 시스템이 "
        "자동으로 문맥을 보존하면서 적절한 크기로 분할하여 처리합니다. 안뇽하세요 라고 인사하면 "
        "안녕하세요 로 교정됩니다. 재대로 된서 좋은 결과를 얻을 수 있을 것입니다."
    )
    
    # 테스트 케이스 2: 복잡한 문장 구조와 다양한 오류 (약 800자)
    test_case_2 = (
        "현재 개발중인 이 프로그램은 사용자들이 임력하는 한국어 문장들을 분석하고 교정하는 "
        "시스템입니다. 여러가지 종류의 오류들을 처리할 수 있는데, 예를 들어 맞춤밥 오류나 "
        "뛰어쓰기 문제들을 해결할 수 있습니다. 거기애 추가로 문법적 오류도 어느정도 교정이 "
        "가능합니다. 이 시스템의 핵심 기술은 자연어 처리 기술과 머신러닝 알고리즘을 결합한 "
        "것입니다. 사용자가 긴 문장을 임력하면, 시스템은 먼저 텍스트를 적절한 크기의 청크들로 "
        "분할합니다. 그 다음에 각 청크마다 교정 작업을 수행하고, 마지막에 모든 청크들을 "
        "다시 하나의 완전한 텍스트로 재조합합니다. 이런 방식으로 처리하면 긴 텍스트도 "
        "효율적으로 처리할 수 있습니다. 또한 문맥정보도 최대한 보존할 수 있어서 자연스러운 "
        "결과를 얻을 수 있습니다. 안뇽하세요 같은 인사말도 안녕하세요 로 정확히 교정됩니다."
    )
    
    # 테스트 케이스 3: 매우 긴 텍스트 (약 1200자)
    test_case_3 = (
        "한국어는 세계에서 가장 과학적이고 체계적인 문자 체계를 가진 언어 중 하나입니다. "
        "하지만 맞춤밥이나 뛰어쓰기 규칙들이 복잡해서 많은 사람들이 어려워합니다. "
        "특히 외국인들이나 어린 학생들에게는 더욱 어려운 문제입니다. 여기애 개발된 "
        "시스템은 이런 문제들을 해결하기 위해 만들어졌습니다. 사용자가 임력한 텍스트를 "
        "자동으로 분석하고 교정해주는 기능을 제공합니다. 이 시스템의 가장 큰 장점은 "
        "단순히 틀린 부분만 고치는 것이 아니라, 전체적인 문맥을 이해하고 자연스러운 "
        "문장으로 만들어준다는 것입니다. 거기애 더해서 사용자가 왜 그 부분이 틀렸는지 "
        "설명도 제공합니다. 예를 들어 안뇽하세요 를 안녕하세요 로 교정할 때, 단순히 "
        "고치는 것만이 아니라 왜 그렇게 써야 하는지 이유도 알려줍니다. 또한 재대로 된서 "
        "같은 복합적인 오류도 제대로 돼서 로 정확하게 교정합니다. 이런 기능들이 모두 "
        "합쳐져서 사용자들이 한국어를 더 정확하고 자연스럽게 사용할 수 있도록 도와줍니다. "
        "앞으로도 계속해서 더 많은 기능들을 추가하고 성능을 향상시켜 나갈 계획입니다. "
        "궁극적으로는 모든 한국어 사용자들이 올바르고 아름다운 한국어를 사용할 수 있도록 "
        "지원하는 것이 목표입니다."
    )
    
    test_cases = [
        ("테스트 1 (약 500자)", test_case_1),
        ("테스트 2 (약 800자)", test_case_2), 
        ("테스트 3 (약 1200자)", test_case_3)
    ]
    
    results = []
    
    for test_name, original_text in test_cases:
        print(f"\n{test_name}")
        print(f"원문 길이: {len(original_text)}자")
        print(f"원문: {original_text[:100]}...")
        print()
        
        try:
            # LangGraph workflow를 통한 전체 교정 프로세스 실행
            result = advanced_spellcheck_service.correct_text(original_text)
            
            if 'error' in result:
                print(f"FAIL 교정 실패: {result['error']}")
                results.append({
                    'test_name': test_name,
                    'original_length': len(original_text),
                    'original_text': original_text,
                    'error': result['error'],
                    'success': False
                })
                continue
            
            corrected_text = result['corrected_text']
            corrections = result.get('corrections', [])
            suggestions = result.get('suggestions', [])
            
            print(f"PASS 교정 성공")
            print(f"교정 결과 길이: {len(corrected_text)}자")
            print(f"교정 결과: {corrected_text[:100]}...")
            print(f"발견된 교정 사항: {len(corrections)}건")
            print(f"제안 사항: {len(suggestions)}건")
            print()
            
            # 교정 사항 출력
            if corrections:
                print("주요 교정 사항:")
                for i, correction in enumerate(corrections[:10], 1):  # 최대 10개만 표시
                    print(f"  {i}. '{correction.get('original', '')}' -> '{correction.get('corrected', '')}' ({correction.get('type', 'Unknown')})")
                if len(corrections) > 10:
                    print(f"  ... 및 {len(corrections)-10}건 더")
                print()
            
            # 기대하는 교정 사항 확인
            expected_corrections = [
                ("여기애", "여기에"),
                ("임력", "입력"),
                ("맞춤밥", "맞춤법"),
                ("뛰어쓰기", "띄어쓰기"),
                ("거기애", "거기에"),
                ("안뇽하세요", "안녕하세요"),
                ("재대로", "제대로"),
                ("된서", "돼서")
            ]
            
            correction_status = []
            for wrong, correct in expected_corrections:
                if wrong in original_text:
                    if wrong not in corrected_text and correct in corrected_text:
                        correction_status.append(f"PASS {wrong} -> {correct} (교정됨)")
                    else:
                        correction_status.append(f"FAIL {wrong} -> {correct} (교정 안됨)")
            
            if correction_status:
                print("핵심 교정 확인:")
                for status in correction_status:
                    print(f"  {status}")
                print()
            
            results.append({
                'test_name': test_name,
                'original_length': len(original_text),
                'result_length': len(corrected_text),
                'corrections_count': len(corrections),
                'suggestions_count': len(suggestions),
                'correction_status': correction_status,
                'original_text': original_text,
                'corrected_text': corrected_text,
                'corrections': corrections,
                'suggestions': suggestions,
                'success': True
            })
            
        except Exception as e:
            print(f"FAIL 예외 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append({
                'test_name': test_name,
                'original_length': len(original_text),
                'original_text': original_text,
                'error': str(e),
                'success': False
            })
    
    return results


if __name__ == "__main__":
    print("한국어 맞춤법 교정 시스템 - 실제 모델 테스트")
    print("=" * 60)
    
    results = test_model_based_correction()
    
    print("\n" + "=" * 60)
    print("테스트 결과 요약:")
    for result in results:
        status = "PASS 성공" if result['success'] else "FAIL 실패"
        print(f"\n{result['test_name']}: {status}")
        if result['success']:
            print(f"  원문: {result['original_length']}자 -> 교정문: {result['result_length']}자")
            print(f"  교정 사항: {result['corrections_count']}건")
            print(f"  제안 사항: {result['suggestions_count']}건")
            
            # 핵심 교정 성공률 계산
            correction_statuses = result.get('correction_status', [])
            if correction_statuses:
                success_count = len([s for s in correction_statuses if 'PASS' in s])
                total_count = len(correction_statuses)
                success_rate = (success_count / total_count * 100) if total_count > 0 else 0
                print(f"  핵심 교정 성공률: {success_count}/{total_count} ({success_rate:.1f}%)")
        else:
            print(f"  에러: {result.get('error', '알 수 없는 오류')}")
    
    # 결과를 JSON으로 저장
    with open('model_test_results.json', 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n상세 결과가 model_test_results.json에 저장되었습니다.")