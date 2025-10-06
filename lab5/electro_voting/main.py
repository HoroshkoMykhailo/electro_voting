from collections import Counter
import random
from electro_voting.Voter import Voter
from electro_voting.key_generation import generate_common_modulus_and_keys
from electro_voting.hashing import int_hash
from electro_voting.encrypt import verify_signature

SIMULATE_SUBSTITUTION_ATTACK = False
SIMULATE_DELETION_ATTACK = False

NUM_VOTERS = 5
VOTER_NAMES = ["A", "B", "C", "D", "E"]
CANDIDATES = {"Петро Порошенко": 15, "Володимир Зеленський": 14}
RP_BITS = 8

votes = [
    CANDIDATES["Володимир Зеленський"],
    CANDIDATES["Петро Порошенко"],
    CANDIDATES["Володимир Зеленський"],
    CANDIDATES["Володимир Зеленський"],
    CANDIDATES["Петро Порошенко"]
]

(p, q, n, phi), keypairs = generate_common_modulus_and_keys(NUM_VOTERS)
print(f"Згенерували загальний модуль n={n} (p={p}, q={q})\n")

voters = [Voter(name, keypairs[i], rp_bits=RP_BITS) for i, name in enumerate(VOTER_NAMES)]

print("\n--- Створення зашифрованих бюлетенів ---")
encrypted_ballots = []
for i, voter in enumerate(voters):
    ballot = voter.create_ballot(votes[i], voters)
    encrypted_ballots.append(ballot)
    print(f"  {voter.name} сформував зашифрований бюлетень.")

print("\n--- Раунд розшифрування і змішування ---")
current_list = encrypted_ballots
last_signature = None
for i, current_voter in enumerate(voters):
    if i > 0:
        prev = voters[i-1]
        list_tuple = tuple(sorted(current_list))
        data_hash = int_hash(list_tuple, prev.public_key[1])
        if not verify_signature(prev.public_key, last_signature, data_hash):
            raise Exception(f"!!! ✅ ВИКРИТТЯ: Невалідний підпис від {prev.name}. Список було змінено!")
        else:
            print(f"  ✅ Підпис від {prev.name} перевірено.")

    current_list, last_signature = current_voter.mix_and_decrypt_step(current_list)

    if SIMULATE_SUBSTITUTION_ATTACK and current_voter.name == "C":
        print("\n  >>> 😈 АТАКА: Виборець C таємно підміняє один бюлетень! <<<\n")
        current_list[0] = random.randint(1, n) 
    
    if SIMULATE_DELETION_ATTACK and current_voter.name == "C":
        print("\n  >>> 😈 АТАКА: Виборець C таємно видаляє один бюлетень! <<<\n")
        current_list.pop()


prev = voters[-1]
list_tuple = tuple(sorted(current_list))
data_hash = int_hash(list_tuple, prev.public_key[1])
if not verify_signature(prev.public_key, last_signature, data_hash):
    raise Exception(f"!!! ✅ ВИКРИТТЯ: Невалідний підпис від {prev.name} в кінці раунду. Список було змінено!")
else:
    print(f"  ✅ Фінальний підпис від {prev.name} перевірено.")


print("\n--- Видалення маркерів (Раунд 1: зняття зовнішнього шару rp2) ---")
list_after_round1 = []
for voter in voters:
    unwrapped_ballot = voter.find_and_unwrap_ballot(current_list, round_num=1)
    list_after_round1.append(unwrapped_ballot)

print("\n--- Видалення маркерів (Раунд 2: зняття внутрішнього шару rp1) ---")
final_decrypted_votes = []
for voter in voters:
    vote = voter.find_and_unwrap_ballot(list_after_round1, round_num=2)
    final_decrypted_votes.append(vote)


print("\n--- Підрахунок голосів ---")
print("Остаточний список розшифрованих бюлетенів:", sorted(final_decrypted_votes))
vote_counts = Counter(final_decrypted_votes)
id_to_candidate = {v: k for k, v in CANDIDATES.items()}

print("\n--- РЕЗУЛЬТАТИ ---")
for cid, cnt in vote_counts.items():
    print(f"{id_to_candidate.get(cid, 'Невідомий')}: {cnt} голос(ів)")

print("\n--- ПЕРЕВІРКА ---")
original_counts = Counter(votes)
if original_counts == vote_counts:
    print("✅ Успіх — результати збігаються з початковими голосами.")
else:
    print("❌ Помилка — результати не збігаються.")
    print("Очікувалось:", dict(original_counts))
    print("Отримано:", dict(vote_counts))