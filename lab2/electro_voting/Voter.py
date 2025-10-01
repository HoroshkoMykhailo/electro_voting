import random

from electro_voting.key_generation import gcd
from electro_voting.hashing import quadratic_hash
from electro_voting.blind import blind, unblind
from electro_voting.sign import encrypt
from electro_voting.candidates import CANDIDATE_TO_CODE

class Voter:
    def __init__(self, voter_id, public_key_cec):
        self.voter_id = voter_id
        self.public_key_cec = public_key_cec
        self.n_cec = public_key_cec[1]
        self.ballot_uid = random.getrandbits(128)
        self.r_values = []
        self.candidates = []
        self.signed_ballots = {}

    def generate_ballot_sets(self, candidates, num_sets=10):
        """
        Кроки 2-4: Генерує 10 наборів бюлетенів, хешує їх,
        додає UID та маскує за допомогою r.
        Повертає список замаскованих наборів, множники маскування ТА розкритий вміст.
        """
        self.candidates = candidates
        self.r_values = []
        blinded_ballot_sets = []
        content_sets = [] 
        
        for _ in range(num_sets):
            blinded_set = {}
            content_set = {}
            
            while True:
                r = random.randrange(2, self.n_cec)
                if gcd(r, self.n_cec) == 1:
                    break
            self.r_values.append(r)
            
            for candidate in candidates:
                message = f"{self.ballot_uid}|{candidate}"
                message_hash = quadratic_hash(message, self.n_cec)
                
                blinded_hash = blind(message_hash, self.public_key_cec, r)
                
                blinded_set[candidate] = blinded_hash
                content_set[candidate] = message
            
            blinded_ballot_sets.append(blinded_set)
            content_sets.append(content_set)
            
        print(f"[{self.voter_id}]: ✅ Згенеровано {num_sets} замаскованих наборів бюлетенів (ID: {self.ballot_uid}).")
        
        return blinded_ballot_sets, self.r_values, content_sets

    def process_signed_ballots(self, signed_set: dict, r: int):
        """
        Крок 8: Знімає маскування з підписаних бюлетенів.
        """
        self.signed_ballots = {}
        for candidate, signed_hash_prime in signed_set.items():
            signature = unblind(signed_hash_prime, self.n_cec, r)
            self.signed_ballots[candidate] = signature
        
        print(f"[{self.voter_id}]: ✅ Отримано та розмасковано підписані бюлетені ЦВК.")
        
    def vote(self, choice: str) -> dict:
        """
        Кроки 9-10: Обирає один бюлетень, шифрує його та надсилає.
        Тепер шифрується як підпис, так і вибір.
        """
        if choice not in self.signed_ballots:
            raise ValueError(f"Кандидат '{choice}' не знайдений у підписаних бюлетенях.")
        
        ballot_signature = self.signed_ballots[choice] 

        if choice not in CANDIDATE_TO_CODE:
             raise ValueError(f"Невідомий кандидат: {choice}")
        choice_code = CANDIDATE_TO_CODE[choice]
        
        encrypted_signature = encrypt(self.public_key_cec, ballot_signature)
        
        encrypted_choice = encrypt(self.public_key_cec, choice_code)
        
        print(f"[{self.voter_id}]: ✅ Обрано бюлетень. Підпис ЦВК та вибір зашифровано.")
        
        return {
            'uid': self.ballot_uid, 
            'encrypted_choice': encrypted_choice, 
            'encrypted_signature': encrypted_signature
        }