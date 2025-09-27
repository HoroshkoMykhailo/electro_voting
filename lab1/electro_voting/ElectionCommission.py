from electro_voting.hashing import quadratic_hash
from electro_voting.key_generation import generate_rsa_keys
from electro_voting.sign import verify

class CentralElectionCommission:
    def __init__(self, candidates, voter_ids):
        self.candidates = {candidate: 0 for candidate in candidates}
        self.voter_ids = voter_ids
        
        p, q = 61, 53 
        self.public_key, self.private_key = generate_rsa_keys(p, q)
        print("🔑 ЦВК згенерувала власну пару ключів.")
        
        self.voter_public_keys = {}
        self._voter_private_keys = {}
        self.received_ballots = {}
        self.has_voted = []

    def generate_voter_keys(self):
        primes = [101, 103, 107, 109, 113, 127, 131, 137, 139, 149]
        for i, voter_id in enumerate(self.voter_ids):
            p, q = primes[2*i], primes[2*i+1]
            pub_key, priv_key = generate_rsa_keys(p, q)
            self.voter_public_keys[voter_id] = pub_key
            self._voter_private_keys[voter_id] = priv_key
        print("🔑 ЦВК згенерувала ключі для всіх виборців.")
    
    def get_voter_private_key(self, voter_id):
        return self._voter_private_keys[voter_id]
    
    def receive_ballot(self, voter_id, ballot_package):
        """
        Приймає та реєструє бюлетень, ігноруючи повторні надсилання.
        """
        if voter_id in self.received_ballots:
            print(f"📬 -> ❌ Бюлетень від '{voter_id}' вже отримано раніше. Повторне надсилання проігноровано.")
            return
        
        self.received_ballots[voter_id] = ballot_package
        print(f"📬 ЦВК отримала бюлетень від '{voter_id}'.")

    def process_ballots(self):
        print("\n--- PROCESSING: ЦВК починає обробку бюлетенів ---\n")
        for voter_id, ballot_data in self.received_ballots.items():
            print(f"Опрацювання бюлетеня від '{voter_id}':")
            
            try:
                voter_public_key = self.voter_public_keys[voter_id]
            except KeyError:
                print(f"  -> ❌ ПОМИЛКА: Виборець '{voter_id}' не знайдений у реєстрі.")
                print("  -> Бюлетень проігноровано.")
                print("-" * 20)
                continue

            choice = ballot_data['choice']
            signature = ballot_data['signature']

            print(f"  -> Отримано підпис: {signature}")
            
            hash_from_signature = verify(signature, voter_public_key)
            print(f"  -> З підпису отримано хеш: {hash_from_signature}")

            expected_hash = quadratic_hash(choice, voter_public_key[1])
            print(f"  -> Очікуваний хеш для '{choice}': {expected_hash}")
            
            if hash_from_signature == expected_hash:
            
                print(f"  -> ✅ Підпис дійсний. Хеші збігаються.")
                try:
                    self.candidates[choice] += 1
                except KeyError:
                    print(f"  -> ❌ ПОМИЛКА: Бюлетень пошкоджено.")
                    print("  -> Бюлетень проігноровано.")
                    print("-" * 20)
                    continue
                print(f"  -> ✅ Голос за '{choice}' зараховано.")
            else:
                print(f"  -> ❌ ПІДПИС НЕПРАВИЛЬНИЙ. Хеші не збігаються.")
            print("-" * 20)

    def publish_results(self):
        print("\n--- 📊 РЕЗУЛЬТАТИ ГОЛОСУВАННЯ ---")
        for candidate, votes in self.candidates.items():
            print(f"Кандидат '{candidate}': {votes} голосів")

        if not any(self.candidates.values()):
            print("\nЖодного голосу не було зараховано.")
            return

        max_votes = max(self.candidates.values())
        winners = [candidate for candidate, num_votes in self.candidates.items() if num_votes == max_votes]
        
        if len(winners) > 1:
            tied_candidates = ", ".join(winners)
            print(f"\n🤝 Результат: нічия! Кандидати '{tied_candidates}' набрали по {max_votes} голосів.")
            print("Потрібне повторне голосування.")
        else:
            winner = winners[0]
            print(f"\n🏆 Переможець: {winner}")