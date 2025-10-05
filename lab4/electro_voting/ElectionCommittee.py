from electro_voting.key_generation import verify_signature

class ElectionCommittee:
    def __init__(self, name):
        self.name = name
        self.voter_list = set()
        self.received_ballots = []
        print(f"🏢 Створено Виборчу Комісію '{self.name}'.")

    def set_voter_list(self, voters):
        """Отримує свою частину списку виборців від ЦВК."""
        self.voter_list = set(voters)
        print(f"[{self.name}]: Отримала список з {len(self.voter_list)} виборців.")

    def receive_ballot(self, ballot):
        """Крок 4: Отримує бюлетень, перевіряє виборця та ЕЦП."""
        voter_name = ballot['voter_name']
        
        if voter_name not in self.voter_list:
            print(f"[{self.name}]: ❌ '{voter_name}' не знайдений у моєму списку. Бюлетень відхилено.")
            return

        is_valid = verify_signature(
            ballot['voter_public_key'], 
            ballot['signature'], 
            ballot['encrypted_part']
        )
        
        if not is_valid:
            print(f"[{self.name}]: ❌ ЕЦП для '{voter_name}' невалідний. Бюлетень відхилено.")
            return
            
        print(f"[{self.name}]: ✅ Отримано валідний бюлетень від '{voter_name}'.")
        self.received_ballots.append({
            'anonymous_id': ballot['anonymous_id'],
            'encrypted_part': ballot['encrypted_part']
        })

    def publish_data(self):
        """Крок 5: Публікує всі отримані анонімні зашифровані бюлетені."""
        print(f"\n📢 [{self.name}] Публікує отримані дані:")
        for ballot in self.received_ballots:
            print(f"  - ID: {ballot['anonymous_id']}, Зашифрована частина: {ballot['encrypted_part']}")
        return self.received_ballots