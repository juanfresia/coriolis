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

    # TODO make it raise error
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
    def test_parse_filter_wildcards(self):
        rule = """
        rule test_parse_filter_wildcards
        for any e1, e2
        after foo()
        bar() must happen
        """
        rules = parse_str(rule)

        rule_scope = rules[0].scope
        expected_filter_wildcards = ["e1", "e2"]
        expected_filter_iterators = []
        expected_filter_condition = []

        self.assertIsNotNone(rule_scope.filter)
        self.assertEqual(expected_filter_wildcards, rule_scope.filter.wildcards)
        self.assertEqual(expected_filter_iterators, rule_scope.filter.iterators)
        self.assertEqual(expected_filter_condition, rule_scope.filter.conditions)

    def test_parse_filter_iterators(self):
        rule = """
        rule test_parse_filter_iterators
        for every e1, e2
        after foo()
        bar() must happen
        """
        rules = parse_str(rule)

        rule_scope = rules[0].scope
        expected_filter_wildcards = []
        expected_filter_iterators = ["e1", "e2"]
        expected_filter_condition = []

        self.assertIsNotNone(rule_scope.filter)
        self.assertEqual(expected_filter_wildcards, rule_scope.filter.wildcards)
        self.assertEqual(expected_filter_iterators, rule_scope.filter.iterators)
        self.assertEqual(expected_filter_condition, rule_scope.filter.conditions)

    def test_parse_filter_mixed_wildcards_iterators(self):
        rule = """
        rule test_parse_filter_mixed_wildcards_iterators
        for every e1, e2 and any e3, e4
        after foo()
        bar() must happen
        """
        rules = parse_str(rule)

        rule_scope = rules[0].scope
        expected_filter_wildcards = ["e3", "e4"]
        expected_filter_iterators = ["e1", "e2"]
        expected_filter_condition = []

        self.assertIsNotNone(rule_scope.filter)
        self.assertEqual(expected_filter_wildcards, rule_scope.filter.wildcards)
        self.assertEqual(expected_filter_iterators, rule_scope.filter.iterators)
        self.assertEqual(expected_filter_condition, rule_scope.filter.conditions)

    def test_parse_filter_insane_iterator(self):
        rule = """
        rule test_parse_filter_insane_iterator
        for every e1 and any e3, e4 and every e2
        after foo()
        bar() must happen
        """
        rules = parse_str(rule)

        # Note that parsing of the elements preserve order
        rule_scope = rules[0].scope
        expected_filter_wildcards = ["e3", "e4"]
        expected_filter_iterators = ["e1", "e2"]
        expected_filter_condition = []

        self.assertIsNotNone(rule_scope.filter)
        self.assertEqual(expected_filter_wildcards, rule_scope.filter.wildcards)
        self.assertEqual(expected_filter_iterators, rule_scope.filter.iterators)
        self.assertEqual(expected_filter_condition, rule_scope.filter.conditions)

    def test_parse_filter_iteratior_duplicated_err(self):
        rule = """
        rule test_parse_filter_same_argument_in_both_err
        for every e1 and every e1
        after foo()
        bar() must happen
        """

        self.assertRaises(JarlArgumentAlreadyDeclared, parse_str, rule)

    def test_parse_filter_same_argument_in_both_err(self):
        rule = """
        rule test_parse_filter_same_argument_in_both_err
        for every e1 and any e1
        after foo()
        bar() must happen
        """

        self.assertRaises(JarlArgumentAlreadyDeclared, parse_str, rule)

    # Tests involving conditions
    def test_parse_filter_conditions(self):
        operators = ["=", "!=", "<", "<=", ">", ">="]

        rule = """
        rule test_parse_filter_conditions
        for every e1, e2 with e1{}e2
        after foo()
        bar() must happen
        """

        for op in operators:
            rules = parse_str(rule.format(op))

            rule_scope = rules[0].scope
            expected_operator = JarlComparator(op)
            expected_filter_condition = [JarlWithCondition("e1", expected_operator, "e2")]
            self.assertEqual(expected_filter_condition, rule_scope.filter.conditions)

    def test_parse_filter_multiple_conditions(self):
        rule = """
        rule test_parse_filter_multiple_conditions
        for every e1, e2, e3, e4 with e1=e2, e3>e4, e2<=e4
        after foo()
        bar() must happen
        """

        rules = parse_str(rule)

        rule_scope = rules[0].scope
        expected_cond_1 = JarlWithCondition("e1", JarlComparator.EQ, "e2")
        expected_cond_2 = JarlWithCondition("e3", JarlComparator.GT, "e4")
        expected_cond_3 = JarlWithCondition("e2", JarlComparator.LE, "e4")
        expected_filter_condition = [expected_cond_1, expected_cond_2, expected_cond_3]
        self.assertEqual(expected_filter_condition, rule_scope.filter.conditions)

    def test_parse_filter_condition_uses_undefined_iterator(self):
        rule = """
        rule test_parse_filter_condition_uses_undefined_iterator
        for every e1, e2 with e1=e2, e3>e4
        after foo()
        bar() must happen
        """

        self.assertRaises(JarlArgumentNotDeclared, parse_str, rule)

    def test_parse_filter_condition_uses_wildcards(self):
        rule = """
        rule test_parse_filter_condition_uses_wildcards
        for any e1, e2 with e1<=e2
        after foo()
        bar() must happen
        """

        rules = parse_str(rule)

        rule_scope = rules[0].scope
        expected_cond = JarlWithCondition("e1", JarlComparator.LE, "e2")
        expected_filter_condition = [expected_cond]
        self.assertEqual(expected_filter_condition, rule_scope.filter.conditions)

    def test_parse_filter_condition_uses_wildcards2(self):
        rule = """
        rule test_parse_filter_condition_uses_wildcards2
        for any e1 and every e2 with e1=e2
        after foo()
        bar() must happen
        """

        self.assertRaises(JarlConditionMixesArguments, parse_str, rule)

    # Conditions involving literals
    def test_parse_filter_condition_literal_string(self):
        rule = """
        rule test_parse_filter_condition_literal_string
        for any e1 with e1=\'literal\'
        after foo()
        bar() must happen
        """

        rules = parse_str(rule)

        rule_scope = rules[0].scope
        expected_cond = JarlWithCondition("e1", JarlComparator.EQ, "literal", is_literal=True)
        expected_filter_condition = [expected_cond]
        self.assertEqual(expected_filter_condition, rule_scope.filter.conditions)

    def test_parse_filter_condition_literal_number(self):
        rule = """
        rule test_parse_filter_condition_literal_number
        for any e1 with e1=10
        after foo()
        bar() must happen
        """

        rules = parse_str(rule)

        rule_scope = rules[0].scope
        expected_cond = JarlWithCondition("e1", JarlComparator.EQ, 10, is_literal=True)
        expected_filter_condition = [expected_cond]
        self.assertEqual(expected_filter_condition, rule_scope.filter.conditions)

    def test_parse_filter_condition_literal_number_as_string(self):
        rule = """
        rule test_parse_filter_condition_literal_number_as_string
        for any e1 with e1=\'10\'
        after foo()
        bar() must happen
        """

        rules = parse_str(rule)

        rule_scope = rules[0].scope
        expected_cond = JarlWithCondition("e1", JarlComparator.EQ, "10", is_literal=True)
        expected_filter_condition = [expected_cond]
        self.assertEqual(expected_filter_condition, rule_scope.filter.conditions)

    # Tests involving filter in rule fact
    def test_parse_fact_filter(self):
        rule = """
        rule test_parse_filter
        for every e1, e2 with e2!=e1
        bar() must happen
        """

        rules = parse_str(rule)

        rule_fact = rules[0].fact
        expected_cond = JarlWithCondition("e2", JarlComparator.NE, "e1")
        expected_filter_wildcards = []
        expected_filter_iterators = ["e1", "e2"]
        expected_filter_condition = [expected_cond]
        self.assertEqual(expected_filter_wildcards, rule_fact.filter.wildcards)
        self.assertEqual(expected_filter_iterators, rule_fact.filter.iterators)
        self.assertEqual(expected_filter_condition, rule_fact.filter.conditions)

    def test_parse_fact_filter_with_scope_wildcard(self):
        rule = """
        rule test_parse_filter_with_scope_wildcard
        for any e1
        after foo()
        for every e2 with e2!=e1
        bar() must happen
        """

        rules = parse_str(rule)

        rule_fact = rules[0].fact
        expected_cond = JarlWithCondition("e2", JarlComparator.NE, "e1")
        expected_filter_wildcards = []
        expected_filter_iterators = ["e2"]
        expected_filter_condition = [expected_cond]
        self.assertEqual(expected_filter_wildcards, rule_fact.filter.wildcards)
        self.assertEqual(expected_filter_iterators, rule_fact.filter.iterators)
        self.assertEqual(expected_filter_condition, rule_fact.filter.conditions)

    def test_parse_fact_filter_argument_not_declared_err(self):
        rule = """
        rule test_parse_filter_argument_not_declared_err
        for any e1
        after foo()
        for every e2 with e2!=e3
        bar() must happen
        """

        self.assertRaises(JarlArgumentNotDeclared, parse_str, rule)

if __name__ == '__main__':
    unittest.main()
