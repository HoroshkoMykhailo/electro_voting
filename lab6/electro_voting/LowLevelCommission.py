from electro_voting.encrypt import verify_signature
from electro_voting.hashing import int_hash

class LowLevelCommission:
    """Виборча Комісія Низького Рівня: збирає та верифікує частини бюлетенів."""
    def __init__(self, name: str, parent_vcs):
        self.name = name
        self.parent_vcs = parent_vcs
        self.collected_parts = {}
        print(f"🏠 Створено ВКН: {self.name} (для {parent_vcs.name})")

    def receive_part(self, voter_pk: tuple, voter_name: str, part: tuple, signature: int, part_type: int):
        """Отримує частину бюлетеня та перевіряє підпис виборця."""
        part_hash = int_hash(part, voter_pk[1])

        if verify_signature(voter_pk, signature, part_hash):
            self.collected_parts[voter_name] = part
            print(f"📥 {self.name}: Отримано та верифіковано частину {part_type} від {voter_name}.")
        else:
            raise ValueError(f"🔥 УВАГА: Невалідний підпис від виборця {voter_name} на {self.name}!")

    def send_to_vcs(self, part_type: int):
        """Надсилає зібрані частини до своєї ВКС."""
        self.parent_vcs.receive_parts(self.collected_parts, part_type)
        print(f"📤 {self.name}: Передано {len(self.collected_parts)} частин до {self.parent_vcs.name}.")