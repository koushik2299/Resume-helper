"""Utilities for analyzing job descriptions and extracting keywords."""

import re
from typing import List, Dict
from collections import Counter


# Common stop words to filter out
STOP_WORDS = {
    'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
    'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'be',
    'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
    'would', 'should', 'could', 'may', 'might', 'must', 'can', 'this',
    'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they',
    'what', 'which', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
    'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such', 'no',
    'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'our',
    'your', 'their'
}


def extract_keywords(job_description: str, top_n: int = 8) -> List[str]:
    """
    Extract top keywords from a job description.
    
    Args:
        job_description: Full job description text
        top_n: Number of top keywords to return
        
    Returns:
        List of top N keywords/phrases
    """
    # Tokenize and clean
    words = tokenize_text(job_description)
    
    # Count frequency
    word_counts = Counter(words)
    
    # Get top keywords
    top_keywords = [word for word, count in word_counts.most_common(top_n)]
    
    return top_keywords


def tokenize_text(text: str) -> List[str]:
    """
    Tokenize text into words, filtering stop words and cleaning.
    
    Args:
        text: Input text
        
    Returns:
        List of cleaned tokens
    """
    # Convert to lowercase
    text = text.lower()
    
    # Extract words (alphanumeric + hyphens for compound words)
    words = re.findall(r'\b[a-z0-9]+(?:-[a-z0-9]+)*\b', text)
    
    # Filter stop words and short words
    filtered_words = [
        word for word in words 
        if word not in STOP_WORDS and len(word) > 2
    ]
    
    return filtered_words


def extract_phrases(text: str, max_words: int = 3) -> List[str]:
    """
    Extract common phrases (n-grams) from text.
    
    Args:
        text: Input text
        max_words: Maximum words per phrase
        
    Returns:
        List of common phrases
    """
    # Tokenize
    words = tokenize_text(text)
    
    phrases = []
    
    # Extract 2-word and 3-word phrases
    for n in range(2, max_words + 1):
        for i in range(len(words) - n + 1):
            phrase = ' '.join(words[i:i+n])
            phrases.append(phrase)
    
    # Count and return most common
    phrase_counts = Counter(phrases)
    common_phrases = [phrase for phrase, count in phrase_counts.most_common(10) if count > 1]
    
    return common_phrases


def count_keyword_matches(text: str, keywords: List[str]) -> int:
    """
    Count how many keywords from the list appear in the text.
    
    Args:
        text: Text to search in
        keywords: List of keywords to search for
        
    Returns:
        Number of keywords found
    """
    text_lower = text.lower()
    matches = 0
    
    for keyword in keywords:
        if keyword.lower() in text_lower:
            matches += 1
    
    return matches


def get_matched_keywords(text: str, keywords: List[str]) -> List[str]:
    """
    Get list of keywords that appear in the text.
    
    Args:
        text: Text to search in
        keywords: List of keywords to search for
        
    Returns:
        List of keywords that were found
    """
    text_lower = text.lower()
    matched = []
    
    for keyword in keywords:
        if keyword.lower() in text_lower:
            matched.append(keyword)
    
    return matched
