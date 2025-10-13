import random
import json
import uuid
from electro_voting.key_generation import gcd, generate_keypair, mod_inverse
from electro_voting.blind import blind, unblind
from electro_voting.hashing import int_hash
from electro_voting.encrypt import encrypt, sign

class Voter:
    """Клас виборця: отримує підпис, створює, шифрує та відправляє бюлетень."""
    def __init__(self, name: str, p: int, q: int, token: str, ballot_id: int = None):
        self.name = name
        self.public_key, self.private_key = generate_keypair(p, q)
        self.token = token
        self.ballot_id = ballot_id if ballot_id is not None else int(uuid.uuid4().int % 1_000_000)
        self.cec_signature = None
        print(f"👤 Створено виборця: {self.name}")

    def get_blind_signature(self, cec):
        """Проходить повний цикл сліпого підпису з ЦВК."""
        _, n_cec = cec.public_key
        message_hash = int_hash(self.ballot_id, n_cec)
        
        self.r = random.randint(2, n_cec - 1)
        blinded_hash = blind(message_hash, cec.public_key, self.r)
        
        signed_blinded_hash = cec.issue_blind_signature(blinded_hash, self.token)
        
        self.cec_signature = unblind(signed_blinded_hash, n_cec, self.r)
        print(f"✍️  {self.name}: Отримано та розсліплено підпис від ЦВК.")

    def create_and_cast_vote(self, vote: str, cec_pk: tuple, vcs_pk: tuple, vkn_part1, vkn_part2):
        """Створює, шифрує, розділяє та відправляє бюлетень."""
        print(f"🗳️  {self.name}: Голосує за '{vote}'...")
        
        ballot_int = self.ballot_id * 10 + vote

        c = encrypt(vcs_pk, ballot_int)

        n_vcs = vcs_pk[1]
        _, n_cec = cec_pk

        r1 = random.randint(2, n_vcs - 1)
        r2 = (c * mod_inverse(r1, n_vcs)) % n_vcs

        t1 = random.randint(2, n_cec - 1)
        while gcd(t1, n_cec) != 1:
            t1 = random.randint(2, n_cec - 1)
        
        t2 = (self.cec_signature * mod_inverse(t1, n_cec)) % n_cec

        part1, part2 = (r1, t1), (r2, t2)

        sig1 = sign(self.private_key, int_hash(part1, self.public_key[1]))
        sig2 = sign(self.private_key, int_hash(part2, self.public_key[1]))

        vkn_part1.receive_part(self.public_key, self.name, part1, sig1, 1)
        vkn_part2.receive_part(self.public_key, self.name, part2, sig2, 2)