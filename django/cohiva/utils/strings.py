import re


def pluralize(count, singular, plural):
    if count == 1:
        return f"1 {singular}"
    return f"{count} {plural}"


def sanitize_log_message(text: str):
    return _sanitize_uris(text)


def _sanitize_uris(text: str):
    pattern = (
        r"\b(?P<protocol>[a-zA-Z][a-zA-Z0-9+.-]*)://"
        r"(?P<username>[^:@/\s]+):(?P<password>[^@/\s]+)@"
        r"(?P<host>[^/\s?#]+)"
    )
    safe_text = re.sub(pattern, r"\g<protocol>://\g<username>:******@\g<host>", text)
    return safe_text
