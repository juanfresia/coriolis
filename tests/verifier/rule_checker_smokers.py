import unittest

from verifier.rule_checker import *


class TestSmokers(unittest.TestCase):
    lp = LogParser("/vagrant/resources/smokers_1.log", "/vagrant/resources/smokers.chk")

    rule_1_statement = (
        "# Only one smoker smokes at a time\n"
        "between agent_wake and next agent_wake\n"
        "for any s\n"
        "smoker_smoke(s) must happen 1 time\n"
    )
    rule_1_between = scope_between("agent_wake", "agent_wake", True)
    rule_1_transformations = [
        match_checkpoints(["smoker_smoke"]),
        rename_args(["smoker_smoke"], [ ["s"] ]),
        cross_group_arg_names(["smoker_smoke"], [ ["null"] ]),
        compare_results_quantity("=", 1),
        reduce_result()
    ]

    rule_2_statement = (
        "# Smoker that smoked could really smoke\n"
        "between agent_wake and next smoker_smoke\n"
        "for any s, e\n"
        "smoker_take_element(s, e) must happen 2 times\n"
    )
    rule_2_between = scope_between("agent_wake", "smoker_smoke", True)
    rule_2_transformations = [
        match_checkpoints(["smoker_take_element"]),
        rename_args(["smoker_take_element"], [ ["s", "e"] ]),
        cross_group_arg_names(["smoker_take_element"], [ ["null"] ]),
        impose_wildcard_condition("s", "=", "e"),
        compare_results_quantity("=", 2),
        reduce_result()
    ]

    def test_one_smoke_per_round(self):
        self.lp.populate_db()
        rc = RuleChecker([ JARLRule(self.rule_1_statement, self.rule_1_transformations, self.rule_1_between) ])
        rule = rc.check_all_rules()[0]
        self.lp.db.concu_collection.drop()

        self.assertTrue(rule.has_passed())

    def test_smoker_could_smoke(self):
        self.lp.populate_db()
        rc = RuleChecker([ JARLRule(self.rule_2_statement, self.rule_2_transformations, self.rule_2_between) ])
        rule = rc.check_all_rules()[0]
        self.lp.db.concu_collection.drop()

        self.assertTrue(rule.has_passed())


    def test_all_rules(self):
        self.lp.populate_db()
        all_rules = [
            JARLRule(self.rule_1_statement, self.rule_1_transformations, self.rule_1_between),
            JARLRule(self.rule_2_statement, self.rule_2_transformations, self.rule_2_between)
        ]
        rc = RuleChecker(all_rules)
        all_rules = rc.check_all_rules()
        self.lp.db.concu_collection.drop()

        all_passed = True
        for rule in all_rules:
            if rule.has_failed(): all_passed = False

        #VerifierPrinter(False).print_verifier_summary(all_rules)
        self.assertTrue(all_passed)

if __name__ == '__main__':
    unittest.main()