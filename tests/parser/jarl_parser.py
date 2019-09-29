import unittest

from parser.JarlParserCLI import parse_str
from parser.JarlRule import *
from parser.JarlParserExceptions import *

class TestParserCLI(unittest.TestCase):
    def test_parse_rule_name(self):
        rule = """
        rule test_parse_rule_name
        after foo():
            bar() must happen
        """

        rules = parse_str(rule)

        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].name, "test_parse_rule_name")

    def test_parse_empty_str(self):
        rules = parse_str("")
        self.assertFalse(rules)

    def test_parse_garbage(self):
        rules = parse_str("this is a garbage rule, it should not mean anything")
        self.assertFalse(rules)
        self.assertListEqual([], rules)

    def test_parse_basic_rule(self):
        rule = """
        rule test_parse_basic_rule
        after foo():
            bar() must happen
        """
        rules = parse_str(rule)

        # sanity checks
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].name, "test_parse_basic_rule")

        rule_scope = rules[0].scope
        expected_selector =  JarlSelectorExpr(JarlSelectorClauseType.AFTER, JarlCheckpoint("foo"))
        rule_fact = rules[0].fact
        expected_facts = [JarlRuleFactClause(JarlCheckpoint("bar"), JarlRuleFactRequirementCount())]

        self.assertIsNone(rule_scope.filter)
        self.assertIsNone(rule_fact.filter)
        self.assertEqual(expected_selector, rule_scope.selector)
        self.assertEqual(expected_facts, rule_fact.facts)

    def test_parse_no_scope(self):
        rule = """
        rule test_parse_no_scope
        bar() must happen
        """
        rules = parse_str(rule)

        # sanity checks
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].name, "test_parse_no_scope")

        rule_scope = rules[0].scope
        rule_fact = rules[0].fact
        expected_facts = [JarlRuleFactClause(JarlCheckpoint("bar"), JarlRuleFactRequirementCount())]

        self.assertIsNone(rule_scope)
        self.assertIsNone(rule_fact.filter)
        self.assertEqual(expected_facts, rule_fact.facts)

    # Tests for filter expressions
    def test_parse_filter_any(self):
        rule = """
        rule test_parse_filter_any
        for any e1, e2
        after foo()
        bar() must happen
        """
        rules = parse_str(rule)

        rule_scope = rules[0].scope
        expected_filter_any = ["e1", "e2"]
        expected_filter_every = []
        expected_filter_condition = []

        self.assertIsNotNone(rule_scope.filter)
        self.assertEqual(expected_filter_any, rule_scope.filter.any)
        self.assertEqual(expected_filter_every, rule_scope.filter.every)
        self.assertEqual(expected_filter_condition, rule_scope.filter.conditions)

    def test_parse_filter_every(self):
        rule = """
        rule test_parse_filter_every
        for every e1, e2
        after foo()
        bar() must happen
        """
        rules = parse_str(rule)

        rule_scope = rules[0].scope
        expected_filter_any = []
        expected_filter_every = ["e1", "e2"]
        expected_filter_condition = []

        self.assertIsNotNone(rule_scope.filter)
        self.assertEqual(expected_filter_any, rule_scope.filter.any)
        self.assertEqual(expected_filter_every, rule_scope.filter.every)
        self.assertEqual(expected_filter_condition, rule_scope.filter.conditions)

    def test_parse_filter_mixed_any_every(self):
        rule = """
        rule test_parse_filter_mixed_any_every
        for every e1, e2 and any e3, e4
        after foo()
        bar() must happen
        """
        rules = parse_str(rule)

        rule_scope = rules[0].scope
        expected_filter_any = ["e3", "e4"]
        expected_filter_every = ["e1", "e2"]
        expected_filter_condition = []

        self.assertIsNotNone(rule_scope.filter)
        self.assertEqual(expected_filter_any, rule_scope.filter.any)
        self.assertEqual(expected_filter_every, rule_scope.filter.every)
        self.assertEqual(expected_filter_condition, rule_scope.filter.conditions)

    # TODO: does order matter??
    @unittest.skip
    def test_parse_filter_insane_iterator(self):
        rule = """
        rule test_parse_filter_insane_iterator
        for every e1 and any e3, e4 and every e2
        after foo()
        bar() must happen
        """
        rules = parse_str(rule)

        rule_scope = rules[0].scope
        expected_filter_any = ["e3", "e4"]
        expected_filter_every = ["e1", "e2"]
        expected_filter_condition = []

        self.assertIsNotNone(rule_scope.filter)
        self.assertEqual(expected_filter_any, rule_scope.filter.any)
        self.assertEqual(expected_filter_every, rule_scope.filter.every)
        self.assertEqual(expected_filter_condition, rule_scope.filter.conditions)

    @unittest.skip
    def test_parse_filter_iteratior_duplicated_err(self):
        rule = """
        rule test_parse_filter_same_argument_in_both_err
        for every e1 and every e1
        after foo()
        bar() must happen
        """

        self.assertRaises(JarlIteratorAlreadyDefined, parse_str, rule)

    @unittest.skip
    def test_parse_filter_same_argument_in_both_err(self):
        rule = """
        rule test_parse_filter_same_argument_in_both_err
        for every e1 and any e1
        after foo()
        bar() must happen
        """

        self.assertRaises(JarlIteratorAlreadyDefined, parse_str, rule)

    # Tests involving conditions
    def test_parse_filter_with_valid_condition(self):
        rule = """
        rule test_parse_filter_same_argument_in_both_err
        for every e1, e2 with e1=e2
        after foo()
        bar() must happen
        """
        rules = parse_str(rule)

        rule_scope = rules[0].scope
        expected_filter_any = []
        expected_filter_every = ["e1", "e2"]
        expected_filter_condition = [JarlWithCondition("e1", JarlComparator.EQ, "e2")]

        self.assertIsNotNone(rule_scope.filter)
        self.assertEqual(expected_filter_any, rule_scope.filter.any)
        self.assertEqual(expected_filter_every, rule_scope.filter.every)
        self.assertEqual(expected_filter_condition, rule_scope.filter.conditions)

if __name__ == '__main__':
    unittest.main()
