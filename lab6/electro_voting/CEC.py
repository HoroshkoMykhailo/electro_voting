import random
from electro_voting.key_generation import generate_keypair
from electro_voting.blind import sign_blinded
from electro_voting.candidates import REVERSED_CANDIDATES

class CEC:
    """Центральна Виборча Комісія: видає сліпі підписи, підбиває підсумки."""
    def __init__(self, p: int, q: int, token_db: set):
        self.name = "Центральна Виборча Комісія"
        self.public_key, self.private_key = generate_keypair(p, q)
        self.valid_tokens = token_db
        self.used_tokens = set()
        self.jurisdictions = {}
        print(f"🏢 Створено ЦВК.")

    def set_jurisdictions(self, voter_list: list, vcs1_name: str, vcs2_name: str):
        """Розподіляє виборців між двома ВКС."""
        shuffled_voters = random.sample(voter_list, len(voter_list))
        mid = len(shuffled_voters) // 2
        self.jurisdictions[vcs1_name] = shuffled_voters[:mid]
        self.jurisdictions[vcs2_name] = shuffled_voters[mid:]
        print(f"🗺️  ЦВК: Юрисдикції для {vcs1_name} та {vcs2_name} розподілено.")

    def issue_blind_signature(self, blinded_hash: int, token: str) -> int:
        """Перевіряє токен та підписує засліплений хеш."""
        if token in self.valid_tokens and token not in self.used_tokens:
            self.used_tokens.add(token)
            return sign_blinded(blinded_hash, self.private_key)
        else:
            raise PermissionError("❌ Помилка: Недійсний або вже використаний токен!")

    def publish_results(self, final_tally: dict, counted_ballot_ids: set):
        """Публікує фінальні результати голосування."""
        final_tally_named = {REVERSED_CANDIDATES[k]: v for k, v in final_tally.items()}
        print("\n" + "="*50)
        print("🏆🏆🏆 ФІНАЛЬНІ РЕЗУЛЬТАТИ ВИБОРІВ 🏆🏆🏆")
        print("="*50)
        for candidate, count in final_tally_named.items():
            print(f"  {candidate}: {count} голос(ів)")
        print("-" * 50)
        print(f"Всього враховано бюлетенів: {len(counted_ballot_ids)}")
        print("="*50)