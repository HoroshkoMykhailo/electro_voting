import random

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def extended_gcd(a, b):
    """
    Розширений алгоритм Евкліда.
    Повертає (gcd, x, y) такі, що a*x + b*y = gcd.
    Нам потрібен 'x', щоб знайти модульне обернене число.
    """
    if a == 0:
        return b, 0, 1
    gcd_val, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return gcd_val, x, y

def mod_inverse(e, phi):
    """
    Знаходить модульне обернене число d для e по модулю phi.
    Тобто, d таке, що (e * d) % phi = 1.
    """
    gcd_val, x, y = extended_gcd(e, phi)
    if gcd_val != 1:
        raise Exception('Модульне обернене число не існує')
    return x % phi

def generate_rsa_keys(p, q):
    """
    Генерує пари ключів RSA (відкритий та закритий) на основі простих чисел p та q.
    """
    if not (is_prime(p) and is_prime(q)):
        raise ValueError("Обидва числа p та q мають бути простими.")
    if p == q:
        raise ValueError("p та q не повинні бути однаковими.")

    n = p * q

    phi_n = (p - 1) * (q - 1)

    e = 65537

    while gcd(e, phi_n) != 1:
        e = random.randrange(3, phi_n, 2)

    d = mod_inverse(e, phi_n)

    public_key = (e, n)
    private_key = (d, n)

    return public_key, private_key

def is_prime(num):
    """Проста функція для перевірки, чи є число простим."""
    if num < 2:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True