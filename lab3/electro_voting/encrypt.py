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