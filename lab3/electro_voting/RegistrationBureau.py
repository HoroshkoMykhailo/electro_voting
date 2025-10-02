import random
from electro_voting.key_generation import generate_rsa_keys, is_prime

class RegistrationBureau:
    def __init__(self):
        p, q = 67, 59
        self.public_key_rb, self.private_key_rb = generate_rsa_keys(p, q)
        print("🔑 Бюро Реєстрації згенерувало власну пару ключів.")
        
        self.registered_voters = {} 
        self.available_rns = set()
        self.rn_counter = 1

    def get_registration_number(self, voter_id: str) -> int:
        """ Крок 1-2: Виборець запитує RN. БР видає унікальний RN. """
        if voter_id in self.registered_voters:
            print(f"[{voter_id}]: ❌ Вже зареєстровано (RN: {self.registered_voters[voter_id]}).")
            return self.registered_voters[voter_id]
        
        new_rn = self.rn_counter
        self.rn_counter += 1
        
        self.registered_voters[voter_id] = new_rn
        self.available_rns.add(new_rn)
        
        print(f"[{voter_id}]: ✅ Отримано Реєстраційний Номер (RN): {new_rn}.")
        return new_rn

    def send_rns_to_ec(self):
        """ Крок 3: БР відправляє список RN до ВК (без інформації про власників). """
        rns_to_send = self.available_rns.copy()
        self.available_rns.clear() 
        print(f"📡 БР відправляє {len(rns_to_send)} RN до Виборчої Комісії.")
        return rns_to_send
