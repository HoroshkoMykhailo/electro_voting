from collections import Counter
from electro_voting.encrypt import verify_signature, decrypt

class MediumLevelCommission:
    """Виборча Комісія Середнього Рівня: збирає, об'єднує та розшифровує бюлетені."""
    def __init__(self, name: str, p: int, q: int):
        from electro_voting.key_generation import generate_keypair
        self.name = name
        self.public_key, self.private_key = generate_keypair(p, q)
        self.parts1 = {}
        self.parts2 = {}
        self.assembled_ballots = {}
        self.decrypted_votes = {}
        print(f"🏤 Створено ВКС: {self.name}")

    def receive_parts(self, parts: dict, part_type: int):
        if part_type == 1: self.parts1.update(parts)
        else: self.parts2.update(parts)
        print(f"📬 {self.name}: Отримано {len(parts)} частин бюлетенів типу {part_type}.")

    def assemble_and_verify(self, cec_pk: tuple, voters: dict):
        """Збирає бюлетені з частин та перевіряє сліпий підпис ЦВК."""
        print(f"🧩 {self.name}: Об'єднання бюлетенів та перевірка підписів ЦВК...")
        n_cec = cec_pk[1]
        n_vcs = self.public_key[1]
        
        for voter_name, (r1, t1) in self.parts1.items():
            if voter_name in self.parts2:
                r2, t2 = self.parts2[voter_name]
                c = (r1 * r2) % n_vcs
                s = (t1 * t2) % n_cec
                
                voter = voters[voter_name]
                from electro_voting.hashing import int_hash
                ballot_hash = int_hash(voter.ballot_id, n_cec)

                if verify_signature(cec_pk, s, ballot_hash):
                    self.assembled_ballots[voter_name] = c
                else:
                    print(f"🔥 УВАГА: Невалідний підпис ЦВК для бюлетеня від {voter_name}!")
        print(f"✅ {self.name}: {len(self.assembled_ballots)} бюлетенів успішно зібрано.")

    def decrypt_votes(self):
        """Розшифровує всі зашифровані голоси власним ключем."""
        for name, c in self.assembled_ballots.items():
            decrypted_int = decrypt(self.private_key, c)
            ballot_id = decrypted_int // 10
            vote = decrypted_int % 10
            self.decrypted_votes[name] = (ballot_id, vote)

    def count_votes(self) -> tuple:
        """Підраховує голоси та повертає результати і ID врахованих бюлетенів."""
        votes = [vote for (_, vote) in self.decrypted_votes.values()]
        results = Counter(votes)
        counted_ids = {ballot_id for (ballot_id, _) in self.decrypted_votes.values()}
        print(f"📊 {self.name}: Результати підраховано: {dict(results)}")
        return results, counted_ids