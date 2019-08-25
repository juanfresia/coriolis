import unittest

from verifier.rule_checker import *


class TestConculand(unittest.TestCase):
    log_file = "/vagrant/resources/conculand_1.log"
    checkpoint_file = "/vagrant/resources/conculand.chk"

    rule_1_statement = (
        "# Employees serve a person per round (they are not gnocchi)\n"
        "for every e1, e2=e1:\n"
        "between employee_ready(e1) and next employee_ready(e2):\n"
        "  for any employee_id=e1, person_name, type:\n"
        "  employee_serve(employee_id, person_name, type)must happen 1 times\n"
    )
    rule_1_scope = RuleScope([
        MatchCheckpoints(["employee_ready"]),
        RenameArgs(["employee_ready", "employee_ready"], [["e1"], ["e2"]]),
        CrossAndGroupByArgs(["employee_ready", "employee_ready"], [["e1"], ["e2"]]),
        ImposeIteratorCondition("e1", "=", "e2"),
        ScopeBetween("employee_ready1", "employee_ready2")
    ])
    rule_1_fact = RuleFact([
        MatchCheckpoints(["employee_serve"]),
        RenameArgs(["employee_serve"], [["employee_id", "person_name", "type"]]),
        CrossAndGroupByArgs(["employee_serve"], [["null"]]),
        ImposeWildcardCondition("employee_id", "=", "#e1", True),
        CompareResultsQuantity("=", 1),
        ReduceResult()
    ])
    rule_1 = JARLRule(rule_1_statement, rule_1_fact, rule_1_scope)
    rule_1.set_dynamic_scope_arg("e1", True)

    rule_2_statement = (
        "# Every tourist must wait in queue before being served\n"
        "for every e, person_name, t='tourist':\n"
        "before employee_serve(e, person_name, t):\n"
        "  for any pn=person_name:\n"
        "  tourist_queued(pn) must happen 1 times\n"
    )
    rule_2_scope = RuleScope([
        MatchCheckpoints(["employee_serve"]),
        RenameArgs(["employee_serve"], [["e", "person_name", "t"]]),
        CrossAndGroupByArgs(["employee_serve"], [["e", "person_name", "t"]]),
        ImposeIteratorCondition("t", "=", "tourist", True),
        ScopeBefore("employee_serve1")
    ])
    rule_2_fact = RuleFact([
        MatchCheckpoints(["tourist_queued"]),
        RenameArgs(["tourist_queued"], [["pn"]]),
        CrossAndGroupByArgs(["tourist_queued"], [["null"]]),
        ImposeWildcardCondition("pn", "=", "#person_name", True),
        CompareResultsQuantity("=", 1),
        ReduceResult()
    ])
    rule_2 = JARLRule(rule_2_statement, rule_2_fact, rule_2_scope)
    rule_2.set_dynamic_scope_arg("person_name", False)

    rule_3_statement = (
        "# Every resident must wait in queue before being served\n"
        "for every e, person_name, t='resident':\n"
        "before employee_serve(e, person_name, t):\n"
        "  for any pn=person_name:\n"
        "  resident_queued(pn) must happen 1 times\n"
    )
    rule_3_scope = RuleScope([
        MatchCheckpoints(["employee_serve"]),
        RenameArgs(["employee_serve"], [["e", "person_name", "t"]]),
        CrossAndGroupByArgs(["employee_serve"], [["e", "person_name", "t"]]),
        ImposeIteratorCondition("t", "=", "resident", True),
        ScopeBefore("employee_serve1")
    ])
    rule_3_fact = RuleFact([
        MatchCheckpoints(["resident_queued"]),
        RenameArgs(["resident_queued"], [["pn"]]),
        CrossAndGroupByArgs(["resident_queued"], [["null"]]),
        ImposeWildcardCondition("pn", "=", "#person_name", True),
        CompareResultsQuantity("=", 1),
        ReduceResult()
    ])
    rule_3 = JARLRule(rule_3_statement, rule_3_fact, rule_3_scope)
    rule_3.set_dynamic_scope_arg("person_name", False)

    rule_4_statement = (
        "# Every tourist shows their passport after being asked for it\n"
        "for every e1, e2=e1, person_name, t='tourist':\n"
        "between employee_serve(e1, person_name, t) and next employee_ready(e2):\n"
        "  for every employee_id=e1, pn=person_name and any passport, traits:\n"
        "  tourist_show_passport(pn, passport, traits) must follow employee_request_passport(employee_id)\n"
    )
    rule_4_scope = RuleScope([
        MatchCheckpoints(["employee_serve", "employee_ready"]),
        RenameArgs(["employee_serve", "employee_ready"], [["e1", "person_name", "t"], ["e2"]]),
        CrossAndGroupByArgs(["employee_serve", "employee_ready"], [["e1", "person_name", "t"], ["e2"]]),
        ImposeIteratorCondition("e1", "=", "e2"),
        ImposeIteratorCondition("t", "=", "tourist", True),
        ScopeBetween("employee_serve1", "employee_ready2")
    ])
    rule_4_fact = RuleFact([
        MatchCheckpoints(["tourist_show_passport", "employee_request_passport"]),
        RenameArgs(["tourist_show_passport", "employee_request_passport"],
                   [["pn", "passport", "traits"], ["employee_id"]]),
        CrossAndGroupByArgs(["tourist_show_passport", "employee_request_passport"], [["pn"], ["employee_id"]]),
        ImposeIteratorCondition("pn", "=", "#person_name", True),
        ImposeIteratorCondition("employee_id", "=", "#e1", True),
        CompareResultsPrecedence("employee_request_passport2", "tourist_show_passport1", False),
        ReduceResult()
    ])
    rule_4 = JARLRule(rule_4_statement, rule_4_fact, rule_4_scope)
    rule_4.set_dynamic_scope_arg("e1", True)
    rule_4.set_dynamic_scope_arg("person_name", True)

    rule_5_statement = (
        "# Every resident shows their document after being asked for it\n"
        "for every e1, e2=e1, person_name, t='resident':\n"
        "between employee_serve(e1, person_name, t) and next employee_ready(e2):\n"
        "  for every employee_id=e1, pn=person_name and any document, gender:\n"
        "  resident_show_document(pn, document, gender) must follow employee_request_document(employee_id)\n"
    )
    rule_5_scope = RuleScope([
        MatchCheckpoints(["employee_serve", "employee_ready"]),
        RenameArgs(["employee_serve", "employee_ready"], [["e1", "person_name", "t"], ["e2"]]),
        CrossAndGroupByArgs(["employee_serve", "employee_ready"], [["e1", "person_name", "t"], ["e2"]]),
        ImposeIteratorCondition("e1", "=", "e2"),
        ImposeIteratorCondition("t", "=", "resident", True),
        ScopeBetween("employee_serve1", "employee_ready2")
    ])
    rule_5_fact = RuleFact([
        MatchCheckpoints(["resident_show_document", "employee_request_document"]),
        RenameArgs(["resident_show_document", "employee_request_document"],
                   [["pn", "document", "gender"], ["employee_id"]]),
        CrossAndGroupByArgs(["resident_show_document", "employee_request_document"], [["pn"], ["employee_id"]]),
        ImposeIteratorCondition("pn", "=", "#person_name", True),
        ImposeIteratorCondition("employee_id", "=", "#e1", True),
        CompareResultsPrecedence("employee_request_document2", "resident_show_document1", False),
        ReduceResult()
    ])
    rule_5 = JARLRule(rule_5_statement, rule_5_fact, rule_5_scope)
    rule_5.set_dynamic_scope_arg("e1", True)
    rule_5.set_dynamic_scope_arg("person_name", True)

    rule_6_statement = (
        "# Every tourist shows their passport once before dying\n"
        "for every pn1, p1, t1, pn2=pn1, p2=p1, t2=t1:\n"
        "between tourist_spawn(pn1, p1, t1) and next tourist_die(pn2, p2, t2):\n"
        "  for any person_name=pn1, passport=p1, traits=t1:\n"
        "  tourist_show_passport(person_name, passport, traits) must happen 1 times\n"
    )
    rule_6_scope = RuleScope([
        MatchCheckpoints(["tourist_spawn", "tourist_die"]),
        RenameArgs(["tourist_spawn", "tourist_die"], [["pn1", "p1", "t1"], ["pn2", "p2", "t2"]]),
        CrossAndGroupByArgs(["tourist_spawn", "tourist_die"], [["pn1", "p1", "t1"], ["pn2", "p2", "t2"]]),
        ImposeIteratorCondition("pn1", "=", "pn2"),
        ImposeIteratorCondition("p1", "=", "p2"),
        ImposeIteratorCondition("t1", "=", "t2"),
        ScopeBetween("tourist_spawn1", "tourist_die2")
    ])
    rule_6_fact = RuleFact([
        MatchCheckpoints(["tourist_show_passport"]),
        RenameArgs(["tourist_show_passport"], [["person_name", "passport", "traits"]]),
        CrossAndGroupByArgs(["tourist_show_passport"], [["null"]]),
        ImposeWildcardCondition("person_name", "=", "#pn1", True),
        ImposeWildcardCondition("passport", "=", "#p1", True),
        ImposeWildcardCondition("traits", "=", "#t1", True),
        CompareResultsQuantity("=", 1),
        ReduceResult()
    ])
    rule_6 = JARLRule(rule_6_statement, rule_6_fact, rule_6_scope)
    rule_6.set_dynamic_scope_arg("pn1", True)
    rule_6.set_dynamic_scope_arg("p1", True)
    rule_6.set_dynamic_scope_arg("t1", True)

    rule_7_statement = (
        "# Every resident shows their document once before dying\n"
        "for every pn1, d1, g1, pn2=pn1, d2=d1, g2=g1:\n"
        "between resident_spawn(pn1, d1, g1) and next resident_die(pn2, d2, g2):\n"
        "  for any person_name=pn1, document=d1, gender=g1:\n"
        "  resident_show_document(person_name, document, gender) must happen 1 times\n"
    )
    rule_7_scope = RuleScope([
        MatchCheckpoints(["resident_spawn", "resident_die"]),
        RenameArgs(["resident_spawn", "resident_die"], [["pn1", "d1", "g1"], ["pn2", "d2", "g2"]]),
        CrossAndGroupByArgs(["resident_spawn", "resident_die"], [["pn1", "d1", "g1"], ["pn2", "d2", "g2"]]),
        ImposeIteratorCondition("pn1", "=", "pn2"),
        ImposeIteratorCondition("d1", "=", "d2"),
        ImposeIteratorCondition("g1", "=", "g2"),
        ScopeBetween("resident_spawn1", "resident_die2")
    ])
    rule_7_fact = RuleFact([
        MatchCheckpoints(["resident_show_document"]),
        RenameArgs(["resident_show_document"], [["person_name", "document", "gender"]]),
        CrossAndGroupByArgs(["resident_show_document"], [["null"]]),
        ImposeWildcardCondition("person_name", "=", "#pn1", True),
        ImposeWildcardCondition("document", "=", "#d1", True),
        ImposeWildcardCondition("gender", "=", "#g1", True),
        CompareResultsQuantity("=", 1),
        ReduceResult()
    ])
    rule_7 = JARLRule(rule_7_statement, rule_7_fact, rule_7_scope)
    rule_7.set_dynamic_scope_arg("pn1", True)
    rule_7.set_dynamic_scope_arg("d1", True)
    rule_7.set_dynamic_scope_arg("g1", True)

    rule_8_statement = (
        "# Tourists passports are sealed once before being allowed in\n"
        "for every employee_id, passport:\n"
        "before employee_allow_tourist(employee_id, passport):\n"
        "  for any e=employee_id, p=passport:\n"
        "  employee_seal_passport(e, p) must happen 1 times\n"
    )
    rule_8_scope = RuleScope([
        MatchCheckpoints(["employee_allow_tourist"]),
        RenameArgs(["employee_allow_tourist"], [["employee_id", "passport"]]),
        CrossAndGroupByArgs(["employee_allow_tourist"], [["employee_id", "passport"]]),
        ScopeBefore("employee_allow_tourist1")
    ])
    rule_8_fact = RuleFact([
        MatchCheckpoints(["employee_seal_passport"]),
        RenameArgs(["employee_seal_passport"], [["e", "p"]]),
        CrossAndGroupByArgs(["employee_seal_passport"], [["null"]]),
        ImposeWildcardCondition("e", "=", "#employee_id", True),
        ImposeWildcardCondition("p", "=", "#passport", True),
        CompareResultsQuantity("=", 1),
        ReduceResult()
    ])
    rule_8 = JARLRule(rule_8_statement, rule_8_fact, rule_8_scope)
    rule_8.set_dynamic_scope_arg("employee_id", False)
    rule_8.set_dynamic_scope_arg("passport", False)

    rule_9_statement = (
        "# A seal must be taken before sealing a passport\n"
        "for every e1, e2=e1, person_name, t='tourist', passport:\n"
        "between employee_serve(e1, person_name, t) and next employee_allow_tourist(e2, passport):\n"
        "  for every eid1=e1, eid2=e1, p=passport:\n"
        "  employee_take_seal(eid1) must precede employee_seal_passport(eid2, p)\n"
    )
    rule_9_scope = RuleScope([
        MatchCheckpoints(["employee_serve", "employee_allow_tourist"]),
        RenameArgs(["employee_serve", "employee_allow_tourist"], [["e1", "person_name", "t"], ["e2", "passport"]]),
        CrossAndGroupByArgs(["employee_serve", "employee_allow_tourist"],
                            [["e1", "person_name", "t"], ["e2", "passport"]]),
        ImposeIteratorCondition("e1", "=", "e2"),
        ImposeIteratorCondition("t", "=", "tourist", True),
        ScopeBetween("employee_serve1", "employee_allow_tourist2")
    ])
    rule_9_fact = RuleFact([
        MatchCheckpoints(["employee_take_seal", "employee_seal_passport"]),
        RenameArgs(["employee_take_seal", "employee_seal_passport"], [["eid1"], ["eid2", "p"]]),
        CrossAndGroupByArgs(["employee_take_seal", "employee_seal_passport"], [["eid1"], ["eid2", "p"]]),
        ImposeIteratorCondition("eid1", "=", "#e1", True),
        ImposeIteratorCondition("eid2", "=", "#e1", True),
        ImposeIteratorCondition("p", "=", "#passport", True),
        CompareResultsPrecedence("employee_take_seal1", "employee_seal_passport2"),
        ReduceResult()
    ])
    rule_9 = JARLRule(rule_9_statement, rule_9_fact, rule_9_scope)
    rule_9.set_dynamic_scope_arg("e1", True)
    rule_9.set_dynamic_scope_arg("passport", False)

    rule_10_statement = (
        "# There are only 3 seals available\n"
        "for any e1, e2:\n"
        "between employee_take_seal(e1) and next employee_return_seal(e2):\n"
        "  for any e:\n"
        "  employee_take_seal(e) must happen at most 3 times\n"
    )
    rule_10_scope = RuleScope([
        MatchCheckpoints(["employee_take_seal", "employee_return_seal"]),
        RenameArgs(["employee_take_seal", "employee_return_seal"], [["e1"], ["e2"]]),
        CrossAndGroupByArgs(["employee_take_seal", "employee_return_seal"], [["null"], ["null"]]),
        ScopeBetween("employee_take_seal1", "employee_return_seal2")
    ])
    rule_10_fact = RuleFact([
        MatchCheckpoints(["employee_take_seal"]),
        RenameArgs(["employee_take_seal"], [["e"]]),
        CrossAndGroupByArgs(["employee_take_seal"], [["null"]]),
        CompareResultsQuantity("<=", 3),
        ReduceResult()
    ])
    rule_10 = JARLRule(rule_10_statement, rule_10_fact, rule_10_scope)

    rule_11_statement = (
        "# 12 people are served\n"
        "for any e, p, t:\n"
        "employee_serve(e, p, t) must happen 12 times\n"
    )
    rule_11_fact = RuleFact([
        MatchCheckpoints(["employee_serve"]),
        RenameArgs(["employee_serve"], [["e", "p", "t"]]),
        CrossAndGroupByArgs(["employee_serve"], [["null"]]),
        CompareResultsQuantity("=", 12),
        ReduceResult()
    ])
    rule_11 = JARLRule(rule_11_statement, rule_11_fact)

    rule_12_statement = (
        "# All taken seals are later returned\n"
        "for every employee_id:\n"
        "after employee_take_seal(employee_id):\n"
        "  for any e=employee_id:\n"
        "  employee_return_seal(e) must happen at least 1 times\n"
    )
    rule_12_scope = RuleScope([
        MatchCheckpoints(["employee_take_seal"]),
        RenameArgs(["employee_take_seal"], [["employee_id"]]),
        CrossAndGroupByArgs(["employee_take_seal"], [["employee_id"]]),
        ScopeAfter("employee_take_seal1")
    ])
    rule_12_fact = RuleFact([
        MatchCheckpoints(["employee_return_seal"]),
        RenameArgs(["employee_return_seal"], [["e"]]),
        CrossAndGroupByArgs(["employee_return_seal"], [["null"]]),
        ImposeWildcardCondition("e", "=", "#employee_id", True),
        CompareResultsQuantity(">=", 1),
        ReduceResult()
    ])
    rule_12 = JARLRule(rule_12_statement, rule_12_fact, rule_12_scope)
    rule_12.set_dynamic_scope_arg("employee_id", True)

    def check_one_rule(self, rule):
        rc = RuleChecker([ rule ], self.log_file, self.checkpoint_file)
        rule = rc.check_all_rules()[0]
        self.assertTrue(rule.has_passed())

    def test_employee_serve_once_per_round(self):
        self.check_one_rule(self.rule_1)

    def test_tourists_wait_on_queue(self):
        self.check_one_rule(self.rule_2)

    def test_residents_wait_on_queue(self):
        self.check_one_rule(self.rule_3)

    def test_tourists_show_passport_when_asked(self):
        self.check_one_rule(self.rule_4)

    def test_residents_show_document_when_asked(self):
        self.check_one_rule(self.rule_5)

    def test_all_tourists_showed_passport(self):
        self.check_one_rule(self.rule_6)

    def test_all_residents_showed_document(self):
        self.check_one_rule(self.rule_7)

    def test_tourists_passports_sealed_before_allowed(self):
        self.check_one_rule(self.rule_8)

    def test_employee_take_seal_for_sealing(self):
        self.check_one_rule(self.rule_9)

    def test_at_most_3_seals_used_at_same_time(self):
        self.check_one_rule(self.rule_10)

    def test_12_people_served(self):
        self.check_one_rule(self.rule_11)

    def test_taken_seals_are_returned(self):
        self.check_one_rule(self.rule_12)

    def test_all_rules(self):
        all_rules = [
            self.rule_1,
            self.rule_2,
            self.rule_3,
            self.rule_4,
            self.rule_5,
            self.rule_6,
            self.rule_7,
            self.rule_8,
            self.rule_9,
            self.rule_10,
            self.rule_11,
            self.rule_12,
        ]
        rc = RuleChecker(all_rules, self.log_file, self.checkpoint_file)
        all_rules = rc.check_all_rules()

        all_passed = True
        for rule in all_rules:
            if rule.has_failed(): all_passed = False

        #VerifierPrinter(True).print_verifier_summary(all_rules)
        self.assertTrue(all_passed)

if __name__ == '__main__':
    unittest.main()