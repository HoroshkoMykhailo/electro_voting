import random
from electro_voting.encrypt import encrypt, decrypt, sign, encode_vote_with_rp, decode_vote_and_rp
from electro_voting.hashing import int_hash

class Voter:
    def __init__(self, name, keypair):
        self.name = name
        self.encrypted1 = None
        self.encrypted2 = None
        self.public_key, self.private_key = keypair
        self.rp1 = random.randrange(1, 100)
        self.rp2 = random.randrange(1, 100)
        print(f"👤 Створено {self.name}")

    def create_ballot(self, vote_id: int, voter_objects_ordered):
        """
        Створює бюлетень, зашифрований у два раунди:
        1. Перший раунд: шифрування відкритими ключами E→D→C→B→A.
           Коли черга доходить до поточного виборця, додається RP перед шифруванням.
        2. Другий раунд: повторення першого етапу шифрування.
        """
        # --- 1️⃣ Базовий бюлетень (без RP) ---
        encrypted_ballot = vote_id

        # --- 2️⃣ Перший раунд шифрування ---
        for voter in reversed(voter_objects_ordered):
            if voter.name == self.name:
                self.encrypted1 = encrypted_ballot
                encrypted_ballot = encode_vote_with_rp(encrypted_ballot, self.rp1)
            encrypted_ballot = encrypt(voter.public_key, encrypted_ballot)

        # --- 3️⃣ Другий раунд шифрування ---
        for voter in reversed(voter_objects_ordered):
            if voter.name == self.name:
                self.encrypted2 = encrypted_ballot
                encrypted_ballot = encode_vote_with_rp(encrypted_ballot, self.rp2)
            encrypted_ballot = encrypt(voter.public_key, encrypted_ballot)

        return encrypted_ballot

    def mix_and_decrypt_step(self, ballot_list, round_num):
        """
        Знімає один шар шифрування з усіх бюлетенів, перемішує,
        перевіряє RP і видаляє його тільки зі свого бюлетеня.
        
        round_num = 1 -> перевірка rp2
        round_num = 2 -> перевірка rp1
        """
        print(f"  -> {self.name} розшифровує і перемішує {len(ballot_list)} бюлетенів.")

        rp_to_check = self.rp2 if round_num == 1 else self.rp1
        encrypted_to_check = self.encrypted2 if round_num == 1 else self.encrypted1

        found_own_ballot = False

        decrypted_list = []
        for ballot in ballot_list:
            decrypted = decrypt(self.private_key, ballot)
            vote = decode_vote_and_rp(decrypted, rp_to_check)
            if encrypted_to_check == vote:
                decrypted = vote
                found_own_ballot = True
            decrypted_list.append(decrypted)

        if not found_own_ballot:
            raise Exception(f"!!! ПОМИЛКА: {self.name} не знайшов свій бюлетень у раунді {round_num}!")
        
        random.shuffle(decrypted_list)

        list_tuple = tuple(sorted(decrypted_list))
        data_hash = int_hash(list_tuple, self.public_key[1])
        signature = sign(self.private_key, data_hash)

        return decrypted_list, signature