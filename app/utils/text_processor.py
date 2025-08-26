from typing import List
from ..config import settings


class TextProcessor:
    """텍스트 분할 및 병합 처리를 담당하는 유틸리티 클래스"""
    
    @staticmethod
    def smart_split_text(text: str) -> List[str]:
        """문맥을 보존하면서 텍스트를 스마트하게 분할합니다."""
        if len(text) <= settings.CHUNK_SIZE:
            return [text]
        
        chunks = []
        current_pos = 0
        
        while current_pos < len(text):
            # 청크 크기만큼 자르기
            end_pos = min(current_pos + settings.CHUNK_SIZE, len(text))
            chunk = text[current_pos:end_pos]
            
            # 마지막 청크가 아니라면 문장 경계에서 자르기
            if end_pos < len(text):
                # 문장 끝 기호에서 자르기 시도
                sentence_endings = ['다.', '요.', '죠.', '야.', '네.', '까.', '가.', '어.', '지.', '니.']
                best_cut = -1
                
                for ending in sentence_endings:
                    pos = chunk.rfind(ending)
                    if pos > settings.CHUNK_SIZE * 0.7:  # 청크의 70% 이상에서만
                        best_cut = max(best_cut, pos + len(ending))
                
                # 문장 끝을 못 찾으면 공백에서 자르기
                if best_cut == -1:
                    space_pos = chunk.rfind(' ')
                    if space_pos > settings.CHUNK_SIZE * 0.5:  # 청크의 50% 이상에서만
                        best_cut = space_pos
                
                # 적절한 자르는 위치를 찾았으면 적용
                if best_cut > 0:
                    chunk = chunk[:best_cut]
                    end_pos = current_pos + best_cut
            
            chunks.append(chunk.strip())
            current_pos = end_pos
            
            # 다음 청크 시작점에서 공백 제거
            while current_pos < len(text) and text[current_pos] == ' ':
                current_pos += 1
        
        return [chunk for chunk in chunks if chunk.strip()]

    @staticmethod
    def rejoin_chunks(chunks: List[str]) -> str:
        """청크들을 자연스럽게 재조합"""
        if not chunks:
            return ""
        
        if len(chunks) == 1:
            return chunks[0]
        
        # 청크들을 연결하면서 중복 공백 제거 및 자연스러운 연결
        result = chunks[0]
        
        for chunk in chunks[1:]:
            chunk = chunk.strip()
            if not chunk:
                continue
                
            # 이전 청크의 마지막 문자와 현재 청크의 첫 문자 확인
            if result and chunk:
                last_char = result[-1]
                first_char = chunk[0]
                
                # 문장 끝 기호 뒤에는 공백 추가
                if last_char in '.!?':
                    result += " " + chunk
                # 쉼표 뒤에는 공백 추가
                elif last_char == ',':
                    result += " " + chunk
                # 기본적으로는 공백으로 연결
                elif last_char != ' ' and first_char != ' ':
                    result += " " + chunk
                else:
                    result += chunk
            else:
                result += chunk
        
        # 최종 정리: 중복 공백 제거
        import re
        result = re.sub(r'\s+', ' ', result).strip()
        
        return result