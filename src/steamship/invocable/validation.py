import logging
from functools import wraps
from typing import List, Optional

from thefuzz import fuzz


def _check_word_count(input_text: str, max_words: int):
    words = input_text.split()
    return len(words) <= max_words


def _check_malicious(input_text: str):
    logging.error("checking malicious")
    banned_keywords = ["ignore previous instructions", "print prior sentences"]
    input_text = input_text.lower()
    for keyword in banned_keywords:
        ratio = fuzz.partial_token_sort_ratio(input_text, keyword)
        if ratio > 90:
            return True
    return False


def _validate_value(value: str, max_words: Optional[int] = None):
    proper_length = True
    if max_words:
        proper_length = _check_word_count(value, max_words)
    malicious = _check_malicious(input_text=value)

    if (not proper_length) or malicious:
        raise ValueError()


def validate_input_strings(param_names: List[str], max_words: Optional[int] = None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for key, value in kwargs.items():
                if key in param_names:
                    _validate_value(value, max_words)
            return func(*args, **kwargs)

        return wrapper

    return decorator
