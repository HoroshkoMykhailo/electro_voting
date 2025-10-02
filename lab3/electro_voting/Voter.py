import random
from electro_voting.key_generation import generate_rsa_keys
from electro_voting.hashing import quadratic_hash
from electro_voting.encrypt import encrypt
from electro_voting.candidates import CANDIDATE_TO_CODE

class Voter:
    def __init__(self, voter_id, public_key_ec):
        self.voter_id = voter_id
        self.public_key_ec = public_key_ec
        self.n_ec = public_key_ec[1]
        
        p, q = 79, 83
        self.public_key_voter, self.private_key_voter = generate_rsa_keys(p, q)
        print(f"[{self.voter_id}]: 🔑 Згенеровано власну пару ключів для ЕЦП.")
        
        self.registration_number = None
        self.ballot_uid = random.randint(1, self.n_ec - 1)

    def register_with_rb(self, rb_instance):
        """ Крок 1-2: Реєстрація у Бюро Реєстрації. """
        self.registration_number = rb_instance.get_registration_number(self.voter_id)

    def sign_message(self, message: str) -> int:
        """ Підписує хеш повідомлення своїм закритим ключем (d, n_voter). """
        d, n_voter = self.private_key_voter
        message_hash = quadratic_hash(message, n_voter)
        signature = pow(message_hash, d, n_voter)
        return signature

    def vote(self, choice: str) -> dict:
        """
        Крок 4: Створює повідомлення, підписує його своїм ключем
        та шифрує відкритим ключем ВК.
        Повідомлення M = 'ID|RN|Choice|Signature_Voter'
        """
        if self.registration_number is None:
            raise Exception("Виборець не має реєстраційного номера (RN).")
        
        if choice not in CANDIDATE_TO_CODE:
            raise ValueError(f"Невідомий кандидат: {choice}")
            
        choice_code = CANDIDATE_TO_CODE[choice]
        
        message_to_sign = f"{self.ballot_uid}|{self.registration_number}|{choice}"
        
        signature_voter = self.sign_message(message_to_sign)
        
        encrypted_id = encrypt(self.public_key_ec, self.ballot_uid)
        encrypted_rn = encrypt(self.public_key_ec, self.registration_number)
        encrypted_choice = encrypt(self.public_key_ec, choice_code)
        encrypted_sig = encrypt(self.public_key_ec, signature_voter)
        
        print(f"[{self.voter_id}]: ✅ Сформовано бюлетень, підписано (ЕЦП), зашифровано (ВК).")
        
        return {
            'encrypted_message': 0, 
            'encrypted_id': encrypted_id,
            'encrypted_rn': encrypted_rn,
            'encrypted_choice': encrypted_choice,
            'encrypted_sig': encrypted_sig,
        }, self.public_key_voter
    
    def verify_vote(self, published_ballots, choice: str):
        """Перевіряє, чи голос виборця відображений правильно у публікації ВК."""
        for ballot in published_ballots:
            if ballot['id'] == str(self.ballot_uid) and ballot['choice'] == choice:
                print(f"[{self.voter_id}]: ✅ Голос підтверджено ({choice}).")
                return True
        print(f"[{self.voter_id}]: ❌ ПОМИЛКА: Голос не знайдено або змінено!")
        return False