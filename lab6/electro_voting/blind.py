from electro_voting.key_generation import mod_inverse

def blind(message_hash: int, public_key: tuple, r: int) -> int:
    """
    Маскування бюлетеня (перший етап сліпого ЕЦП).
    m' = m * (r^e) mod n
    e, n - відкритий ключ ЦВК
    r - випадковий множник маскування, НСД(r, n) = 1
    """
    e, n = public_key
    r_pow_e = pow(r, e, n)
    blinded_hash = (message_hash * r_pow_e) % n
    return blinded_hash

def unblind(signed_hash_prime: int, n: int, r: int) -> int:
    """
    Зняття маскування з підписаного хешу.
    s = s' * (r^{-1}) mod n
    s' - підписаний хеш (підпис)
    r - множник маскування
    n - модуль ключа ЦВК
    """
    r_inverse = mod_inverse(r, n)
    signature = (signed_hash_prime * r_inverse) % n
    return signature
def unmask_blinded_for_verification(blinded_value: int, public_key: tuple, r: int) -> int:
    """
    Знімає маску з замаскованого значення m' згідно формули:
    m = (m' * (r^{-1} mod n)^e mod n) mod n
    Використовується ЦВК при перевірці розкритого вмісту (до підпису).
    """
    e, n = public_key
    r_inv = mod_inverse(r, n)
    factor = pow(r_inv, e, n)
    unmasked = (blinded_value * factor) % n
    return unmasked

def sign_blinded(blinded_hash: int, private_key: tuple) -> int:
    """
    Підписання замаскованого хешу ЦВК (аналог звичайного RSA-підпису).
    s' = (m')^d mod n
    d, n - закритий ключ ЦВК
    """
    d, n = private_key
    signed_hash_prime = pow(blinded_hash, d, n)
    return signed_hash_prime