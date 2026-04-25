import functools
import keyword
import re
from datetime import datetime, timezone

UTC = timezone.utc


def utcnow() -> datetime:
    return datetime.now(tz=UTC)


@functools.cache
def to_valid_python_identifier(s: str) -> str:
    # 1. Replace non-alphanumeric/non-underscore characters with '_'
    s = re.sub(r'[^0-9a-zA-Z_]', '_', s)

    # 2. Ensure it doesn't start with a number
    if s and s[0].isdigit():
        s = '_' + s

    # 3. Handle empty strings or reserved keywords
    if not s or keyword.iskeyword(s):
        s = '_' + s

    return s
