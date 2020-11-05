# coding:utf-8
import sys

PY3 = sys.version_info[0] == 3
if PY3:
    text_type = str
    binary_type = bytes
else:
    text_type = unicode
    binary_type = str


def text_(s, encoding='utf-8', errors='strict'):
    """
    Convert s to bytes.

    Args:
        s: (todo): write your description
        encoding: (str): write your description
        errors: (todo): write your description
    """
    if isinstance(s, binary_type):
        return s.decode(encoding, errors)
    return s


def bytes_(s, encoding='utf-8', errors='strict'):
    """
    Encode s to bytes.

    Args:
        s: (todo): write your description
        encoding: (str): write your description
        errors: (todo): write your description
    """
    if isinstance(s, text_type):
        return s.encode(encoding, errors)
    return s
