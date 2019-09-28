import unittest

from verifier.rule_checker import *


class TestSmokers(unittest.TestCase):
    log_file = "/vagrant/resources/smokers_2.log"
    checkpoint_file = "/vagrant/resources/smokers.chk"

    rule_1_statement = (
        "# Only one smoker smokes at a time\n"
        "between agent_wake and next agent_wake:\n"
        "  for any s:\n"
        "  smoker_smoke(s) must happen 1 time\n"
    )
    rule_1_scope = RuleScope([
        MatchCheckpoints(["agent_wake"]),
        CrossAndGroupByArgs([ ["agent_wake"], ["agent_wake"] ]),
        ScopeBetween("agent_wake", "agent_wake")
    ])
    rule_1_fact = RuleFact([
        MatchCheckpoints(["smoker_smoke"]),
        RenameArgs([ ["smoker_smoke", "s"] ]),
        CrossAndGroupByArgs([ ["smoker_smoke"] ]),
        CompareResultsQuantity("=", 1),
        ReduceResult()
    ])
    rule_1 = JARLRule(rule_1_statement, rule_1_fact, rule_1_scope, passed_by_default=False)

    rule_2_statement = (
        "# Smoker that smoked took two elements\n"
        "for any s:\n"
        "between agent_wake and next smoker_smoke(s):\n"
        "  for any sid=s, e:\n"
        "  smoker_take_element(sid, e) must happen 2 times\n"
    )
    rule_2_scope = RuleScope([
        MatchCheckpoints(["agent_wake", "smoker_smoke"]),
        RenameArgs([ ["smoker_smoke", "s"] ]),
        CrossAndGroupByArgs([ ["agent_wake"], ["smoker_smoke"] ]),
        ScopeBetween("agent_wake", "smoker_smoke")
    ])
    rule_2_fact = RuleFact([
        MatchCheckpoints(["smoker_take_element"]),
        RenameArgs([ ["smoker_take_element", "sid", "e"] ]),
        CrossAndGroupByArgs([ ["smoker_take_element"] ]),
        ImposeWildcardCondition("sid", "=", "#s", True),
        CompareResultsQuantity("=", 2),
        ReduceResult()
    ])
    rule_2 = JARLRule(rule_2_statement, rule_2_fact, rule_2_scope, passed_by_default=False)
    rule_2.set_dynamic_scope_arg("s", False)

    rule_3_statement = (
        "# Every element can only be taken once\n"
        "for any s:\n"
        "between agent_wake and next smoker_smoke(s):\n"
        "  for every e and any sid=s:\n"
        "  smoker_take_element(sid, e) must happen 1 times\n"
    )
    rule_3_scope = RuleScope([
        MatchCheckpoints(["agent_wake", "smoker_smoke"]),
        RenameArgs([ ["smoker_smoke", "s"] ]),
        CrossAndGroupByArgs([ ["agent_wake"], ["smoker_smoke"] ]),
        ScopeBetween("agent_wake", "smoker_smoke")
    ])
    rule_3_fact = RuleFact([
        MatchCheckpoints(["smoker_take_element"]),
        RenameArgs([ ["smoker_take_element", "sid", "e"] ]),
        CrossAndGroupByArgs([ ["smoker_take_element", "e"] ]),
        ImposeWildcardCondition("sid", "=", "#s", True),
        CompareResultsQuantity("=", 1),
        ReduceResult()
    ])
    rule_3 = JARLRule(rule_3_statement, rule_3_fact, rule_3_scope, passed_by_default=False)
    rule_3.set_dynamic_scope_arg("s", False)

    rule_4_statement = (
        "# Elements cant be taken after smoking if agent doesnt wake again\n"
        "for any s:\n"
        "between smoker_smoke(s) and next agent_wake:\n"
        "  for any sid, e:\n"
        "  smoker_take_element(sid, e) must happen 0 times\n"
    )
    rule_4_scope = RuleScope([
        MatchCheckpoints(["smoker_smoke", "agent_wake"]),
        RenameArgs([ ["smoker_smoke", "s"] ]),
        CrossAndGroupByArgs([ ["smoker_smoke"], ["agent_wake"] ]),
        ScopeBetween("smoker_smoke", "agent_wake")
    ])
    rule_4_fact = RuleFact([
        MatchCheckpoints(["smoker_take_element"]),
        RenameArgs([ ["smoker_take_element", "sid", "e"] ]),
        CrossAndGroupByArgs([ ["smoker_take_element"] ]),
        CompareResultsQuantity("=", 0),
        ReduceResult()
    ])
    rule_4 = JARLRule(rule_4_statement, rule_4_fact, rule_4_scope, passed_by_default=True)

    rule_5_statement = (
        "# Agent produces 2 items per round\n"
        "between agent_wake and next agent_sleep:\n"
        "  for any e:\n"
        "  agent_produce(e) must happen 2 times\n"
    )
    rule_5_scope = RuleScope([
        MatchCheckpoints(["agent_wake", "agent_sleep"]),
        CrossAndGroupByArgs([ ["agent_wake"], ["agent_sleep"] ]),
        ScopeBetween("agent_wake", "agent_sleep")
    ])
    rule_5_fact = RuleFact([
        MatchCheckpoints(["agent_produce"]),
        RenameArgs([ ["agent_produce", "e"] ]),
        CrossAndGroupByArgs([ ["agent_produce"] ]),
        CompareResultsQuantity("=", 2),
        ReduceResult()
    ])
    rule_5 = JARLRule(rule_5_statement, rule_5_fact, rule_5_scope, passed_by_default=False)

    rule_6_statement = (
        "# Elements arent produced if agent is sleeping\n"
        "between agent_sleep and next agent_wake:\n"
        "  for any e:\n"
        "  agent_produce(e) must happen 0 times\n"
    )
    rule_6_scope = RuleScope([
        MatchCheckpoints(["agent_sleep", "agent_wake"]),
        CrossAndGroupByArgs([ ["agent_sleep"], ["agent_wake"] ]),
        ScopeBetween("agent_sleep", "agent_wake")
    ])
    rule_6_fact = RuleFact([
        MatchCheckpoints(["agent_produce"]),
        RenameArgs([ ["agent_produce", "e"] ]),
        CrossAndGroupByArgs([ ["agent_produce"] ]),
        CompareResultsQuantity("=", 0),
        ReduceResult()
    ])
    rule_6 = JARLRule(rule_6_statement, rule_6_fact, rule_6_scope, passed_by_default=True)

    rule_7_statement = (
        "# Smokers never take elements they already have\n"
        "for every s, e=s:\n"
        "smoker_take_element(s, e) must happen 0 times\n"
    )
    rule_7_fact = RuleFact([
        MatchCheckpoints(["smoker_take_element"]),
        RenameArgs([ ["smoker_take_element", "s", "e"] ]),
        CrossAndGroupByArgs([ ["smoker_take_element", "s", "e"] ]),
        ImposeIteratorCondition("s", "=", "e"),
        CompareResultsQuantity("=", 0),
        ReduceResult()
    ])
    rule_7 = JARLRule(rule_7_statement, rule_7_fact, passed_by_default=True)

    rule_8_statement = (
        "# Smoker smokes once between dreams\n"
        "for every s1, s2=s1:\n"
        "between smoker_sleep(s1) and next smoker_sleep(s2):\n"
        "  for any s=s1:\n"
        "  smoker_smoke(s) must happen 1 times\n"
    )
    rule_8_scope = RuleScope([
        MatchCheckpoints(["smoker_sleep"]),
        RenameArgs([ ["smoker_sleep", "s1"], ["smoker_sleep", "s2"] ]),
        CrossAndGroupByArgs([ ["smoker_sleep", "s1"], ["smoker_sleep", "s2"] ]),
        ImposeIteratorCondition("s1", "=", "s2"),
        ScopeBetween("smoker_sleep", "smoker_sleep")
    ])
    rule_8_fact = RuleFact([
        MatchCheckpoints(["smoker_smoke"]),
        RenameArgs([ ["smoker_smoke", "s"] ]),
        CrossAndGroupByArgs([ ["smoker_smoke"] ]),
        ImposeWildcardCondition("s", "=", "#s1", True),
        CompareResultsQuantity("=", 1),
        ReduceResult()
    ])
    rule_8 = JARLRule(rule_8_statement, rule_8_fact, rule_8_scope, passed_by_default=False)
    rule_8.set_dynamic_scope_arg("s1", False)

    rule_9_statement = (
        "# 40 elements are produced\n"
        "for any e:\n"
        "agent_produce(e) must happen 40 times\n"
    )
    rule_9_fact = RuleFact([
        MatchCheckpoints(["agent_produce"]),
        RenameArgs([ ["agent_produce", "e"] ]),
        CrossAndGroupByArgs([ ["agent_produce"] ]),
        CompareResultsQuantity("=", 40),
        ReduceResult()
    ])
    rule_9 = JARLRule(rule_9_statement, rule_9_fact, passed_by_default=False)

    rule_10_statement = (
        "# All elements are taken\n"
        "for any s, e:\n"
        "smoker_take_element(s, e) must happen 40 times\n"
    )
    rule_10_fact = RuleFact([
        MatchCheckpoints(["smoker_take_element"]),
        RenameArgs([ ["smoker_take_element", "s", "e"] ]),
        CrossAndGroupByArgs([ ["smoker_take_element"] ]),
        CompareResultsQuantity("=", 40),
        ReduceResult()
    ])
    rule_10 = JARLRule(rule_10_statement, rule_10_fact, passed_by_default=False)

    rule_11_statement = (
        "# 20 cigarettes can be smoked\n"
        "for any s:\n"
        "smoker_smoke(e) must happen 20 times\n"
    )
    rule_11_fact = RuleFact([
        MatchCheckpoints(["smoker_smoke"]),
        RenameArgs([ ["smoker_smoke", "s"] ]),
        CrossAndGroupByArgs([ ["smoker_smoke"] ]),
        CompareResultsQuantity("=", 20),
        ReduceResult()
    ])
    rule_11 = JARLRule(rule_11_statement, rule_11_fact, passed_by_default=False)

    def check_one_rule(self, rule):
        rc = RuleChecker([ rule ], self.log_file, self.checkpoint_file)
        rule = rc.check_all_rules()[0]
        self.assertTrue(rule.has_passed())

    def test_one_smoke_per_round(self):
        self.check_one_rule(self.rule_1)

    def test_smoker_took_two_elements(self):
        self.check_one_rule(self.rule_2)

    def test_elements_taken_once(self):
        self.check_one_rule(self.rule_3)

    def test_elements_arent_taken_after_smoke(self):
        self.check_one_rule(self.rule_4)

    def test_agent_produces_two_elements(self):
        self.check_one_rule(self.rule_5)

    def test_sleeping_agent_cant_produce(self):
        self.check_one_rule(self.rule_6)

    def test_smokers_dont_take_their_element(self):
        self.check_one_rule(self.rule_7)

    def test_smoke_once_between_dreams(self):
        self.check_one_rule(self.rule_8)

    def test_forty_elements_produced(self):
        self.check_one_rule(self.rule_9)

    def test_forty_elements_taken(self):
        self.check_one_rule(self.rule_10)

    def test_twenty_cigarettes_smoked(self):
        self.check_one_rule(self.rule_11)

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