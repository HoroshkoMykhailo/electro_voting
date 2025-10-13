import random
from electro_voting.RegistrationBureau import RegistrationBureau
from electro_voting.CEC import CEC
from electro_voting.MediumLevelCommission import MediumLevelCommission
from electro_voting.LowLevelCommission import LowLevelCommission
from electro_voting.Voter import Voter

from electro_voting.key_generation import is_prime, mod_inverse
from electro_voting.candidates import CANDIDATES
from electro_voting.encrypt import sign, encrypt, verify_signature
from electro_voting.hashing import int_hash

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

def run_tests():
    """
    Запускає набір тестів для перевірки стійкості системи до типових атак.
    """
    print("\n" + "="*50)
    print("🚀🚀🚀 ПОЧАТОК ТЕСТУВАННЯ АЛГОРИТМУ 🚀🚀🚀")
    print("="*50)

    print("\n--- [Етап 0]: Ініціалізація тестового середовища ---\n")
    primes_test = [p for p in range(8000, 12000) if is_prime(p)]
    p_test, q_test = random.sample(primes_test, 2)

    TEST_VOTER_NAMES = ["Тестовий-Виборець-A", "Тестовий-Виборець-B", "Тестовий-Виборець-C"]
    
    rb_test = RegistrationBureau(TEST_VOTER_NAMES)
    voter_tokens_test = rb_test.verify_and_issue_tokens()
    voter_list_test, token_db_test = rb_test.get_databases()

    cec_test = CEC(p_test, q_test, token_db_test)
    vcs_test = MediumLevelCommission("Тест-ВКС-1", p_test, q_test)
    vkn1_test = LowLevelCommission("Тест-ВКН-1", vcs_test)
    vkn2_test = LowLevelCommission("Тест-ВКН-2", vcs_test)
    
    cec_test.jurisdictions[vcs_test.name] = voter_list_test
    
    voters_test = {}
    for i, name in enumerate(TEST_VOTER_NAMES, start=100): 
        voters_test[name] = Voter(name, p_test, q_test, voter_tokens_test[name], ballot_id=i)
    
    for voter in voters_test.values():
        voter.get_blind_signature(cec_test)
    
    print("\n--- ✅ Тестове середовище успішно налаштовано. ---\n")

    print("\n--- [Тест А]: Спроба отримати другий сліпий підпис з тим самим токеном ---\n")
    test_voter_A = voters_test["Тестовий-Виборець-A"]
    print(f"👤 {test_voter_A.name} намагається повторно використати свій токен для отримання ще одного підпису від ЦВК.")
    
    try:
        test_voter_A.get_blind_signature(cec_test)
    except PermissionError as e:
        print(f"✅ УСПІХ: ЦВК коректно відхилила запит з помилкою: '{e}'")
    except Exception as e:
        print(f"❌ ПОМИЛКА: Очікувалася помилка PermissionError, але виникла інша: {type(e).__name__}")

    print("\n--- [Тест B]: Спроба подати частину бюлетеня з невалідним ЕЦП виборця ---\n")
    test_voter_B = voters_test["Тестовий-Виборець-B"]
    vote = CANDIDATES["Петро Порошенко"]
    
    ballot_int = test_voter_B.ballot_id * 10 + vote
    c = encrypt(vcs_test.public_key, ballot_int)
    n_vcs = vcs_test.public_key[1]
    _, n_cec = cec_test.public_key
    r1 = random.randint(2, n_vcs - 1)
    r2 = (c * mod_inverse(r1, n_vcs)) % n_vcs
    t1 = random.randint(2, n_cec - 1)
    t2 = (test_voter_B.cec_signature * mod_inverse(t1, n_cec)) % n_cec
    part1, part2 = (r1, t1), (r2, t2)

    valid_sig1 = sign(test_voter_B.private_key, int_hash(part1, test_voter_B.public_key[1]))
    invalid_sig1 = valid_sig1 + 10 
    
    print(f"👤 {test_voter_B.name} надсилає частину 1 до {vkn1_test.name} з пошкодженим ЕЦП.")
    
    try:
        vkn1_test.receive_part(test_voter_B.public_key, test_voter_B.name, part1, invalid_sig1, 1)
    except ValueError as e:
        print(f"✅ УСПІХ: {vkn1_test.name} коректно відхилила частину бюлетеня з помилкою: '{e}'")
    except Exception as e:
        print(f"❌ ПОМИЛКА: Очікувалася помилка ValueError, але виникла інша: {type(e).__name__}")

    print("\n--- [Тест C]: Спроба зібрати бюлетень з невалідним підписом ЦВК ---\n")
    test_voter_C = voters_test["Тестовий-Виборець-C"]
    
    print(f"🧩 {vcs_test.name} намагається зібрати бюлетень для {test_voter_C.name}, але ми симулюємо, що сліпий підпис s було підроблено.")
    
    s_valid = test_voter_C.cec_signature
    s_invalid = s_valid + 10 
    ballot_hash = int_hash(test_voter_C.ballot_id, n_cec)

    is_valid_ok = verify_signature(cec_test.public_key, s_valid, ballot_hash)
    is_invalid_rejected = not verify_signature(cec_test.public_key, s_invalid, ballot_hash)

    print(f"Перевірка оригінального (правильного) підпису ЦВК... Результат: {'Успіх' if is_valid_ok else 'Провал'}")
    print(f"Перевірка підробленого підпису ЦВК... Результат: {'Відхилено' if is_invalid_rejected else 'Прийнято'}")

    if is_valid_ok and is_invalid_rejected:
        print(f"✅ УСПІХ: Механізм перевірки підпису ЦВК на рівні ВКС працює коректно.")
    else:
        print(f"❌ ПОМИЛКА: Механізм перевірки підпису ЦВК не спрацював, як очікувалося.")

    print("\n" + "="*50)
    print("🏁🏁🏁 ТЕСТУВАННЯ АЛГОРИТМУ ЗАВЕРШЕНО 🏁🏁🏁")
    print("="*50)


run_tests()