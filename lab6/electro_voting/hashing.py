import hashlib


def int_hash(obj, n):
    """
    Хешує об'єкт і повертає ціле число в діапазоні [0, n-1].
    """
    b = repr(obj).encode()
    h = hashlib.sha256(b).digest()
    return int.from_bytes(h, "big") % n