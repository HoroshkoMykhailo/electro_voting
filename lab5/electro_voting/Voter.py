import random
from electro_voting.encrypt import encrypt, decrypt, sign, encode_vote_with_rp, decode_vote_and_rp
from electro_voting.hashing import int_hash

class Voter:
    def __init__(self, name, keypair, rp_bits=8):
        self.name = name
        self.public_key, self.private_key = keypair
        self.rp_bits = rp_bits
        self.rp1 = random.randrange(1, 1 << rp_bits)
        self.rp2 = random.randrange(1, 1 << rp_bits)
        print(f"👤 Створено {self.name}, rp1={self.rp1}, rp2={self.rp2}")

    def create_ballot(self, vote_id: int, voter_objects_ordered):
        """
        Створює єдиний пакет даних (payload), який містить
        в собі голос та обидва маркери за принципом матрьошки.
        Цей пакет шифрується ОДИН раз усіма ключами.
        """
        inner_payload = encode_vote_with_rp(vote_id, self.rp1, self.rp_bits)

        outer_payload = encode_vote_with_rp(inner_payload, self.rp2, self.rp_bits)
        
        n = self.public_key[1]
        if outer_payload >= n:
            raise Exception(f"Помилка: згенерований пакет ({outer_payload}) більший за модуль n ({n}). Зменшіть RP_BITS або збільшіть діапазон простих чисел.")

        encrypted_ballot = outer_payload
        for voter in reversed(voter_objects_ordered):
            encrypted_ballot = encrypt(voter.public_key, encrypted_ballot)

        return encrypted_ballot

    def mix_and_decrypt_step(self, ballot_list):
        """
        Знімає один шар шифрування з усіх бюлетенів, перемішує і підписує.
        """
        print(f"  -> {self.name} розшифровує і перемішує {len(ballot_list)} бюлетенів.")
        decrypted_list = [decrypt(self.private_key, b) for b in ballot_list]
        random.shuffle(decrypted_list)

        list_tuple = tuple(sorted(decrypted_list))
        data_hash = int_hash(list_tuple, self.public_key[1])
        signature = sign(self.private_key, data_hash)
        
        return decrypted_list, signature

    def find_and_unwrap_ballot(self, ballot_list, round_num):
        """
        Знаходить свій бюлетень у списку ПІСЛЯ повного раунду розшифрування
        і видаляє відповідний маркер (rp).
        """
        rp_to_check = self.rp2 if round_num == 1 else self.rp1
        
        for ballot in ballot_list:
            if round_num == 1:
                decoded_message, rp_candidate = decode_vote_and_rp(ballot, self.rp_bits)
                if rp_candidate == rp_to_check:
                    print(f"     - {self.name} знайшов свій бюлетень (раунд 1, rp={rp_to_check}) і видалив зовнішній маркер.")
                    return decoded_message 
            else:
                decoded_message, rp_candidate = decode_vote_and_rp(ballot, self.rp_bits)
                if rp_candidate == rp_to_check:
                    print(f"     - {self.name} знайшов свій бюлетень (раунд 2, rp={rp_to_check}) і видалив внутрішній маркер.")
                    return decoded_message 
        
        raise Exception(f"!!! ПОМИЛКА: {self.name} не знайшов свій бюлетень в кінці раунду {round_num}!")