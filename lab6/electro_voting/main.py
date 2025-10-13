import random
from electro_voting.RegistrationBureau import RegistrationBureau
from electro_voting.CEC import CEC
from electro_voting.MediumLevelCommission import MediumLevelCommission
from electro_voting.LowLevelCommission import LowLevelCommission
from electro_voting.Voter import Voter

from electro_voting.key_generation import is_prime
from electro_voting.candidates import CANDIDATES

print("--- 1. ПІДГОТОВЧИЙ ЕТАП ---\n")
primes = [p for p in range(3000, 8000) if is_prime(p)]
p, q = random.sample(primes, 2)

VOTER_NAMES = ["Виборець-1", "Виборець-2", "Виборець-3", "Виборець-4", "Виборець-5", "Виборець-6"]
VOTES = [CANDIDATES["Володимир Зеленський"], CANDIDATES["Петро Порошенко"], CANDIDATES["Володимир Зеленський"], 
         CANDIDATES["Володимир Зеленський"], CANDIDATES["Петро Порошенко"], CANDIDATES["Володимир Зеленський"]]

rb = RegistrationBureau(VOTER_NAMES)
voter_tokens = rb.verify_and_issue_tokens()
voter_list, token_db = rb.get_databases()

cec = CEC(p, q, token_db)
vcs1 = MediumLevelCommission("ВКС-1", p, q)
vcs2 = MediumLevelCommission("ВКС-2", p, q)
cec.set_jurisdictions(voter_list, vcs1.name, vcs2.name)

vkn1 = LowLevelCommission("ВКН-1", vcs1)
vkn2 = LowLevelCommission("ВКН-2", vcs1)
vkn3 = LowLevelCommission("ВКН-3", vcs2)
vkn4 = LowLevelCommission("ВКН-4", vcs2)

voters = {}
for i, name in enumerate(VOTER_NAMES, start=1):
    voters[name] = Voter(name, p, q, voter_tokens[name], ballot_id=i)

print("\n--- 2. ЕТАП АВТОРИЗАЦІЇ (СЛІПИЙ ПІДПИС) ---\n")
for voter in voters.values():
    voter.get_blind_signature(cec)

print("\n--- 3. ЕТАП ГОЛОСУВАННЯ ---\n")
for i, name in enumerate(VOTER_NAMES):
    voter = voters[name]
    vote = VOTES[i]
    if name in cec.jurisdictions[vcs1.name]:
        voter.create_and_cast_vote(vote, cec.public_key, vcs1.public_key, vkn1, vkn2)
    else:
        voter.create_and_cast_vote(vote, cec.public_key, vcs2.public_key, vkn3, vkn4)

print("\n--- 4. ЕТАП ПІДРАХУНКУ ---\n")
vkn1.send_to_vcs(1); vkn2.send_to_vcs(2)
vkn3.send_to_vcs(1); vkn4.send_to_vcs(2)

vcs1.assemble_and_verify(cec.public_key, voters)
vcs2.assemble_and_verify(cec.public_key, voters)

vcs1.decrypt_votes()
vcs2.decrypt_votes()

results1, ids1 = vcs1.count_votes()
results2, ids2 = vcs2.count_votes()

print("\n--- 5. ФІНАЛІЗАЦІЯ В ЦВК ---\n")
final_tally = results1 + results2
all_counted_ids = ids1.union(ids2)
cec.publish_results(final_tally, all_counted_ids)