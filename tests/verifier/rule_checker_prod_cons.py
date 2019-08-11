import unittest

from verifier.rule_checker import *


class TestProducerConsumer1(unittest.TestCase):
    lp = LogParser("/vagrant/resources/prod_cons_1.log", "/vagrant/resources/prod_cons.chk")

    rule_1_statement = (
        "# Every item is produced only once\n"
        "for every i and any p:\n"
        "produce(p, i) must happen 1 time\n"
    )
    rule_1_transformations = [
        match_checkpoints(["produce"]),
        rename_args(["produce"], [ ["p", "i"] ]),
        cross_group_arg_names(["produce"], [ ["i"] ]),
        compare_results_quantity("=", 1),
        reduce_result()
    ]

    rule_2_statement = (
        "# Every item is consumed only once\n"
        "for every i and any c:\n"
        "consume(c, i) must happen 1 time\n"
    )
    rule_2_transformations = [
        match_checkpoints(["consume"]),
        rename_args(["consume"], [ ["c", "i"] ]),
        cross_group_arg_names(["consume"], [ ["i"] ]),
        compare_results_quantity("=", 1),
        reduce_result()
    ]

    rule_3_statement = (
        "# 10 items are produced\n"
        "for any p, i:\n"
        "produce(p, i) must happen 10 times\n"
    )
    rule_3_transformations = [
        match_checkpoints(["produce"]),
        rename_args(["produce"], [ ["p", "i"] ]),
        cross_group_arg_names(["produce"], [ ["null"] ]),
        compare_results_quantity("=", 10),
        reduce_result()
    ]

    rule_4_statement = (
        "# 10 items are consumed\n"
        "for any c, i:\n"
        "consume(c, i) must happen 10 times\n"
    )
    rule_4_transformations = [
        match_checkpoints(["consume"]),
        rename_args(["consume"], [ ["c", "i"] ]),
        cross_group_arg_names(["consume"], [ ["null"] ]),
        compare_results_quantity("=", 10),
        reduce_result()
    ]

    rule_5_statement = (
        "# Every item is produced before consumed\n"
        "for every i and any p, c:\n"
        "produce(p, i) must precede consume(c, i)\n"
    )
    rule_5_transformations = [
        match_checkpoints(["produce", "consume"]),
        rename_args(["produce", "consume"], [ ["p", "i1"], ["c", "i2"] ]),
        cross_group_arg_names(["produce", "consume"], [("i1",), ("i2",)]),
        having_iterators("i1", "=", "i2"),
        compare_results_precedence("produce1", "consume2"),
        reduce_result()
    ]

    rule_6_statement = (
        "# Items are produced in order\n"
        "for every i, j>i and any p:\n"
        "produce(p, i) must precede produce(p, j)\n"
    )
    rule_6_transformations = [
        match_checkpoints(["produce"]),
        rename_args(["produce", "produce"], [ ["p", "i"], ["p", "j"] ]),
        cross_group_arg_names(["produce", "produce"], [ ["i"], ["j"] ]),
        having_iterators("j", ">", "i"),
        compare_results_precedence("produce1", "produce2"),
        reduce_result()
        ]

    rule_7_statement = (
        "# Items are consumed in order\n"
        "for every i, j>i and any c:\n"
        "consume(c, i) must precede consume(c, j)\n"
    )
    rule_7_transformations = [
        match_checkpoints(["consume"]),
        rename_args(["consume", "consume"], [ ["c", "i"], ["c", "j"] ]),
        cross_group_arg_names(["consume", "consume"], [ ["i"], ["j"] ]),
        having_iterators("j", ">", "i"),
        compare_results_precedence("consume1", "consume2"),
        reduce_result()
        ]

    rule_8_statement = (
        "# The buffer size is 5\n"
        "between every produce and next consume:\n"
        "for any p, i:\n"
        "produce(p, i) must happen at most 5 times\n"
    )
    rule_8_between = scope_between("produce", "consume", True)
    rule_8_transformations = [
        match_checkpoints(["produce"]),
        rename_args(["produce"], [ ["p", "i"] ]),
        cross_group_arg_names(["produce"], [ ["null"] ]),
        compare_results_quantity("<=", 5),
        reduce_result()
    ]

    rule_9_statement = (
        "# Item is consumed only once (written differently)\n"
        "after every consume:\n"
        "for every c, i:\n"
        "consume(c, i) must happen 1 times\n"
    )
    rule_9_after = scope_after("consume")
    rule_9_transformations = [
        match_checkpoints(["consume"]),
        rename_args(["consume"], [ ["c", "i"] ]),
        cross_group_arg_names(["consume"], [ ["c", "i"] ]),
        compare_results_quantity("=", 1),
        reduce_result()
    ]

    rule_10_statement = (
        "# Item is produced only once (written differently)\n"
        "before every produce:\n"
        "for produce p, i:\n"
        "produce(p, i) must happen 1 times\n"
    )
    rule_10_before = scope_after("produce")
    rule_10_transformations = [
        match_checkpoints(["produce"]),
        rename_args(["produce"], [ ["p", "i"] ]),
        cross_group_arg_names(["produce"], [ ["p", "i"] ]),
        compare_results_quantity("=", 1),
        reduce_result()
    ]

    def test_every_item_produced_once(self):
        self.lp.populate_db()
        rc = RuleChecker([ JARLRule(self.rule_1_statement, self.rule_1_transformations) ])
        rule = rc.check_all_rules()[0]
        self.lp.db.concu_collection.drop()

        self.assertTrue(rule.has_passed())

    def test_every_item_consumed_once(self):
        self.lp.populate_db()
        rc = RuleChecker([ JARLRule(self.rule_2_statement, self.rule_2_transformations) ])
        rule = rc.check_all_rules()[0]
        self.lp.db.concu_collection.drop()

        self.assertTrue(rule.has_passed())

    def test_ten_items_produced(self):
        self.lp.populate_db()
        rc = RuleChecker([ JARLRule(self.rule_3_statement, self.rule_3_transformations) ])
        rule = rc.check_all_rules()[0]
        self.lp.db.concu_collection.drop()

        self.assertTrue(rule.has_passed())

    def test_ten_items_consumed(self):
        self.lp.populate_db()
        rc = RuleChecker([ JARLRule(self.rule_4_statement, self.rule_4_transformations) ])
        rule = rc.check_all_rules()[0]
        self.lp.db.concu_collection.drop()

        self.assertTrue(rule.has_passed())

    def test_items_produced_before_consumed(self):
        self.lp.populate_db()
        rc = RuleChecker([ JARLRule(self.rule_5_statement, self.rule_5_transformations) ])
        rule = rc.check_all_rules()[0]
        self.lp.db.concu_collection.drop()

        self.assertTrue(rule.has_passed())

    def test_items_produced_in_order(self):
        self.lp.populate_db()
        rc = RuleChecker([ JARLRule(self.rule_6_statement, self.rule_6_transformations) ])
        rule = rc.check_all_rules()[0]
        self.lp.db.concu_collection.drop()

        self.assertTrue(rule.has_passed())

    def test_items_consumed_in_order(self):
        self.lp.populate_db()
        rc = RuleChecker([ JARLRule(self.rule_7_statement, self.rule_7_transformations) ])
        rule = rc.check_all_rules()[0]
        self.lp.db.concu_collection.drop()

        self.assertTrue(rule.has_passed())

    def test_buffer_size_five(self):
        self.lp.populate_db()
        rc = RuleChecker([ JARLRule(self.rule_8_statement, self.rule_8_transformations, self.rule_8_between) ])
        rule = rc.check_all_rules()[0]
        self.lp.db.concu_collection.drop()

        self.assertTrue(rule.has_passed())

    def test_items_not_consumed_after_consumed(self):
        self.lp.populate_db()
        rc = RuleChecker([ JARLRule(self.rule_9_statement, self.rule_9_transformations, self.rule_9_after) ])
        rule = rc.check_all_rules()[0]
        self.lp.db.concu_collection.drop()

        self.assertTrue(rule.has_passed())

    def test_items_not_produced_before_produced(self):
        self.lp.populate_db()
        rc = RuleChecker([ JARLRule(self.rule_10_statement, self.rule_10_transformations, self.rule_10_before) ])
        rule = rc.check_all_rules()[0]
        self.lp.db.concu_collection.drop()

        self.assertTrue(rule.has_passed())

    def test_all_rules(self):
        self.lp.populate_db()
        all_rules = [
            JARLRule(self.rule_1_statement, self.rule_1_transformations),
            JARLRule(self.rule_2_statement, self.rule_2_transformations),
            JARLRule(self.rule_3_statement, self.rule_3_transformations),
            JARLRule(self.rule_4_statement, self.rule_4_transformations),
            JARLRule(self.rule_5_statement, self.rule_5_transformations),
            JARLRule(self.rule_6_statement, self.rule_6_transformations),
            JARLRule(self.rule_7_statement, self.rule_7_transformations),
            JARLRule(self.rule_8_statement, self.rule_8_transformations, self.rule_8_between),
            JARLRule(self.rule_9_statement, self.rule_9_transformations, self.rule_9_after),
            JARLRule(self.rule_9_statement, self.rule_9_transformations, self.rule_10_before)
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