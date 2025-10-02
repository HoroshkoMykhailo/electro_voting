from electro_voting.encrypt import decrypt
from electro_voting.hashing import quadratic_hash
from electro_voting.key_generation import generate_rsa_keys, verify_signature
from electro_voting.candidates import CODE_TO_CANDIDATE

class ElectionCommittee:
    def __init__(self, candidates):
        self.candidates = {candidate: 0 for candidate in candidates}
        self.candidates_list = candidates

        p, q = 71, 73
        self.public_key, self.private_key = generate_rsa_keys(p, q)
        self.n_ec = self.public_key[1]
        print("🔑 Виборча Комісія згенерувала власну пару ключів.")
        
        self.available_rns = set() 
        self.successful_voter_ids = set() 
        self.published_ballots = [] 

    def receive_rns_from_rb(self, rns: set):
        """ Отримує доступні RN від БР (Крок 3). """
        self.available_rns.update(rns)
        print(f"📝 ВК отримала {len(rns)} RN від БР.")

    def receive_vote_package(self, vote_package: dict, voter_public_key: tuple) -> bool:
        """
        Крок 5: Приймає зашифрований голос, розшифровує, перевіряє RN та ЕЦП.
        vote_package = {'encrypted_message': C}
        Повідомлення M = 'ID|RN|Choice|Signature_Voter'
        """
        
        # 1. Розшифрування повідомлення (Закритим ключем ВК)
        # Увага: Для цього потрібен був би більш складний механізм, 
        # наприклад, гібридне шифрування, або RSA дозволяє лише шифрування
        # одного великого числа. Для спрощення, припустимо, що зашифроване число
        # містить об'єднану інформацію (ID|RN|Choice|Signature). 
        # Оскільки не маємо механізму для такого об'єднання/розділення в
        # існуючих файлах, *імітуємо* передачу структури даних:
        
        try:
            # Тут в реальності має бути: decrypt(private_key, encrypted_message) 
            # з подальшою десеріалізацією. Для демонстрації:
            rn = decrypt(self.private_key, vote_package.get('encrypted_rn', 0))
            voter_id = decrypt(self.private_key, vote_package.get('encrypted_id', 0))
            choice_code = decrypt(self.private_key, vote_package.get('encrypted_choice', 0))
            signature_voter = decrypt(self.private_key, vote_package.get('encrypted_sig', 0))

            if not all([rn, voter_id, choice_code, signature_voter]):
                 print("  -> ❌ ПОМИЛКА: Не вдалося розшифрувати всі частини бюлетеня.")
                 return False

            voter_id = str(voter_id)
            rn = int(rn)

        except Exception as e:
            print(f"  -> ❌ ПОМИЛКА: Не вдалося розшифрувати голос. {e}")
            return False

        print(f"📬 ВК отримала та розшифрувала голос (ID: {voter_id}, RN: {rn})")

        if rn not in self.available_rns:
            print(f"  -> ❌ RN '{rn}' не знайдений або вже використаний. Голос відхилено.")
            return False
            
        try:
            choice = CODE_TO_CANDIDATE[choice_code]
        except KeyError:
            print(f"  -> ❌ Некоректний код вибору: {choice_code}. Голос відхилено.")
            return False

        message_to_verify = f"{voter_id}|{rn}|{choice}"
        expected_hash = quadratic_hash(message_to_verify, voter_public_key[1])
        
        hash_from_signature = verify_signature(signature_voter, voter_public_key)
        
        print(f"  -> Очікуваний хеш: {expected_hash}, Отриманий з підпису: {hash_from_signature}")

        if hash_from_signature != expected_hash:
            print("  -> ❌ ЕЦП виборця невалідна. Голос відхилено.")
            return False

        self.available_rns.remove(rn)
        self.successful_voter_ids.add(voter_id)
        self.candidates[choice] += 1
        
        self.published_ballots.append({
            'id': voter_id, 
            'rn': rn, 
            'choice': choice, 
            'signature': signature_voter
        })
        
        print(f"  -> ✅ ГОЛОС ЗАРАХОВАНО. RN '{rn}' викреслено.")
        return True

    def process_and_publish_results(self):
        """ Крок 6: Публікує результати та список бюлетенів. """
        print("\n--- 📊 РЕЗУЛЬТАТИ ГОЛОСУВАННЯ ---")
        for candidate, votes in self.candidates.items():
            print(f"Кандидат '{candidate}': {votes} голосів")
        
        max_votes = max(self.candidates.values())
        winners = [c for c, num in self.candidates.items() if num == max_votes]
        print(f"\n🏆 Переможець: {winners[0]}" if len(winners) == 1 else f"\n🤝 Результат: нічия! {', '.join(winners)}.")
        
        print("\n--- 📜 ОПУБЛІКОВАНІ БЮЛЕТЕНІ (ID та підпис виборця) ---")
        print(f"{'Виборець ID':<18} | {'RN':<10} | {'Вибір':<30} | {'Підпис Виборця (Хеш^d)':<10}")
        print("-" * 75)
        for ballot in self.published_ballots:
            print(f"{str(ballot['id']):<18} | {ballot['rn']:<10} | {ballot['choice']:<30} | {ballot['signature'] % 10000:<10}...")