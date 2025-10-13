from electro_voting.key_generation import extended_gcd


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

def sign(private_key, message):
    """
    Формує ЕЦП за допомогою закритого ключа та хешу повідомлення.
    Формула: ЕЦП = H^d mod n
    """
    d, n = private_key
    return pow(message, d, n)

def verify_signature(public_key, signature_int, original_message):
    """
    Перевіряє ЕЦП.
    """
    e, n = public_key
    recovered = pow(signature_int, e, n)
   
    return recovered == original_message