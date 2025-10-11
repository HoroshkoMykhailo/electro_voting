from collections import Counter
import random
from electro_voting.Voter import Voter
from electro_voting.key_generation import generate_common_modulus_and_keys
from electro_voting.hashing import int_hash
from electro_voting.encrypt import verify_signature

SIMULATE_SUBSTITUTION_ATTACK = False
SIMULATE_DELETION_ATTACK = True

NUM_VOTERS = 5
VOTER_NAMES = ["A", "B", "C", "D", "E"]
CANDIDATES = {"Петро Порошенко": 1, "Володимир Зеленський": 2}

votes = [
    CANDIDATES["Володимир Зеленський"],
    CANDIDATES["Петро Порошенко"],
    CANDIDATES["Володимир Зеленський"],
    CANDIDATES["Володимир Зеленський"],
    CANDIDATES["Петро Порошенко"]
]

(p, q, n, phi), keypairs = generate_common_modulus_and_keys(NUM_VOTERS)
print(f"Згенерували загальний модуль n={n} (p={p}, q={q})\n")

voters = [Voter(name, keypairs[i]) for i, name in enumerate(VOTER_NAMES)]

print("\n--- Створення зашифрованих бюлетенів ---")
encrypted_ballots = []
for i, voter in enumerate(voters):
    ballot = voter.create_ballot(votes[i], voters)
    encrypted_ballots.append(ballot)
    print(f"  {voter.name} сформував зашифрований бюлетень.")

print("\n--- Раунд 1: розшифрування та видалення RP2 ---")
current_list = encrypted_ballots
last_signature = None

for i, voter in enumerate(voters):
    if i > 0:
        prev = voters[i-1]
        list_tuple = tuple(sorted(current_list))
        data_hash = int_hash(list_tuple, prev.public_key[1])
        if not verify_signature(prev.public_key, last_signature, data_hash):
            raise Exception(f"!!! ВИКРИТТЯ: Невалідний підпис від {prev.name}. Список було змінено!")
        else:
            print(f"  ✅ Підпис від {prev.name} перевірено.")
    current_list, last_signature = voter.mix_and_decrypt_step(current_list, round_num=1)

    if SIMULATE_SUBSTITUTION_ATTACK and voter.name == "C":
        print("\n  >>> 😈 АТАКА: Виборець C таємно підміняє один бюлетень! <<<\n")
        current_list[0] = random.randint(1, n) 

    if SIMULATE_DELETION_ATTACK and voter.name == "C":
        print("\n  >>> 😈 АТАКА: Виборець C таємно видаляє один бюлетень! <<<\n")
        current_list.pop()

prev = voters[-1]
list_tuple = tuple(sorted(current_list))
data_hash = int_hash(list_tuple, prev.public_key[1])
if not verify_signature(prev.public_key, last_signature, data_hash):
    raise Exception(f"!!! ВИКРИТТЯ: Невалідний підпис від {prev.name} після раунду 1!")
else:
    print(f"  ✅ Фінальний підпис від {prev.name} перевірено після раунду 1.")

print("\n--- Раунд 2: розшифрування та видалення RP1 ---")
for i, voter in enumerate(voters):
    if i > 0:
        prev = voters[i-1]
        list_tuple = tuple(sorted(current_list))
        data_hash = int_hash(list_tuple, prev.public_key[1])
        if not verify_signature(prev.public_key, last_signature, data_hash):
            raise Exception(f"!!! ВИКРИТТЯ: Невалідний підпис від {prev.name}. Список було змінено!")
        else:
            print(f"  ✅ Підпис від {prev.name} перевірено.")

    current_list, last_signature = voter.mix_and_decrypt_step(current_list, round_num=2)

prev = voters[-1]
list_tuple = tuple(sorted(current_list))
data_hash = int_hash(list_tuple, prev.public_key[1])
if not verify_signature(prev.public_key, last_signature, data_hash):
    raise Exception(f"!!! ВИКРИТТЯ: Невалідний підпис від {prev.name} після раунду 2!")
else:
    print(f"  ✅ Фінальний підпис від {prev.name} перевірено після раунду 2.")

print("\n--- Підрахунок голосів ---")
final_decrypted_votes = current_list
vote_counts = Counter(final_decrypted_votes)
id_to_candidate = {v: k for k, v in CANDIDATES.items()}

print("\n--- РЕЗУЛЬТАТИ ---")
for cid, cnt in vote_counts.items():
    print(f"{id_to_candidate.get(cid, 'Невідомий')}: {cnt} голос(ів)")

original_counts = Counter(votes)
if original_counts == vote_counts:
    print("✅ Успіх — результати збігаються з початковими голосами.")
else:
    print("❌ Помилка — результати не збігаються.")
    print("Очікувалось:", dict(original_counts))
    print("Отримано:", dict(vote_counts))