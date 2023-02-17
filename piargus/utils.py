from pathlib import Path


def format_argument(text):
    if text is None:
        return ""
    elif isinstance(text, Path):
        return f'"{text!s}"'
    elif isinstance(text, str):
        return f'"{text!s}"'
    elif isinstance(text, bool):
        return str(int(text))
    else:
        return str(text)
