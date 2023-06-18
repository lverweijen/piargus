import re
from pathlib import Path

import unicodedata


def format_argument(argument) -> str:
    if argument is None:
        return ""
    elif isinstance(argument, Path):
        return f'"{argument!s}"'
    elif isinstance(argument, str):
        return f'"{argument!s}"'
    elif isinstance(argument, bool):
        return str(int(argument))
    else:
        return str(argument)


def slugify(value, allow_unicode=False) -> str:
    """
    Taken from https://github.com/django/django/blob/master/django/utils/text.py
    Convert to ASCII if 'allow_unicode' is False. Convert spaces or repeated
    dashes to single dashes. Remove characters that aren't alphanumerics,
    underscores, or hyphens. Convert to lowercase. Also strip leading and
    trailing whitespace, dashes, and underscores.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value.lower())
    return re.sub(r'[-\s]+', '-', value).strip('-_')
