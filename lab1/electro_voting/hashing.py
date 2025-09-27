UKRAINIAN_ALPHABET = "абвгґдеєжзиіїйклмнопрстуфхцчшщьюя"
ALPHABET_MAP = {char: i + 1 for i, char in enumerate(UKRAINIAN_ALPHABET)}

def quadratic_hash(message: str, n: int) -> int:
    """
    Обчислює хеш-образ повідомлення за допомогою квадратичної згортки.
    Формула: H_i = (H_{i-1} + M_i)^2 mod n
    де H_0 = 0, M_i - номер букви в алфавіті.
    """
    
    h = 0 
    
    processed_message = message.lower().replace(" ", "")
    
    for char in processed_message:
        if char in ALPHABET_MAP:
            m_i = ALPHABET_MAP[char]
            h = pow(h + m_i, 2, n)
            
    return h