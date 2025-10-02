from electro_voting.ElectionCommittee import ElectionCommittee
from electro_voting.RegistrationBureau import RegistrationBureau
from electro_voting.Voter import Voter
from electro_voting.candidates import CANDIDATES

VOTER_IDS = [f"Виборець-{i+1}" for i in range(5)]

rb = RegistrationBureau()
ec = ElectionCommittee(CANDIDATES)

voters = [Voter(v_id, ec.public_key) for v_id in VOTER_IDS]

print("\n" + "="*50)
print("1. ЕТАП: РЕЄСТРАЦІЯ У БР (Кроки 1-3)")
print("="*50)

for voter in voters:
    voter.register_with_rb(rb)

rns_to_ec = rb.send_rns_to_ec()
ec.receive_rns_from_rb(rns_to_ec)

print("\n" + "="*50)
print("2. ЕТАП: ГОЛОСУВАННЯ ТА ОБРОБКА (Кроки 4-5)")
print("="*50)

choices = ["Володимир Зеленський", "Петро Порошенко", "Володимир Зеленський", "Володимир Зеленський", "Петро Порошенко"]

for i, voter in enumerate(voters):
    print("-" * 50)
    vote_package, voter_pub_key = voter.vote(choices[i]) 
    ec.receive_vote_package(vote_package, voter_pub_key) 
    
print("-" * 50)
ec.process_and_publish_results()

print("\n[a] Тест: Повторне отримання RN від БР")
voter_1 = voters[0]
first_rn = voter_1.registration_number
print(f"[{voter_1.voter_id}]: Спроба отримати RN вдруге...")

voter_1.register_with_rb(rb) 

second_rn = voter_1.registration_number
print(f"   -> Результат: Перший RN: {first_rn}, Другий RN: {second_rn}")

if second_rn == first_rn:
    print("   -> Виборець не може отримати більше одного RN ✅")
else:
    print("   -> ❌ ПОМИЛКА: Виборець отримав новий RN.")

print("\n[b] Тест: Спроба проголосувати двічі")
voter_2 = voters[1]
choice = "Петро Порошенко"

print(f"[{voter_2.voter_id}]: Спроба проголосувати повторно...")
vote_package2, voter_pub_key2 = voter_2.vote(choice)
ec.receive_vote_package(vote_package2, voter_pub_key2)

print("\n[Тест невалідного RN]")
fake_vote = vote_package.copy()
fake_vote['encrypted_rn'] = ec.public_key[1] - 1
ec.receive_vote_package(fake_vote, voter_pub_key)

print("\n[c] Тест: Перевірка виборцями своїх голосів")
for i, voter in enumerate(voters):
    voter.verify_vote(ec.published_ballots, choices[i])