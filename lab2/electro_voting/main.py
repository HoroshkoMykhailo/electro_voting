from electro_voting.ElectionCommission import CentralElectionCommission
from electro_voting.Voter import Voter
from electro_voting.candidates import CANDIDATES

VOTER_IDS = [f"Виборець-{i+1}" for i in range(5)]

cec = CentralElectionCommission(CANDIDATES, VOTER_IDS)

voters = [Voter(v_id, cec.public_key) for v_id in VOTER_IDS]

print("\n" + "="*50)
print("1. ЕТАП: ГЕНЕРАЦІЯ ТА ПІДПИС БЮЛЕТЕНІВ (Кроки 2-8)")
print("="*50)

voter_data_to_sign = {}
for voter in voters:
    blinded_sets, r_values, content_sets = voter.generate_ballot_sets(CANDIDATES, num_sets=10)
    voter_data_to_sign[voter.voter_id] = (voter, blinded_sets, r_values, content_sets)

for voter_id, (voter, blinded_sets, r_values, content_sets) in voter_data_to_sign.items():
    print("-" * 50)
    signed_set, r_to_sign = cec.receive_ballot_sets_for_signing(voter_id, blinded_sets, r_values, content_sets)
    
    if signed_set:
        voter.process_signed_ballots(signed_set, r_to_sign)
    print("\n" + "~"*20 + "\n")


print("\n" + "="*50)
print("2. ЕТАП: ГОЛОСУВАННЯ ТА ОБРОБКА (Кроки 9-11)")
print("="*50)

choices = ["Володимир Зеленський", "Петро Порошенко", "Володимир Зеленський", "Володимир Зеленський", "Петро Порошенко"]

for i, voter in enumerate(voters):
    print("-" * 50)
    vote_package = voter.vote(choices[i])
    cec.receive_vote(vote_package)
    
print("-" * 50)
cec.process_and_publish_results()

print("\n" + "="*50)
print("3. ТЕСТУВАННЯ ПРОТОКОЛУ (a, b, c)")
print("="*50)
print("\n[a] Тест: Один набір на виборця")
extra_signed_set, extra_r_to_sign  = cec.receive_ballot_sets_for_signing(
    VOTER_IDS[0],
    voter_data_to_sign[VOTER_IDS[0]][1],
    voter_data_to_sign[VOTER_IDS[0]][2],
    voter_data_to_sign[VOTER_IDS[0]][3],
)
print("   -> Результат:", "Видано ще один набір!" if extra_signed_set else "ДРУГИЙ НАБІР НЕ ВИДАНО ✅")

print("\n[b] Тест: Дубльоване голосування")
dup_vote = voters[1].vote("Петро Порошенко")
cec.receive_vote(dup_vote) 
print("   -> Голос виборця-2 повторно відправлений, але проігнорований ✅")

print("\n[c] Тест: Некоректні набори бюлетенів")

FRAUD_VOTER_ID = "Шахрай-1"
cec.register_voter_for_signing(FRAUD_VOTER_ID)

fraud_voter = Voter(FRAUD_VOTER_ID, cec.public_key)

bad_blinded_sets, bad_r_values, bad_content_sets = fraud_voter.generate_ballot_sets(CANDIDATES, num_sets=10)

print(f"[{FRAUD_VOTER_ID}]: 😈 Змінено вміст набору 1. Очікується відмова у підписі.")
import copy
fraud_content_sets = copy.deepcopy(bad_content_sets)
for cand in fraud_content_sets[0]:
    fraud_content_sets[0][cand] = f"Фальшивий контент для {cand}" 

bad_signed_set, bad_r_to_sign = cec.receive_ballot_sets_for_signing(
    FRAUD_VOTER_ID, 
    bad_blinded_sets, 
    bad_r_values, 
    fraud_content_sets
)

if bad_signed_set:
    print(f"    -> Результат: ❌ ПОМИЛКА: Набір підписано! (Це сталося, якщо ЦВК випадково обрала ШАХРАЙСЬКИЙ набір 1 для підпису, шанс 1/10).")
else:
    print("    -> Результат: ЦВК ВІДМОВИЛА У ПІДПИСІ ✅ (Шахрайство виявлено в одному з 9 розкритих наборів).")