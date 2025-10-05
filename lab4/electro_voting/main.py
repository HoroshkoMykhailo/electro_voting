from electro_voting.ElectionCommittee import ElectionCommittee
from electro_voting.Voter import Voter
from electro_voting.CentralElectionCommittee import CentralElectionCommittee

print("="*50)
print("1. ЕТАП: ПІДГОТОВКА ДО ГОЛОСУВАННЯ")
print("="*50)

CANDIDATES = {"Петро Порошенко": 15, "Володимир Зеленський": 14}
VOTER_NAMES = [f"Громадянин-{i+1}" for i in range(5)]

cec = CentralElectionCommittee(CANDIDATES, VOTER_NAMES)
ec1 = ElectionCommittee("ВК-1")
ec2 = ElectionCommittee("ВК-2")

voters = [Voter(name, cec.public_key) for name in VOTER_NAMES]

cec.distribute_voters(ec1, ec2)

print("\n" + "="*50)
print("2. ЕТАП: ГОЛОСУВАННЯ (Кроки 2-4)")
print("="*50)

choices = [
    CANDIDATES["Володимир Зеленський"],
    CANDIDATES["Петро Порошенко"],
    CANDIDATES["Володимир Зеленський"],
    CANDIDATES["Володимир Зеленський"],
    CANDIDATES["Петро Порошенко"]
]
ballots_for_test = []

for i, voter in enumerate(voters):
    print("-" * 40)
    candidate_id_choice = choices[i]
    
    ballot1, ballot2 = voter.create_ballots(candidate_id_choice)
    
    ec1.receive_ballot(ballot1)
    ec2.receive_ballot(ballot2)
    if i == 0: ballots_for_test = [ballot1, ballot2]


print("\n" + "="*50)
print("3. ЕТАП: ПУБЛІКАЦІЯ ДАНИХ ТА ПІДРАХУНОК (Кроки 5-6)")
print("="*50)

published_data_ec1 = ec1.publish_data()
published_data_ec2 = ec2.publish_data()

final_vote_counts = cec.tally_votes(published_data_ec1, published_data_ec2)
cec.publish_final_results(final_vote_counts)

print("\n" + "="*50)
print("4. ЕТАП: ПЕРЕВІРКА РЕЗУЛЬТАТІВ ВИБОРЦЯМИ")
print("="*50)

for i, voter in enumerate(voters):
    voter.verify_final_vote(cec.final_results, choices[i])

print("\n--- [Тест А]: Спроба подати бюлетень з невалідним ЕЦП ---\n")
invalid_ballot = ballots_for_test[0].copy()
original_signature = invalid_ballot['signature']
invalid_ballot['signature'] = original_signature + 1 
print(f"Надсилаємо до ВК-1 бюлетень від '{invalid_ballot['voter_name']}' зі зміненим підписом...")
ec1.receive_ballot(invalid_ballot)

print("\n--- [Тест B]: Симуляція підміни частини бюлетеня з боку ВК-1 ---\n")
tampered_published_data_ec1 = [b.copy() for b in published_data_ec1]
original_part = tampered_published_data_ec1[0]['encrypted_part']
tampered_published_data_ec1[0]['encrypted_part'] = 1234 
print("ВК-1 опублікувала дані, але таємно змінила одну із зашифрованих частин.")
print(f"Оригінальна частина: {original_part} -> Змінена частина: 1234")
print("\nЦВК починає підрахунок з підробленими даними від ВК-1...")
cec_test = CentralElectionCommittee(CANDIDATES, VOTER_NAMES)
final_vote_counts =cec_test.tally_votes(tampered_published_data_ec1, published_data_ec2)
cec_test.publish_final_results(final_vote_counts)