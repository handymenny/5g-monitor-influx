#!/usr/bin/env python3
"""Common parsing helpers."""

import re
from typing import Iterator, List, Optional


# Lines that are empty or status words (OK / ERROR) are skipped.
_SKIP = frozenset({"", "OK", "ERROR"})

# Tokenization regex for AT response payloads (comma separated values).
# Pattern structure (two alternations):
# 1) "([^"]*)"
#    - Matches quoted strings. Group 1 captures the content inside quotes.
#    - Allows empty quoted strings (""), so group 1 can be an empty string.
# 2) \s*([^,]*[^,\s])\s*
#    - Matches unquoted tokens possibly surrounded by whitespace.
#    - Captures a sequence that does not contain a comma and is not purely whitespace.
#    - The trailing [^,\s] ensures we don't capture empty or whitespace-only tokens
#      (so consecutive commas or trailing commas don't produce spurious empty values).
#
# Examples:
#  payload: '"a b",123,-92,foo'  -> groups: ['a b','123','-92','foo']
#  payload: '"",42'              -> groups: ['','42']
#  payload: '1,2,3'               -> groups: ['1','2','3']
_TOKEN_RE = re.compile(r'"([^"]*)"|\s*([^,]*[^,\s])\s*')


def parse_response(text: str, prefix: str) -> Iterator[List[str]]:
    """Yield parsed value lists for each AT response line matching *prefix*.

    Lines that are empty or status words (OK / ERROR) are skipped.
    Quoted values are unquoted automatically; unquoted tokens are trimmed.

    The function returns an iterator of lists of strings; callers expect the
    same ordering and tokenization as before.
    """
    tag = f"{prefix}:"
    tag_len = len(tag)

    for raw_line in text.splitlines():
        stripped = raw_line.strip()

        # Skip lines that don't start with the expected tag or are in the _SKIP set.
        if stripped in _SKIP or not stripped.startswith(tag):
            continue

        # Extract text after the tag
        response = stripped[tag_len:].strip()

        # For each match, group(1) is the quoted string (may be empty),
        # group(2) is the unquoted token (guaranteed non-empty when present).
        tokens = []
        for m in _TOKEN_RE.finditer(response):
            if m.group(1) is not None:
                tokens.append(m.group(1))
            else:
                tokens.append(m.group(2))
        yield tokens


def parse_int(val: str, default: int = 0, hex: bool = False) -> int:
    value = parse_optional_int(val, default, hex)
    return value if value is not None else default


def parse_optional_int(
    val: str, default: Optional[int] = None, hex: bool = False
) -> Optional[int]:
    try:
        return int(val, 16) if hex else int(val)
    except ValueError:
        return default
