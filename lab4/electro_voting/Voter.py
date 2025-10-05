import random

from electro_voting.key_generation import find_factors, generate_rsa_keys
from electro_voting.key_generation import is_prime
from electro_voting.encrypt import encrypt, sign

class Voter:
    def __init__(self, name, cec_public_key):
        self.name = name
        self.cec_public_key = cec_public_key
        p, q = random.sample([p for p in range(50, 100) if is_prime(p)], 2)
        self.public_key, self.private_key = generate_rsa_keys(p, q)
        self.anonymous_id = random.randint(10000, 99999)
        print(f"👤 Створено виборця '{self.name}' з анонімним ID: {self.anonymous_id}.")

    def create_ballots(self, candidate_id):
        """Розділяє ID кандидата на 2 множники та створює 2 зашифровані бюлетені."""
        m1, m2 = find_factors(candidate_id)
        print(f"[{self.name}]: Обрав кандидата з ID={candidate_id}. Розділив на множники: {m1} та {m2}.")

        encrypted_m1 = encrypt(self.cec_public_key, m1)
        encrypted_m2 = encrypt(self.cec_public_key, m2)
        
        signature1 = sign(self.private_key, encrypted_m1)
        signature2 = sign(self.private_key, encrypted_m2)
        
        ballot1 = {
            'voter_name': self.name,
            'anonymous_id': self.anonymous_id,
            'encrypted_part': encrypted_m1,
            'signature': signature1,
            'voter_public_key': self.public_key
        }
        
        ballot2 = {
            'voter_name': self.name,
            'anonymous_id': self.anonymous_id,
            'encrypted_part': encrypted_m2,
            'signature': signature2,
            'voter_public_key': self.public_key
        }
        
        return ballot1, ballot2

    def verify_final_vote(self, final_results, expected_candidate_id):
        """Перевіряє, чи правильно ЦВК врахувала його голос."""
        voter_result = final_results.get(self.anonymous_id)
        if voter_result and voter_result == expected_candidate_id:
            print(f"[{self.name}]: ✅ Мій голос (ID {self.anonymous_id}) враховано вірно! Кандидат: {expected_candidate_id}.")
        else:
            print(f"[{self.name}]: ❌ ПОМИЛКА! Мій голос не знайдено або враховано неправильно.")