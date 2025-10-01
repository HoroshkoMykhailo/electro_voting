import random
from electro_voting.hashing import quadratic_hash
from electro_voting.key_generation import generate_rsa_keys
from electro_voting.blind import blind, sign_blinded, unmask_blinded_for_verification, verify_signature
from electro_voting.sign import decrypt
from electro_voting.candidates import CODE_TO_CANDIDATE

class CentralElectionCommission:
    def __init__(self, candidates, voter_ids):
        self.candidates = {candidate: 0 for candidate in candidates}
        self.voter_ids = voter_ids
        self.voters_who_signed = set()
        self.received_uids = set()
        self.published_ballots = []
        self.candidates_list = candidates 

        p, q = 61, 53
        self.public_key, self.private_key = generate_rsa_keys(p, q)
        self.n_cec = self.public_key[1]
        print("🔑 ЦВК згенерувала власну пару ключів.")
        
    def register_voter_for_signing(self, voter_id: str):
        """ Додає новий ID виборця до списку, дозволяючи йому отримати підпис. """
        if voter_id not in self.voter_ids:
            self.voter_ids.append(voter_id)
            print(f"[{voter_id}]: ✅ Зареєстровано нового виборця для тестування.")
        else:
            print(f"[{voter_id}]: ℹ️ Виборець вже був у початковому списку.")

    def receive_ballot_sets_for_signing(self, voter_id: str, blinded_ballot_sets: list, r_values: list, content_sets: list):
        """Кроки 5-7: Приймає, перевіряє (9/10) та підписує (1/10)."""
        if voter_id in self.voters_who_signed:
            print(f"[{voter_id}]: ❌ Вже отримував підпис. Запит проігноровано.")
            return None, None
            
        print(f"[{voter_id}]: 📥 Отримано 10 наборів бюлетенів для підпису.")
        
        NUM_SETS = len(blinded_ballot_sets)
        set_to_sign_index = random.randint(0, NUM_SETS - 1)
        
        set_to_sign = {}
        r_to_sign = 0
        
        for i in range(NUM_SETS):
            r = r_values[i]
            
            revealed_set = {
                'blinded_set': blinded_ballot_sets[i],
                'content_set': content_sets[i],
                'uid': content_sets[i][self.candidates_list[0]].split('|')[0] 
            }
            
            if i == set_to_sign_index:
                set_to_sign = blinded_ballot_sets[i]
                r_to_sign = r
                print(f"[{voter_id}]: ➡️ Набір {i+1} позначено для підпису (не перевіряється).")
            else:
                print(f"[{voter_id}]: 🔎 Перевіряється набір {i+1}...")
                
                is_valid = self._verify_ballot_set(revealed_set, r)
                
                if not is_valid:
                    print(f"[{voter_id}]: ❌ ШАХРАЙСТВО виявлено в наборі {i+1}. Підпис відхилено.")
                    return None, None
                print(f"[{voter_id}]: ✅ Набір {i+1} коректний.")

        signed_set = {}
        for candidate, blinded_hash in set_to_sign.items():
            signed_hash_prime = sign_blinded(blinded_hash, self.private_key)
            signed_set[candidate] = signed_hash_prime
            
        self.voters_who_signed.add(voter_id)
        print(f"[{voter_id}]: ✅ Підписано останній набір. Виборця позначено.")
        
        return signed_set, r_to_sign

    def _verify_ballot_set(self, revealed_set: dict, r: int) -> bool:
        """
        Перевіряє коректність одного розкритого набору бюлетенів (Крок 6).

        revealed_set містить:
        - 'blinded_set': замасковані хеші
        - 'content_set': оригінальний вміст бюлетенів (UID|Кандидат)
        - 'uid': унікальний ID виборця для цього набору
        """
        
        blinded_set = revealed_set['blinded_set']
        content_set = revealed_set['content_set']
        set_uid = revealed_set['uid']
        
        if len(blinded_set) != len(self.candidates_list) or len(content_set) != len(self.candidates_list):
            print("   -> ❌ ПЕРЕВІРКА: Неправильна кількість бюлетенів у наборі.")
            return False 

        candidates_in_set = set(content_set.keys())
        if candidates_in_set != set(self.candidates_list):
            print("   -> ❌ ПЕРЕВІРКА: Набір не містить бюлетенів для всіх кандидатів.")
            return False

        for candidate, blinded_hash in blinded_set.items():
            expected_content = f"{set_uid}|{candidate}"
            
            if content_set.get(candidate) != expected_content:
                 print(f"   -> ❌ ПЕРЕВІРКА: Розкритий вміст для '{candidate}' не відповідає очікуваному.")
                 return False

            expected_hash = quadratic_hash(expected_content, self.n_cec)

            try:
                unmasked_hash = unmask_blinded_for_verification(blinded_hash, self.public_key, r)
            except Exception as e:
                print(f"   -> ❌ ПЕРЕВІРКА: Помилка зняття маскування: {e}.")
                return False

            if unmasked_hash != expected_hash:
                print(f"   -> ❌ ПЕРЕВІРКА: Хеш після зняття маскування не відповідає очікуваному для '{candidate}'.")
                print(f"      -> Очікуваний: {expected_hash}, Отриманий після розмаскування: {unmasked_hash}")
                return False
                    
            return True

    def receive_vote(self, vote_package: dict):
        """
        Крок 10-11: Приймає зашифрований голос, розшифровує обидві частини та обробляє.
        """
        uid = vote_package['uid']
        encrypted_choice = vote_package['encrypted_choice']
        encrypted_signature = vote_package['encrypted_signature']
        
        print(f"📬 ЦВК отримала голос (UID: {uid}, Заш.Вибір: {encrypted_choice}, Заш.Підпис: {encrypted_signature})")
        
        signature = decrypt(self.private_key, encrypted_signature)
        print(f"  -> Розшифровано підпис ЦВК: {signature}")

        choice_code = decrypt(self.private_key, encrypted_choice)
        
        try:
            choice = CODE_TO_CANDIDATE[choice_code] 
            print(f"  -> Розшифровано вибір: '{choice}' (Код: {choice_code})")
        except KeyError:
             print(f"  -> ❌ ПОМИЛКА: Некоректний код вибору: {choice_code}. Голос відхилено.")
             return

        if uid in self.received_uids:
            print(f"  -> ❌ ПОВТОРНЕ ГОЛОСУВАННЯ: UID '{uid}' вже зареєстрований. Голос відхилено.")
            return

        hash_from_signature = verify_signature(signature, self.public_key)
        print(f"  -> З підпису отримано хеш: {hash_from_signature}")

        message = f"{uid}|{choice}"
        expected_hash = quadratic_hash(message, self.n_cec)
        print(f"  -> Очікуваний хеш для '{choice}': {expected_hash}")
        
        if hash_from_signature == expected_hash:
            print(f"  -> ✅ ПІДПИС ВАЛІДНИЙ. Голос зараховано.")
            self.candidates[choice] += 1
            self.received_uids.add(uid)
            # Крок 12: Зберігаємо для публікації
            self.published_ballots.append({'uid': uid, 'choice': choice, 'signature': signature})
        else:
            print(f"  -> ❌ ПІДПИС НЕВАЛІДНИЙ. Голос відхилено.")
            
        print("-" * 20)


    def process_and_publish_results(self):
        """
        Крок 12: Обробляє голоси та публікує результати.
        """
        print("\n--- 📊 РЕЗУЛЬТАТИ ГОЛОСУВАННЯ ---")
        for candidate, votes in self.candidates.items():
            print(f"Кандидат '{candidate}': {votes} голосів")
        
        max_votes = max(self.candidates.values())
        winners = [candidate for candidate, num_votes in self.candidates.items() if num_votes == max_votes]
        if len(winners) > 1:
             print(f"\n🤝 Результат: нічия! Кандидати '{', '.join(winners)}'.")
        else:
            print(f"\n🏆 Переможець: {winners[0]}")
            
        print("\n--- 📜 ОПУБЛІКОВАНІ БЮЛЕТЕНІ (для перевірки) ---")
        print(f"{'UID':<18} | {'Вибір':<30} | {'Підпис ЦВК (Хеш^d)':<10}")
        print("-" * 65)
        for ballot in self.published_ballots:
            print(f"{str(ballot['uid']):<18} | {ballot['choice']:<30} | {ballot['signature'] % 10000:<10}...")