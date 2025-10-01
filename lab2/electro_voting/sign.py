def encrypt(public_key, plaintext_message):
    """
    Шифрує повідомлення за допомогою відкритого ключа.
    C = M^e mod n
    """
    e, n = public_key
    ciphertext = pow(plaintext_message, e, n)
    return ciphertext

def decrypt(private_key, ciphertext):
    """
    Розшифровує повідомлення за допомогою закритого ключа.
    M = C^d mod n
    """
    d, n = private_key
    plaintext_message = pow(ciphertext, d, n)
    return plaintext_message

def sign(message_hash: int, private_key: tuple) -> int:
    """
    Формує ЕЦП за допомогою закритого ключа та хешу повідомлення.
    Формула: ЕЦП = H^d mod n
    """
    d, n = private_key
    signature = pow(message_hash, d, n)
    return signature

def verify(signature: int, public_key: tuple) -> int:
    """
    Отримує хеш з ЕЦП за допомогою відкритого ключа.
    Формула: H_c = ЕЦП^e mod n
    """
    e, n = public_key
    calculated_hash = pow(signature, e, n)
    return calculated_hash