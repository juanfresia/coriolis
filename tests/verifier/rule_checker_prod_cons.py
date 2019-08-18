import unittest

from verifier.rule_checker import *


class TestProducerConsumer1(unittest.TestCase):
    lp = LogParser("/vagrant/resources/prod_cons_1.log", "/vagrant/resources/prod_cons.chk")

    rule_1_statement = (
        "# Every item is produced only once\n"
        "for every i and any p:\n"
        "produce(p, i) must happen 1 time\n"
    )
    rule_1_fact = RuleFact([
        MatchCheckpoints(["produce"]),
        RenameArgs(["produce"], [ ["p", "i"] ]),
        CrossAndGroupByArgs(["produce"], [ ["i"] ]),
        CompareResultsQuantity("=", 1),
        ReduceResult()
    ])
    rule_1 = JARLRule(rule_1_statement, rule_1_fact)

    rule_2_statement = (
        "# Every item is consumed only once\n"
        "for every i and any c:\n"
        "consume(c, i) must happen 1 time\n"
    )
    rule_2_fact = RuleFact([
        MatchCheckpoints(["consume"]),
        RenameArgs(["consume"], [ ["c", "i"] ]),
        CrossAndGroupByArgs(["consume"], [ ["i"] ]),
        CompareResultsQuantity("=", 1),
        ReduceResult()
    ])
    rule_2 = JARLRule(rule_2_statement, rule_2_fact)

    rule_3_statement = (
        "# 10 items are produced\n"
        "for any p, i:\n"
        "produce(p, i) must happen 10 times\n"
    )
    rule_3_fact = RuleFact([
        MatchCheckpoints(["produce"]),
        RenameArgs(["produce"], [ ["p", "i"] ]),
        CrossAndGroupByArgs(["produce"], [ ["null"] ]),
        CompareResultsQuantity("=", 10),
        ReduceResult()
    ])
    rule_3 = JARLRule(rule_3_statement, rule_3_fact)

    rule_4_statement = (
        "# 10 items are consumed\n"
        "for any c, i:\n"
        "consume(c, i) must happen 10 times\n"
    )
    rule_4_fact = RuleFact([
        MatchCheckpoints(["consume"]),
        RenameArgs(["consume"], [ ["c", "i"] ]),
        CrossAndGroupByArgs(["consume"], [ ["null"] ]),
        CompareResultsQuantity("=", 10),
        ReduceResult()
    ])
    rule_4 = JARLRule(rule_4_statement, rule_4_fact)

    rule_5_statement = (
        "# Every item is produced before consumed\n"
        "for every i and any p, c:\n"
        "produce(p, i) must precede consume(c, i)\n"
    )
    rule_5_fact = RuleFact([
        MatchCheckpoints(["produce", "consume"]),
        RenameArgs(["produce", "consume"], [ ["p", "i1"], ["c", "i2"] ]),
        CrossAndGroupByArgs(["produce", "consume"], [("i1",), ("i2",)]),
        ImposeIteratorCondition("i1", "=", "i2"),
        CompareResultsPrecedence("produce1", "consume2"),
        ReduceResult()
    ])
    rule_5 = JARLRule(rule_5_statement, rule_5_fact)

    rule_6_statement = (
        "# Items are produced in order\n"
        "for every i, j>i and any p:\n"
        "produce(p, i) must precede produce(p, j)\n"
    )
    rule_6_fact = RuleFact([
        MatchCheckpoints(["produce"]),
        RenameArgs(["produce", "produce"], [ ["p", "i"], ["p", "j"] ]),
        CrossAndGroupByArgs(["produce", "produce"], [ ["i"], ["j"] ]),
        ImposeIteratorCondition("j", ">", "i"),
        CompareResultsPrecedence("produce1", "produce2"),
        ReduceResult()
    ])
    rule_6 = JARLRule(rule_6_statement, rule_6_fact)

    rule_7_statement = (
        "# Items are consumed in order\n"
        "for every i, j>i and any c:\n"
        "consume(c, i) must precede consume(c, j)\n"
    )
    rule_7_fact = RuleFact([
        MatchCheckpoints(["consume"]),
        RenameArgs(["consume", "consume"], [ ["c", "i"], ["c", "j"] ]),
        CrossAndGroupByArgs(["consume", "consume"], [ ["i"], ["j"] ]),
        ImposeIteratorCondition("j", ">", "i"),
        CompareResultsPrecedence("consume1", "consume2"),
        ReduceResult()
    ])
    rule_7 = JARLRule(rule_7_statement, rule_7_fact)

    rule_8_statement = (
        "# The buffer size is 5\n"
        "for any pid, cid, i1, i2:\n"
        "between every produce(pid, i1) and next consume(cid, i2):\n"
        "  for any p, i:\n"
        "  produce(p, i) must happen at most 5 times\n"
    )
    rule_8_scope = RuleScope([
        MatchCheckpoints(["produce", "consume"]),
        RenameArgs(["produce", "consume"], [ ["pid", "i1"], ["cid", "i2"] ]),
        CrossAndGroupByArgs(["produce", "consume"], [ ["null"], ["null"] ]),
        ScopeBetween("produce1", "consume2")
    ])
    rule_8_fact = RuleFact([
        MatchCheckpoints(["produce"]),
        RenameArgs(["produce"], [ ["p", "i"] ]),
        CrossAndGroupByArgs(["produce"], [ ["null"] ]),
        CompareResultsQuantity("<=", 5),
        ReduceResult()
    ])
    rule_8 = JARLRule(rule_8_statement, rule_8_fact, rule_8_scope)

    rule_9_statement = (
        "# Item is consumed only once (written differently)\n"
        "for any cid, iid:\n"
        "after every consume(cid, iid):\n"
        "  for every i and any c:\n"
        "  consume(c, i) must happen 1 times\n"
    )
    rule_9_scope = RuleScope([
        MatchCheckpoints(["consume"]),
        RenameArgs(["consume"], [ ["cid", "iid"] ]),
        CrossAndGroupByArgs(["consume"], [ ["null"] ]),
        ScopeAfter("consume1")
    ])
    rule_9_fact = RuleFact([
        MatchCheckpoints(["consume"]),
        RenameArgs(["consume"], [ ["c", "i"] ]),
        CrossAndGroupByArgs(["consume"], [ ["i"] ]),
        CompareResultsQuantity("=", 1),
        ReduceResult()
    ])
    rule_9 = JARLRule(rule_9_statement, rule_9_fact, rule_9_scope)

    rule_10_statement = (
        "# Item is produced only once (written differently)\n"
        "for any pid, iid:\n"
        "before every produce(pid, iid):\n"
        "  for every i and any p:\n"
        "  produce(p, i) must happen 1 times\n"
    )
    rule_10_scope = RuleScope([
        MatchCheckpoints(["produce"]),
        RenameArgs(["produce"], [ ["pid", "iid"] ]),
        CrossAndGroupByArgs(["produce"], [ ["null"] ]),
        ScopeBefore("produce1")
    ])
    rule_10_fact = RuleFact([
        MatchCheckpoints(["produce"]),
        RenameArgs(["produce"], [ ["p", "i"] ]),
        CrossAndGroupByArgs(["produce"], [ ["i"] ]),
        CompareResultsQuantity("=", 1),
        ReduceResult()
    ])
    rule_10 = JARLRule(rule_10_statement, rule_10_fact, rule_10_scope)

    rule_11_statement = (
        "# Consumer cannot consume items smaller than their own ID\n"
        "for every c, i<c:\n"
        "consume(c, i) must not happen\n"
    )
    rule_11_fact = RuleFact([
        MatchCheckpoints(["consume"]),
        RenameArgs(["consume"], [ ["c", "i"] ]),
        CrossAndGroupByArgs(["consume"], [ ["c", "i"] ]),
        ImposeIteratorCondition("i", "<", "c"),
        CompareResultsQuantity("=", 0),
        ReduceResult()
    ])
    rule_11 = JARLRule(rule_11_statement, rule_11_fact)

    def check_one_rule(self, rule):
        self.lp.populate_db()
        rc = RuleChecker([ rule ])
        rule = rc.check_all_rules()[0]
        self.lp.db.concu_collection.drop()

        self.assertTrue(rule.has_passed())

    def test_every_item_produced_once(self):
        self.check_one_rule(self.rule_1)

    def test_every_item_consumed_once(self):
        self.check_one_rule(self.rule_2)

    def test_ten_items_produced(self):
        self.check_one_rule(self.rule_3)

    def test_ten_items_consumed(self):
        self.check_one_rule(self.rule_4)

    def test_items_produced_before_consumed(self):
        self.check_one_rule(self.rule_5)

    def test_items_produced_in_order(self):
        self.check_one_rule(self.rule_6)

    def test_items_consumed_in_order(self):
        self.check_one_rule(self.rule_7)

    def test_buffer_size_five(self):
        self.check_one_rule(self.rule_8)

    def test_items_not_consumed_after_consumed(self):
        self.check_one_rule(self.rule_9)

    def test_items_not_produced_before_produced(self):
        self.check_one_rule(self.rule_10)

    def test_cant_consume_items_smaller_than_id(self):
        self.check_one_rule(self.rule_11)

    def test_all_rules(self):
        self.lp.populate_db()
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
        rc = RuleChecker(all_rules)
        all_rules = rc.check_all_rules()
        self.lp.db.concu_collection.drop()

        all_passed = True
        for rule in all_rules:
            if rule.has_failed(): all_passed = False

        #VerifierPrinter(True).print_verifier_summary(all_rules)
        self.assertTrue(all_passed)

if __name__ == '__main__':
    unittest.main()