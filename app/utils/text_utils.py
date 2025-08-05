import re
from typing import List, Tuple


def clean_text(text: str) -> str:
    text = text.strip()
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s가-힣]', '', text)
    return text


def split_sentences(text: str) -> List[str]:
    sentences = re.split(r'[.!?]+', text)
    return [s.strip() for s in sentences if s.strip()]


def calculate_text_similarity(text1: str, text2: str) -> float:
    words1 = set(text1.split())
    words2 = set(text2.split())
    
    if not words1 and not words2:
        return 1.0
    if not words1 or not words2:
        return 0.0
    
    intersection = words1.intersection(words2)
    union = words1.union(words2)
    
    return len(intersection) / len(union)


def highlight_differences(original: str, corrected: str) -> List[Tuple[str, str, int, int]]:
    differences = []
    
    original_words = original.split()
    corrected_words = corrected.split()
    
    i = j = 0
    pos = 0
    
    while i < len(original_words) and j < len(corrected_words):
        if original_words[i] != corrected_words[j]:
            start_pos = pos
            end_pos = pos + len(original_words[i])
            differences.append((
                original_words[i],
                corrected_words[j],
                start_pos,
                end_pos
            ))
        
        pos += len(original_words[i]) + 1
        i += 1
        j += 1
    
    return differences