from electro_voting.hashing import quadratic_hash
from electro_voting.sign import encrypt, sign


class Voter:
    def __init__(self, voter_id, private_key):
        self.voter_id = voter_id
        self.private_key = private_key

    def create_ballot(self, candidate_name):
        n_voter = self.private_key[1]
        
        print(f"[{self.voter_id}]: Обирає кандидата '{candidate_name}'.")

        ballot_hash = quadratic_hash(candidate_name, n_voter)
        print(f"[{self.voter_id}]: Хеш бюлетеня = {ballot_hash}")

        signature = sign(ballot_hash, self.private_key)
        print(f"[{self.voter_id}]: ✅ Підпис зашифровано ключем ЦВК.")

        
        return {'choice': candidate_name, 'signature': signature}