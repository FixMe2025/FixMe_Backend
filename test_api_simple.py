#!/usr/bin/env python3
"""
간단한 API 연결 테스트
"""

import requests
import json

def test_api_connection():
    """API 연결 테스트"""
    base_url = "http://localhost:8000"
    
    print("=== API 연결 테스트 ===")
    
    # 1. Health check
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        print(f"Health Check: {response.status_code}")
        print(f"Response: {response.json()}")
    except Exception as e:
        print(f"Health Check 실패: {str(e)}")
        return False
    
    # 2. 종합 교정 API 테스트 (간단한 요청)
    test_data = {
        "text": "안녕하세요. 테스트입니다.",
        "target_style": "공손함"
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/v1/comprehensive/comprehensive",
            json=test_data,
            timeout=10
        )
        print(f"\n종합 교정 API: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"원문: {result.get('original_text', 'N/A')}")
            print(f"교정: {result.get('corrected_text', 'N/A')}")
            print(f"문체변환: {result.get('styled_text', 'N/A')}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"종합 교정 API 실패: {str(e)}")
    
    # 3. 스타일 목록 API 테스트
    try:
        response = requests.get(f"{base_url}/api/v1/comprehensive/styles", timeout=5)
        print(f"\n스타일 목록 API: {response.status_code}")
        if response.status_code == 200:
            styles = response.json()
            print(f"사용 가능한 스타일: {len(styles)}개")
            for style in styles[:2]:  # 처음 2개만 출력
                print(f"- {style['name']}: {style['description']}")
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"스타일 목록 API 실패: {str(e)}")

if __name__ == "__main__":
    print("API 연결 테스트 시작...")
    test_api_connection()
    print("테스트 완료!")