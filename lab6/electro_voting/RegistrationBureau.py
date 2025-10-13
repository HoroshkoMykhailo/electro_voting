import uuid

class RegistrationBureau:
    """Керує реєстрацією виборців та видачею одноразових токенів."""
    def __init__(self, voter_names: list):
        self.voter_names = voter_names
        self.voter_tokens = {}
        self.token_database = set()
        print("🏛️  Бюро Реєстрації створено.")

    def verify_and_issue_tokens(self) -> dict:
        """Симулює верифікацію та генерує токени для кожного виборця."""
        print("🔎 Бюро Реєстрації: Верифікація виборців та видача токенів...")
        for name in self.voter_names:
            token = str(uuid.uuid4())
            self.voter_tokens[name] = token
            self.token_database.add(token)
        print(f"✅ Успішно видано {len(self.voter_tokens)} токенів.")
        return self.voter_tokens

    def get_databases(self) -> tuple[list, set]:
        """Повертає список виборців та базу даних валідних токенів для ЦВК."""
        return list(self.voter_tokens.keys()), self.token_database