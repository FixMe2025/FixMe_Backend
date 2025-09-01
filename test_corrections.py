#!/usr/bin/env python3
"""
한국어 맞춤법 교정 기능 테스트 스크립트
개선된 교정 규칙과 텍스트 분할 로직을 테스트합니다.
"""

import sys
import os

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, os.path.dirname(__file__))

from app.utils.correction_rules import CorrectionRules
from app.utils.text_processor import TextProcessor


def test_correction_rules():
    """교정 규칙 테스트"""
    print("=== 교정 규칙 테스트 ===")
    
    test_cases = [
        ("여기애 한국어문장을 임력하세요", "여기에 한국어문장을 입력하세요"),
        ("임력 후에 결과를 확인하세요", "입력 후에 결과를 확인하세요"),
        ("거기애 있는 파일을 체크해주세요", "거기에 있는 파일을 확인해주세요"),
        ("안뇽하세요 반갑습니다", "안녕하세요 반갑습니다"),
        ("재대로 된서 좋습니다", "제대로 돼서 좋습니다"),
    ]
    
    for i, (input_text, expected) in enumerate(test_cases, 1):
        result = CorrectionRules.apply_comprehensive_corrections(input_text)
        status = "PASS" if result == expected else "FAIL"
        print(f"테스트 {i}: {status}")
        print(f"  입력: {input_text}")
        print(f"  예상: {expected}")
        print(f"  실제: {result}")
        if result != expected:
            print(f"  차이: 예상과 다름")
        print()


def test_text_splitting():
    """텍스트 분할 테스트"""
    print("=== 텍스트 분할 테스트 ===")
    
    # 300자가 넘는 긴 텍스트 테스트
    long_text = (
        "여기애 한국어문장을 임력하세요. 이 시스템은 한국어 맞춤법과 띄어쓰기를 교정해주는 도구입니다. "
        "사용자가 텍스트를 입력하면 자동으로 오타와 맞춤법 오류를 찾아서 수정해줍니다. "
        "또한 띄어쓰기 규칙도 적용하여 더 자연스러운 문장으로 만들어줍니다. "
        "이러한 기능들은 AI 모델과 규칙 기반 시스템을 결합하여 구현되었습니다. "
        "사용자는 최대 2000자까지의 긴 텍스트도 교정할 수 있으며, "
        "시스템이 자동으로 문맥을 보존하면서 적절한 크기로 분할하여 처리합니다."
    )
    
    print(f"원본 텍스트 길이: {len(long_text)}자")
    print(f"원본 텍스트: {long_text[:100]}...")
    print()
    
    chunks = TextProcessor.smart_split_text(long_text)
    print(f"분할된 청크 수: {len(chunks)}")
    
    for i, chunk in enumerate(chunks, 1):
        print(f"청크 {i} ({len(chunk)}자): {chunk[:50]}...")
    print()
    
    # 재조합 테스트
    rejoined = TextProcessor.rejoin_chunks(chunks)
    print(f"재조합된 텍스트 길이: {len(rejoined)}자")
    print(f"재조합된 텍스트: {rejoined[:100]}...")
    print()
    
    # 원본과 재조합된 텍스트 비교
    if long_text.replace(' ', '') == rejoined.replace(' ', ''):
        print("PASS 재조합 성공: 내용이 보존되었습니다")
    else:
        print("FAIL 재조합 실패: 내용이 변경되었습니다")
        print("원본과 재조합 텍스트가 다릅니다")


def test_end_to_end():
    """통합 테스트 (교정 규칙 + 텍스트 분할)"""
    print("=== 통합 테스트 ===")
    
    test_text = (
        "여기애 한국어 맞춤밥 검사 시스템을 임력해보세요. "
        "이 도구는 사용자가 임력한 텍스트에서 맞춤법 오류를 찾아서 교정해줍니다. "
        "또한 뛰어쓰기 규칙도 적용하여 더 자연스러운 문장으로 만들어줍니다."
    )
    
    print(f"원본: {test_text}")
    print()
    
    # 1단계: 텍스트 분할
    chunks = TextProcessor.smart_split_text(test_text)
    print(f"분할된 청크 수: {len(chunks)}")
    
    # 2단계: 각 청크에 교정 규칙 적용
    corrected_chunks = []
    for i, chunk in enumerate(chunks, 1):
        corrected = CorrectionRules.apply_comprehensive_corrections(chunk)
        corrected_chunks.append(corrected)
        print(f"청크 {i} 교정:")
        print(f"  원본: {chunk}")
        print(f"  교정: {corrected}")
    
    print()
    
    # 3단계: 재조합
    final_result = TextProcessor.rejoin_chunks(corrected_chunks)
    print(f"최종 결과: {final_result}")
    
    # 기대하는 교정 사항들이 적용되었는지 확인
    expected_corrections = [
        ("여기애", "여기에"),
        ("맞춤밥", "맞춤법"), 
        ("임력", "입력"),
        ("뛰어쓰기", "띄어쓰기")
    ]
    
    print("\n교정 확인:")
    for wrong, correct in expected_corrections:
        if wrong not in final_result and correct in final_result:
            print(f"PASS {wrong} -> {correct} 교정됨")
        else:
            print(f"FAIL {wrong} -> {correct} 교정 안됨")


if __name__ == "__main__":
    print("한국어 맞춤법 교정 시스템 테스트")
    print("=" * 50)
    print()
    
    test_correction_rules()
    print()
    
    test_text_splitting()
    print()
    
    test_end_to_end()
    
    print("\n테스트 완료!")