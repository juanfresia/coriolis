import unittest

from verifier.verifier_cli import *


class TestBarberShop(unittest.TestCase):
    log_file = "./resources/barber_1.log"
    checkpoint_file = "./resources/barber.chk"
    mongo_factory = MongoClientFactory()

    rule_1_statement = (
        "rule get_hair_cut_once_if_waited\n"
        "for every c1:\n"
        "after take_seat(c1):\n"
        "    for any c2 with c2=c1:\n"
        "    get_hair_cut(c2) must happen 1 times\n"
    )
    rule_1_header = "get_hair_cut_once_if_waited"
    rule_1_scope = RuleScope([
        MatchCheckpoints(['take_seat']),
        RenameArgs([['take_seat', 'c1']]),
        CrossAndGroupByArgs([['take_seat', 'c1']]),
        ScopeAfter("take_seat")
    ])
    rule_1_fact = RuleFact([
        MatchCheckpoints(['get_hair_cut']),
        RenameArgs([['get_hair_cut', 'c2']]),
        CrossAndGroupByArgs([['get_hair_cut']]),
        ImposeWildcardCondition("c2", "=", "#c1", using_literal=True),
        CompareResultsQuantity("=", 1),
        ReduceResult(and_results=True)
    ])
    rule_1 = JARLRule(rule_1_statement, rule_1_header, rule_1_fact, rule_1_scope, passed_by_default=False)
    rule_1.set_dynamic_scope_arg("c1", True)

    rule_2_statement = (
        "rule dont_get_hair_cut_if_left\n"
        "for every c1:\n"
        "after leave_shop(c1):\n"
        "    for any c2 with c2=c1:\n"
        "    get_hair_cut(c2) must not happen\n"
    )
    rule_2_header = "dont_get_hair_cut_if_left"
    rule_2_scope = RuleScope([
        MatchCheckpoints(['leave_shop']),
        RenameArgs([['leave_shop', 'c1']]),
        CrossAndGroupByArgs([['leave_shop', 'c1']]),
        ScopeAfter("leave_shop")
    ])
    rule_2_fact = RuleFact([
        MatchCheckpoints(['get_hair_cut']),
        RenameArgs([['get_hair_cut', 'c2']]),
        CrossAndGroupByArgs([['get_hair_cut']]),
        ImposeWildcardCondition("c2", "=", "#c1", using_literal=True),
        CompareResultsQuantity("=", 0),
        ReduceResult(and_results=True)
    ])
    rule_2 = JARLRule(rule_2_statement, rule_2_header, rule_2_fact, rule_2_scope, passed_by_default=True)
    rule_2.set_dynamic_scope_arg("c1", True)

    rule_3_statement = (
        "rule at_most_2_get_hair_cut_between_cut_hairs\n"
        "for any c1, c2:\n"
        "between cut_hair(c1) and next cut_hair(c2):\n"
        "    for any c3:\n"
        "    get_hair_cut(c3) must happen at most 2 times\n"
    )
    rule_3_header = "at_most_2_get_hair_cut_between_cut_hairs"
    rule_3_scope = RuleScope([
        MatchCheckpoints(['cut_hair']),
        RenameArgs([['cut_hair', 'c1'], ['cut_hair', 'c2']]),
        CrossAndGroupByArgs([['cut_hair'], ['cut_hair']]),
        ScopeBetween("cut_hair", "cut_hair", using_next=True, using_beyond=False)
    ])
    rule_3_fact = RuleFact([
        MatchCheckpoints(['get_hair_cut']),
        RenameArgs([['get_hair_cut', 'c3']]),
        CrossAndGroupByArgs([['get_hair_cut']]),
        CompareResultsQuantity("<=", 2),
        ReduceResult(and_results=True)
    ])
    rule_3 = JARLRule(rule_3_statement, rule_3_header, rule_3_fact, rule_3_scope, passed_by_default=True)

    rule_4_statement = (
        "rule correct_get_hair_cut_happens_between_cut_hairs\n"
        "for any c1, c2:\n"
        "between cut_hair(c1) and next cut_hair(c2):\n"
        "    for any c3 with c3!=c1, c3!=c2:\n"
        "    get_hair_cut(c3) must not happen\n"
    )
    rule_4_header = "correct_get_hair_cut_happens_between_cut_hairs"
    rule_4_scope = RuleScope([
        MatchCheckpoints(['cut_hair']),
        RenameArgs([['cut_hair', 'c1'], ['cut_hair', 'c2']]),
        CrossAndGroupByArgs([['cut_hair'], ['cut_hair']]),
        ScopeBetween("cut_hair", "cut_hair", using_next=True, using_beyond=False)
    ])
    rule_4_fact = RuleFact([
        MatchCheckpoints(['get_hair_cut']),
        RenameArgs([['get_hair_cut', 'c3']]),
        CrossAndGroupByArgs([['get_hair_cut']]),
        ImposeWildcardCondition("c3", "!=", "#c1", using_literal=True),
        ImposeWildcardCondition("c3", "!=", "#c2", using_literal=True),
        CompareResultsQuantity("=", 0),
        ReduceResult(and_results=True)
    ])
    rule_4 = JARLRule(rule_4_statement, rule_4_header, rule_4_fact, rule_4_scope, passed_by_default=True)
    rule_4.set_dynamic_scope_arg("c1", True)
    rule_4.set_dynamic_scope_arg("c2", False)

    rule_5_statement = (
        "rule at_most_2_cut_hair_between_get_hair_cuts\n"
        "for any c1, c2:\n"
        "between get_hair_cut(c1) and next get_hair_cut(c2):\n"
        "    for any c3:\n"
        "    cut_hair(c3) must happen at most 2 times\n"
    )
    rule_5_header = "at_most_2_cut_hair_between_get_hair_cuts"
    rule_5_scope = RuleScope([
        MatchCheckpoints(['get_hair_cut']),
        RenameArgs([['get_hair_cut', 'c1'], ['get_hair_cut', 'c2']]),
        CrossAndGroupByArgs([['get_hair_cut'], ['get_hair_cut']]),
        ScopeBetween("get_hair_cut", "get_hair_cut", using_next=True, using_beyond=False)
    ])
    rule_5_fact = RuleFact([
        MatchCheckpoints(['cut_hair']),
        RenameArgs([['cut_hair', 'c3']]),
        CrossAndGroupByArgs([['cut_hair']]),
        CompareResultsQuantity("<=", 2),
        ReduceResult(and_results=True)
    ])
    rule_5 = JARLRule(rule_5_statement, rule_5_header, rule_5_fact, rule_5_scope, passed_by_default=True)

    rule_6_statement = (
        "rule correct_cut_hair_happens_between_get_hair_cuts\n"
        "for any c1, c2:\n"
        "between get_hair_cut(c1) and next get_hair_cut(c2):\n"
        "    for any c3 with c3!=c1, c3!=c2:\n"
        "    cut_hair(c3) must not happen\n"
    )
    rule_6_header = "correct_cut_hair_happens_between_get_hair_cuts"
    rule_6_scope = RuleScope([
        MatchCheckpoints(['get_hair_cut']),
        RenameArgs([['get_hair_cut', 'c1'], ['get_hair_cut', 'c2']]),
        CrossAndGroupByArgs([['get_hair_cut'], ['get_hair_cut']]),
        ScopeBetween("get_hair_cut", "get_hair_cut", using_next=True, using_beyond=False)
    ])
    rule_6_fact = RuleFact([
        MatchCheckpoints(['cut_hair']),
        RenameArgs([['cut_hair', 'c3']]),
        CrossAndGroupByArgs([['cut_hair']]),
        ImposeWildcardCondition("c3", "!=", "#c1", using_literal=True),
        ImposeWildcardCondition("c3", "!=", "#c2", using_literal=True),
        CompareResultsQuantity("=", 0),
        ReduceResult(and_results=True)
    ])
    rule_6 = JARLRule(rule_6_statement, rule_6_header, rule_6_fact, rule_6_scope, passed_by_default=True)
    rule_6.set_dynamic_scope_arg("c1", True)
    rule_6.set_dynamic_scope_arg("c2", False)

    rule_7_statement = (
        "rule five_chairs_for_waiting\n"
        "for any c1, c2:\n"
        "between take_seat(c1) and next get_hair_cut(c2):\n"
        "  for any c3:\n"
        "  take_seat(c3) must happen at most 5 times\n"
    )
    rule_7_header = "five_chairs_for_waiting"
    rule_7_scope = RuleScope([
        MatchCheckpoints(['take_seat', 'get_hair_cut']),
        RenameArgs([['take_seat', 'c1'], ['get_hair_cut', 'c2']]),
        CrossAndGroupByArgs([['take_seat'], ['get_hair_cut']]),
        ScopeBetween("take_seat", "get_hair_cut", using_next=True, using_beyond=False)
    ])
    rule_7_fact = RuleFact([
        MatchCheckpoints(['take_seat']),
        RenameArgs([['take_seat', 'c3']]),
        CrossAndGroupByArgs([['take_seat']]),
        CompareResultsQuantity("<=", 5),
        ReduceResult(and_results=True)
    ])
    rule_7 = JARLRule(rule_7_statement, rule_7_header, rule_7_fact, rule_7_scope, passed_by_default=True)

    rule_8_statement = (
        "rule no_get_hair_cut_before_taking_seat\n"
        "for every c1:\n"
        "before take_seat(c1):\n"
        "    for any c2 with c2=c1:\n"
        "    get_hair_cut(c2) must not happen\n"
    )
    rule_8_header = "no_get_hair_cut_before_taking_seat"
    rule_8_scope = RuleScope([
        MatchCheckpoints(['take_seat']),
        RenameArgs([['take_seat', 'c1']]),
        CrossAndGroupByArgs([['take_seat', 'c1']]),
        ScopeBefore("take_seat")
    ])
    rule_8_fact = RuleFact([
        MatchCheckpoints(['get_hair_cut']),
        RenameArgs([['get_hair_cut', 'c2']]),
        CrossAndGroupByArgs([['get_hair_cut']]),
        ImposeWildcardCondition("c2", "=", "#c1", using_literal=True),
        CompareResultsQuantity("=", 0),
        ReduceResult(and_results=True)
    ])
    rule_8 = JARLRule(rule_8_statement, rule_8_header, rule_8_fact, rule_8_scope, passed_by_default=True)
    rule_8.set_dynamic_scope_arg("c1", False)

    rule_9_statement = (
        "rule one_take_seat_per_customer\n"
        "for every c:\n"
        "take_seat(c) must happen at most 1 times\n"
    )
    rule_9_header = "one_take_seat_per_customer"
    rule_9_fact = RuleFact([
        MatchCheckpoints(['take_seat']),
        RenameArgs([['take_seat', 'c']]),
        CrossAndGroupByArgs([['take_seat', 'c']]),
        CompareResultsQuantity("<=", 1),
        ReduceResult(and_results=True)
    ])
    rule_9 = JARLRule(rule_9_statement, rule_9_header, rule_9_fact, passed_by_default=True)

    rule_10_statement = (
        "rule one_leave_shop_per_customer\n"
        "for every c:\n"
        "leave_shop(c) must happen at most 1 times"
    )
    rule_10_header = "one_leave_shop_per_customer"
    rule_10_fact = RuleFact([
        MatchCheckpoints(['leave_shop']),
        RenameArgs([['leave_shop', 'c']]),
        CrossAndGroupByArgs([['leave_shop', 'c']]),
        CompareResultsQuantity("<=", 1),
        ReduceResult(and_results=True)
    ])
    rule_10 = JARLRule(rule_10_statement, rule_10_header, rule_10_fact, passed_by_default=True)

    def check_one_rule(self, rule):
        lp = LogParser(self.log_file, self.checkpoint_file)
        client = self.mongo_factory.new_mongo_client()
        lp.populate_db(client)
        rule = RuleChecker.check_rule(self.mongo_factory, rule)
        client.drop()
        self.assertTrue(rule.has_passed())

    def test_get_hair_cut_once_if_waited(self):
        self.check_one_rule(self.rule_1)

    def test_dont_get_hair_cut_if_left(self):
        self.check_one_rule(self.rule_2)

    def test_2_get_hair_cut_between_cut_hairs(self):
        self.check_one_rule(self.rule_3)

    def test_correct_get_hair_cut_between_cut_hairs(self):
        self.check_one_rule(self.rule_4)

    def test_2_cut_hair_between_get_hair_cuts(self):
        self.check_one_rule(self.rule_5)

    def test_correct_cut_hair_between_get_hair_cuts(self):
        self.check_one_rule(self.rule_6)

    def test_five_chairs_for_waiting(self):
        self.check_one_rule(self.rule_7)

    def test_no_get_hair_cut_before_taking_seat(self):
        self.check_one_rule(self.rule_8)

    def test_one_take_seat_per_customer(self):
        self.check_one_rule(self.rule_9)

    def test_one_leave_shop_per_customer(self):
        self.check_one_rule(self.rule_10)

if __name__ == '__main__':
    unittest.main()

