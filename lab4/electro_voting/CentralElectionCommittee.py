from electro_voting.key_generation import generate_rsa_keys
from electro_voting.encrypt import decrypt


class CentralElectionCommittee:
    def __init__(self, candidates_map, voters_list):
        print("🏛️ Створено Центральну Виборчу Комісію (ЦВК).")
        self.candidates = candidates_map
        self.id_to_candidate = {v: k for k, v in candidates_map.items()}
        self.voters = voters_list
        
        p, q = 61, 53
        self.public_key, self.private_key = generate_rsa_keys(p, q)
        self.n = self.public_key[1]
        print(f"🔑 ЦВК згенерувала ключі. Відкритий ключ (e, n): {self.public_key}.")
        
        self.final_results = {}

    def distribute_voters(self, ec1, ec2):
        """Надає повний список виборців обом ВК для верифікації підписів."""
        ec1.set_voter_list(self.voters)
        ec2.set_voter_list(self.voters)
        print("📜 ЦВК надала повні списки виборців комісіям ВК-1 та ВК-2 для верифікації.")


    def tally_votes(self, data_from_ec1, data_from_ec2):
        """Крок 6: Збирає дані, об'єднує бюлетені та розшифровує їх."""
        print("\n=== 📊 ЕТАП ПІДРАХУНКУ ГОЛОСІВ (ЦВК) ===")
        
        all_data = data_from_ec1 + data_from_ec2
        grouped_ballots = {}
        for item in all_data:
            anon_id = item['anonymous_id']
            if anon_id not in grouped_ballots:
                grouped_ballots[anon_id] = []
            grouped_ballots[anon_id].append(item['encrypted_part'])
        
        vote_counts = {name: 0 for name in self.candidates.keys()}

        for anon_id, parts in grouped_ballots.items():
            if len(parts) != 2:
                print(f"  -> ⚠️ Помилка: для ID {anon_id} знайдено не 2 частини бюлетеня. Голос не враховано.")
                continue

            c1, c2 = parts[0], parts[1]
            
            combined_ciphertext = (c1 * c2) % self.n
            
            decrypted_candidate_id = decrypt(self.private_key, combined_ciphertext)
            
            self.final_results[anon_id] = decrypted_candidate_id
            
            candidate_name = self.id_to_candidate.get(decrypted_candidate_id, "Невідомий кандидат")
            if candidate_name != "Невідомий кандидат":
                vote_counts[candidate_name] += 1
            
            print(f"  -> ID виборця {anon_id}: C1={c1}, C2={c2}. C_combined={combined_ciphertext}. Розшифровано ID кандидата: {decrypted_candidate_id} ({candidate_name})")
        
        return vote_counts

    def publish_final_results(self, vote_counts):
        """Публікує фінальні результати голосування."""
        print("\n--- 🏁 ОСТАТОЧНІ РЕЗУЛЬТАТИ ГОЛОСУВАННЯ ---")
        for candidate, votes in vote_counts.items():
            print(f"Кандидат '{candidate}': {votes} голосів")
        
        max_votes = -1
        winners = []
        if vote_counts:
            max_votes = max(vote_counts.values())
            winners = [c for c, num in vote_counts.items() if num == max_votes]

        if len(winners) == 1:
            print(f"\n🏆 Переможець: {winners[0]}")
        elif len(winners) > 1:
             print(f"\n🤝 Результат: нічия між {', '.join(winners)}.")
        else:
            print("\n🤷 Голосів не було.")

        print("\n--- 📜 ОПУБЛІКОВАНІ ДАНІ ДЛЯ ПЕРЕВІРКИ ВИБОРЦЯМИ ---")
        print(f"{'Анонімний ID':<15} | {'ID Кандидата':<15}")
        print("-" * 33)
        for anon_id, candidate_id in self.final_results.items():
            print(f"{anon_id:<15} | {candidate_id:<15}")