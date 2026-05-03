import json
import re
from typing import Any, Optional


def _strip_markdown_code_fences(text: str) -> str:
    # Removes ```json ... ``` and ``` ... ``` wrappers without trying to validate JSON yet.
    text = re.sub(r"```(?:json)?", "", text, flags=re.IGNORECASE).replace("```", "")
    return text.strip()


def _extract_first_valid_json(text: str) -> Optional[str]:
    """
    Extract the first valid JSON object/array from arbitrary text.
    Uses bracket matching and validates candidates via json.loads.
    """
    if not text:
        return None

    cleaned = _strip_markdown_code_fences(text)

    # Find first '{' or '[' and attempt balanced extraction.
    for start_char, end_char in [("{", "}"), ("[", "]")]:
        start = cleaned.find(start_char)
        if start == -1:
            continue
        depth = 0
        for idx in range(start, len(cleaned)):
            ch = cleaned[idx]
            if ch == start_char:
                depth += 1
            elif ch == end_char:
                depth -= 1
                if depth == 0:
                    candidate = cleaned[start : idx + 1]
                    try:
                        json.loads(candidate)
                        return candidate
                    except json.JSONDecodeError:
                        break
    return None


def parse_json_safe(text: str) -> Optional[Any]:
    """
    LLM çıktısından JSON güvenli parse et.
    3 strateji:
    1. Direkt json.loads
    2. Markdown code block ayıkla
    3. İlk geçerli JSON objesi/dizisini çıkar
    """
    if not text or not text.strip():
        return None

    # LLM sometimes incorrectly escapes single quotes in JSON strings
    text = text.replace("\\'", "'")

    # 1. Direkt deneme
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # 2. Markdown code fences temizle + tekrar dene
    stripped = _strip_markdown_code_fences(text)
    if stripped and stripped != text:
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            pass

    # 3. İlk geçerli JSON objesi/dizisini çıkar
    candidate = _extract_first_valid_json(text)
    if candidate:
        try:
            return json.loads(candidate)
        except json.JSONDecodeError as e:
            import logging
            logging.getLogger("json_safe").error(f"JSON decode error after extraction: {e}")

    import logging
    logging.getLogger("json_safe").error("All JSON parse strategies failed!")
    return None
