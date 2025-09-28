from electro_voting.ElectionCommission import CentralElectionCommission
from electro_voting.Voter import Voter
from electro_voting.key_generation import generate_rsa_keys

CANDIDATES = ["Петро Порошенко", "Володимир Зеленський"]
VOTER_IDS = [f"Виборець-{i+1}" for i in range(5)]

cec = CentralElectionCommission(CANDIDATES, VOTER_IDS)
cec.generate_voter_keys()

voters = [Voter(v_id, cec.get_voter_private_key(v_id)) for v_id in VOTER_IDS]
    
print("\n--- ELECTION: Починається процес голосування ---\n")

choices = ["Володимир Зеленський", "Петро Порошенко", "Володимир Зеленський", "Володими Зеленський", "Петро Порошенко"]

for i, voter in enumerate(voters):
    ballot_package = voter.create_ballot(choices[i])
    cec.receive_ballot(voter.voter_id, ballot_package)
    print(f"===> Бюлетень від {voter.voter_id} надіслано до ЦВК.\n")

# --- a. Тест на повторне голосування ---
print("\n--- Тест А: Виборець-1 намагається проголосувати вдруге ---")
voter1_ballot = voters[0].create_ballot("Петро Порошенко")
cec.receive_ballot(voters[0].voter_id, voter1_ballot)

# --- b. Тест на голосування незареєстрованого виборця ---
print("\n--- Тест B: Незареєстрований виборець намагається проголосувати ---")
unregistered_voter_id = "Незареєстрований-Виборець"
p_unregistered, q_unregistered = 151, 157
unregistered_pub_key, unregistered_priv_key = generate_rsa_keys(p_unregistered, q_unregistered)
unregistered_voter = Voter(unregistered_voter_id, unregistered_priv_key)
unregistered_ballot = unregistered_voter.create_ballot("Володимир Зеленський")
cec.receive_ballot(unregistered_voter.voter_id, unregistered_ballot)

cec.process_ballots()
cec.publish_results()