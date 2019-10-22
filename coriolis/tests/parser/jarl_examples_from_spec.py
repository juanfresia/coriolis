import unittest

from parser.jarl_parser_cli import parse_file
from parser.jarl_rule import *
from parser.jarl_parser_exceptions import *

class TestExamplesFromSpec(unittest.TestCase):

    def test_jarl_spec_example_1(self):
        fact_filter_wildcards = []
        fact_filter_iterators = ["msg"]
        fact_filter_conditions = []
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("write", ["msg"])
        fact_chk2 = JarlCheckpoint("read_everything")
        fact_req = JarlRuleFactRequirementOrder(fact_chk2)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_1",
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[0])

    def test_jarl_spec_example_2(self):
        fact_filter_wildcards = []
        fact_filter_iterators = ["shmid"]
        fact_filter_conditions = []
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("shm_destroy", ["shmid"])
        fact_req = JarlRuleFactRequirementCount(JarlComparator.EQ, 1)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_2",
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[1])

    def test_jarl_spec_example_3(self):
        fact_filter_wildcards = []
        fact_filter_iterators = ["i", "j"]
        fact_filter_conditions = []
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("m", ["i", "j"])
        fact_req = JarlRuleFactRequirementCount(JarlComparator.GE, 2)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_3",
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[2])

    def test_jarl_spec_example_4(self):
        fact_filter_wildcards = ["item_id"]
        fact_filter_iterators = []
        fact_filter_conditions = []
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("produce", ["item_id"])
        fact_req = JarlRuleFactRequirementCount(JarlComparator.EQ, 10)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_4",
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[3])

    def test_jarl_spec_example_5(self):
        fact_filter_wildcards = ["pid"]
        fact_filter_iterators = []
        fact_filter_conditions = []
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("sem_wait", ["pid"])
        fact_req = JarlRuleFactRequirementCount(JarlComparator.LE, 5)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_5",
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[4])

    def test_jarl_spec_example_6(self):
        fact_filter_wildcards = ["i", "j"]
        fact_filter_iterators = []
        fact_filter_conditions = []
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("m", ["i", "j"])
        fact_req = JarlRuleFactRequirementCount(JarlComparator.EQ, 5)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_6",
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[5])

    def test_jarl_spec_example_7(self):
        fact_filter_wildcards = ["pid"]
        fact_filter_iterators = ["item_id"]
        fact_filter_conditions = []
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("produce", ["pid", "item_id"])
        fact_chk2 = JarlCheckpoint("consume_all")
        fact_req = JarlRuleFactRequirementOrder(fact_chk2)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_7",
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[6])

    def test_jarl_spec_example_8(self):
        fact_filter_wildcards = ["msg"]
        fact_filter_iterators = ["msqid"]
        fact_filter_conditions = []
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("msq_send", ["msqid", "msg"])
        fact_req = JarlRuleFactRequirementCount(JarlComparator.EQ, 10)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_8",
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[7])

    def test_jarl_spec_example_9(self):
        fact_filter_wildcards = ["j"]
        fact_filter_iterators = ["i"]
        fact_filter_conditions = []
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("m", ["i", "j"])
        fact_req = JarlRuleFactRequirementCount(JarlComparator.LE, 1)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_9",
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[8])

    def test_jarl_spec_example_10(self):
        fact_filter_wildcards = ["smoker_id", "element_id"]
        fact_filter_iterators = []
        fact_filter_conditions = [
            JarlWithCondition("element_id", JarlComparator.EQ, "smoker_id")
        ]
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("smoker_take_element", ["smoker_id", "element_id"])
        fact_req = JarlRuleFactRequirementCount(JarlComparator.EQ, 0)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_10",
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[9])

    def test_jarl_spec_example_11(self):
        fact_filter_wildcards = []
        fact_filter_iterators = ["i", "j"]
        fact_filter_conditions = [
            JarlWithCondition("j", JarlComparator.GT, "i")
        ]
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("produce", ["i"])
        fact_chk2 = JarlCheckpoint("produce", ["j"])
        fact_req = JarlRuleFactRequirementOrder(fact_chk2)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_11",
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[10])

    def test_jarl_spec_example_12(self):
        fact_filter_wildcards = []
        fact_filter_iterators = ["semid", "k"]
        fact_filter_conditions = [
            JarlWithCondition("k", JarlComparator.LT, 0, is_literal=True)
        ]
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("sem_create", ["semid", "k"])
        fact_req = JarlRuleFactRequirementCount(JarlComparator.EQ, 0)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_12",
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[11])



    def test_jarl_spec_example_13(self):
        scope_selector_chk1 = JarlCheckpoint("shm_destroy")
        scope_selector = JarlSelectorExpr(JarlSelectorClauseType.AFTER, scope_selector_chk1)

        fact_filter_wildcards = ["pid"]
        fact_filter_iterators = []
        fact_filter_conditions = []
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("shm_read", ["pid"])
        fact_req = JarlRuleFactRequirementCount(JarlComparator.EQ, 0)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_13",
            scope=JarlRuleScope(None, scope_selector),
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[12])

    def test_jarl_spec_example_14(self):
        scope_selector_chk1 = JarlCheckpoint("notify_all")
        scope_selector = JarlSelectorExpr(JarlSelectorClauseType.AFTER, scope_selector_chk1)

        fact_filter_wildcards = ["pid"]
        fact_filter_iterators = []
        fact_filter_conditions = []
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("process_awake", ["pid"])
        fact_req = JarlRuleFactRequirementCount(JarlComparator.LE, 5)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_14",
            scope=JarlRuleScope(None, scope_selector),
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[13])

    def test_jarl_spec_example_15(self):
        scope_selector_chk1 = JarlCheckpoint("lock_create")
        scope_selector = JarlSelectorExpr(JarlSelectorClauseType.BEFORE, end=scope_selector_chk1)

        fact_filter_wildcards = ["pid"]
        fact_filter_iterators = []
        fact_filter_conditions = []
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("lock_acquire", ["pid"])
        fact_req = JarlRuleFactRequirementCount(JarlComparator.EQ, 0)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_15",
            scope=JarlRuleScope(None, scope_selector),
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[14])

    def test_jarl_spec_example_16(self):
        scope_selector_chk1 = JarlCheckpoint("sem_signal")
        scope_selector = JarlSelectorExpr(JarlSelectorClauseType.BEFORE, end=scope_selector_chk1)

        fact_filter_wildcards = ["pid"]
        fact_filter_iterators = []
        fact_filter_conditions = []
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("sem_wait", ["pid"])
        fact_req = JarlRuleFactRequirementCount(JarlComparator.LE, 5)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_16",
            scope=JarlRuleScope(None, scope_selector),
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[15])

    def test_jarl_spec_example_17(self):
        scope_selector_chk1 = JarlCheckpoint("lock_destroy")
        scope_selector_chk2 = JarlCheckpoint("lock_create")
        scope_selector = JarlSelectorExpr(JarlSelectorClauseType.BETWEEN_PREV, scope_selector_chk1, scope_selector_chk2)

        fact_chk1 = JarlCheckpoint("lock_destroy")
        fact_req = JarlRuleFactRequirementCount(JarlComparator.EQ, 1)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_17",
            scope=JarlRuleScope(None, scope_selector),
            fact=JarlRuleFact(None, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[16])

    def test_jarl_spec_example_18(self):
        scope_selector_chk1 = JarlCheckpoint("produce")
        scope_selector_chk2 = JarlCheckpoint("consume")
        scope_selector = JarlSelectorExpr(JarlSelectorClauseType.BETWEEN_NEXT, scope_selector_chk1, scope_selector_chk2)

        fact_chk1 = JarlCheckpoint("produce")
        fact_req = JarlRuleFactRequirementCount(JarlComparator.LE, 5)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_18",
            scope=JarlRuleScope(None, scope_selector),
            fact=JarlRuleFact(None, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[17])

    def test_jarl_spec_example_19(self):
        scope_filter_wildcards = ["smoker_id"]
        scope_filter_iterators = []
        scope_filter_conditions = []
        scope_filter = JarlFilterExpr(scope_filter_iterators, scope_filter_wildcards, scope_filter_conditions)

        scope_selector_chk1 = JarlCheckpoint("smoker_smoke", ["smoker_id"])
        scope_selector_chk2 = JarlCheckpoint("agent_wake")
        scope_selector = JarlSelectorExpr(JarlSelectorClauseType.BETWEEN_NEXT, scope_selector_chk1, scope_selector_chk2)

        fact_filter_wildcards = ["sid", "element_id"]
        fact_filter_iterators = []
        fact_filter_conditions = []
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("smoker_take_element", ["sid", "element_id"])
        fact_req = JarlRuleFactRequirementCount(JarlComparator.EQ, 0)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_19",
            scope=JarlRuleScope(scope_filter, scope_selector),
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[18])

    def test_jarl_spec_example_20(self):
        scope_filter_wildcards = ["producer_id", "consumer_id", "i1", "i2"]
        scope_filter_iterators = []
        scope_filter_conditions = []
        scope_filter = JarlFilterExpr(scope_filter_iterators, scope_filter_wildcards, scope_filter_conditions)

        scope_selector_chk1 = JarlCheckpoint("produce", ["producer_id", "i1"])
        scope_selector_chk2 = JarlCheckpoint("consume", ["consumer_id", "i2"])
        scope_selector = JarlSelectorExpr(JarlSelectorClauseType.BETWEEN_NEXT, scope_selector_chk1, scope_selector_chk2)

        fact_filter_wildcards = ["p", "i"]
        fact_filter_iterators = []
        fact_filter_conditions = []
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("produce", ["p", "i"])
        fact_req = JarlRuleFactRequirementCount(JarlComparator.LE, 10)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_20",
            scope=JarlRuleScope(scope_filter, scope_selector),
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[19])

    def test_jarl_spec_example_21(self):
        scope_filter_wildcards = []
        scope_filter_iterators = ["lock_id"]
        scope_filter_conditions = []
        scope_filter = JarlFilterExpr(scope_filter_iterators, scope_filter_wildcards, scope_filter_conditions)

        scope_selector_chk1 = JarlCheckpoint("lock_destroy", ["lock_id"])
        scope_selector = JarlSelectorExpr(JarlSelectorClauseType.AFTER, scope_selector_chk1)

        fact_filter_wildcards = []
        fact_filter_iterators = ["lid"]
        fact_filter_conditions = [
            JarlWithCondition("lid", JarlComparator.EQ, "lock_id")
        ]
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("lock_acquire", ["lid"])
        fact_req = JarlRuleFactRequirementCount(JarlComparator.EQ, 0)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_21",
            scope=JarlRuleScope(scope_filter, scope_selector),
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[20])

    def test_jarl_spec_example_22(self):
        scope_filter_wildcards = []
        scope_filter_iterators = ["msqid1", "msqid2"]
        scope_filter_conditions = [
            JarlWithCondition("msqid1", JarlComparator.EQ, "msqid2")
        ]
        scope_filter = JarlFilterExpr(scope_filter_iterators, scope_filter_wildcards, scope_filter_conditions)

        scope_selector_chk1 = JarlCheckpoint("msq_create", ["msqid1"])
        scope_selector_chk2 = JarlCheckpoint("msq_destroy", ["msqid2"])
        scope_selector = JarlSelectorExpr(JarlSelectorClauseType.BETWEEN_NEXT, scope_selector_chk1, scope_selector_chk2)

        fact_filter_wildcards = ["msg_id1", "msg_id2"]
        fact_filter_iterators = ["m1", "m2"]
        fact_filter_conditions = [
            JarlWithCondition("m1", JarlComparator.EQ, "msqid1"),
            JarlWithCondition("m2", JarlComparator.EQ, "m1"),
            JarlWithCondition("msg_id1", JarlComparator.EQ, "msg_id2")
        ]
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("msq_send", ["m1", "msg_id1"])
        fact_chk2 = JarlCheckpoint("msq_receive", ["m2", "msg_id2"])
        fact_req = JarlRuleFactRequirementOrder(fact_chk2)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_22",
            scope=JarlRuleScope(scope_filter, scope_selector),
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[21])

    def test_jarl_spec_example_23(self):
        scope_filter_wildcards = []
        scope_filter_iterators = ["reader_id", "buffer", "msg"]
        scope_filter_conditions = []
        scope_filter = JarlFilterExpr(scope_filter_iterators, scope_filter_wildcards, scope_filter_conditions)

        scope_selector_chk1 = JarlCheckpoint("read_buffer", ["reader_id", "buffer", "msg"])
        scope_selector = JarlSelectorExpr(JarlSelectorClauseType.BEFORE, end=scope_selector_chk1)

        fact_filter_wildcards = ["b", "m", "writer_id"]
        fact_filter_iterators = []
        fact_filter_conditions = [
            JarlWithCondition("b", JarlComparator.EQ, "buffer"),
            JarlWithCondition("m", JarlComparator.EQ, "msg")
        ]
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_conditions)

        fact_chk1 = JarlCheckpoint("write_buffer", ["writer_id", "b", "m"])
        fact_req = JarlRuleFactRequirementCount(JarlComparator.GE, 1)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        expected_rule = JarlRule(
            name="example_23",
            scope=JarlRuleScope(scope_filter, scope_selector),
            fact=JarlRuleFact(fact_filter, fact_clause)
        )

        rules = parse_file("resources/jarl_spec_examples.jarl")
        self.assertEqual(expected_rule, rules[22])



if __name__ == '__main__':
    unittest.main(buffer=True)
