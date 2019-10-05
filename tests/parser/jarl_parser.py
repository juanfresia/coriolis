import unittest

from parser.JarlParserCLI import parse_str, parse_file
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
        rules = parse_str("this is a garbage rule, it should not mean anything", show_errors=False)
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
        for any e1:
        after foo():
        for every e2 with e2!=e3:
        bar() must happen
        """

        self.assertRaises(JarlArgumentNotDeclared, parse_str, rule)

    # Test involving selectors
    def test_parse_selector_after(self):
        rule = """
        rule test_parse_selector_after
        after foo()
        bar() must happen
        """

        rules = parse_str(rule)

        rule_selector = rules[0].scope.selector
        expected_selector = JarlSelectorExpr(JarlSelectorClauseType.AFTER, JarlCheckpoint("foo"))
        self.assertEqual(expected_selector, rule_selector)

    def test_parse_selector_before(self):
        rule = """
        rule test_parse_selector_before
        before foo()
        bar() must happen
        """

        rules = parse_str(rule)

        rule_selector = rules[0].scope.selector
        expected_selector = JarlSelectorExpr(JarlSelectorClauseType.BEFORE, end=JarlCheckpoint("foo"))
        self.assertEqual(expected_selector, rule_selector)

    def test_parse_selector_between_next(self):
        rule = """
        rule test_parse_selector_between_next
        between foo1() and next foo2()
        bar() must happen
        """

        rules = parse_str(rule)

        rule_selector = rules[0].scope.selector
        expected_selector = JarlSelectorExpr(JarlSelectorClauseType.BETWEEN_NEXT, start=JarlCheckpoint("foo1"), end=JarlCheckpoint("foo2"))
        self.assertEqual(expected_selector, rule_selector)

    def test_parse_selector_between_previous(self):
        rule = """
        rule test_parse_selector_between_previous
        between foo1() and previous foo2()
        bar() must happen
        """

        rules = parse_str(rule)

        rule_selector = rules[0].scope.selector
        expected_selector = JarlSelectorExpr(JarlSelectorClauseType.BETWEEN_PREV, start=JarlCheckpoint("foo1"), end=JarlCheckpoint("foo2"))
        self.assertEqual(expected_selector, rule_selector)

    def test_parse_selector_between_with_args(self):
        rule = """
        rule test_parse_selector_between_with_args
        for any e1 and every e2
        between foo1(e1) and next foo2(e2)
        bar() must happen
        """

        rules = parse_str(rule)

        rule_selector = rules[0].scope.selector
        expected_selector = JarlSelectorExpr(JarlSelectorClauseType.BETWEEN_NEXT, start=JarlCheckpoint("foo1", ["e1"]), end=JarlCheckpoint("foo2", ["e2"]))
        self.assertEqual(expected_selector, rule_selector)

    def test_parse_selector_undefined_args(self):
        rule = """
        rule test_parse_selector_undefined_args
        after foo(e1)
        bar() must happen
        """

        self.assertRaises(JarlArgumentNotDeclared, parse_str, rule)

    def test_parse_selector_with_arguments(self):
        rule = """
        rule test_parse_selector_with_arguments
        for every e1
        after foo(e1)
        bar() must happen
        """

        rules = parse_str(rule)

        rule_selector = rules[0].scope.selector
        expected_selector = JarlSelectorExpr(JarlSelectorClauseType.AFTER, start=JarlCheckpoint("foo", ["e1"]))
        self.assertEqual(expected_selector, rule_selector)

    def test_parse_selector_argument_already_used(self):
        rule = """
        rule test_parse_selector_argument_already_used
        for every e1
        after foo(e1, e1)
        bar() must happen
        """

        self.assertRaises(JarlArgumentAlreadyUsed, parse_str, rule)

    # Tests involving facts
    def test_parse_fact_basic(self):
        rule = """
        rule test_parse_fact_basic
        after foo()
        bar() must happen
        """

        rules = parse_str(rule)

        rule_fact = rules[0].fact.facts[0]
        chk = JarlCheckpoint("bar")
        req = JarlRuleFactRequirementCount()
        expected_fact = JarlRuleFactClause(chk, req)
        self.assertEqual(expected_fact, rule_fact)

    def test_parse_fact_basic_negated(self):
        rule = """
        rule test_parse_fact_basic_negated
        after foo()
        bar() must not happen
        """

        rules = parse_str(rule)

        rule_fact = rules[0].fact.facts[0]
        chk = JarlCheckpoint("bar")
        req = JarlRuleFactRequirementCount(type=JarlComparator.EQ, count=0)
        expected_fact = JarlRuleFactClause(chk, req)
        self.assertEqual(expected_fact, rule_fact)

    def test_parse_fact_count_at_least(self):
        rule = """
        rule test_parse_fact_count_at_least
        after foo()
        bar() must happen at least 10 times
        """

        rules = parse_str(rule)

        rule_fact = rules[0].fact.facts[0]
        chk = JarlCheckpoint("bar")
        req = JarlRuleFactRequirementCount(count=10, type=JarlComparator.GE)
        expected_fact = JarlRuleFactClause(chk, req)
        self.assertEqual(expected_fact, rule_fact)

    def test_parse_fact_count_at_most(self):
        rule = """
        rule test_parse_fact_basic_how_many
        after foo()
        bar() must not happen at most 2 times
        """

        rules = parse_str(rule)

        rule_fact = rules[0].fact.facts[0]
        chk = JarlCheckpoint("bar")
        # Since fact requirement is negated, the expected comparator would be GT
        req = JarlRuleFactRequirementCount(count=2, type=JarlComparator.GT)
        expected_fact = JarlRuleFactClause(chk, req)
        self.assertEqual(expected_fact, rule_fact)

    def test_parse_fact_order(self):
        rule = """
        rule test_parse_fact_order
        bar() must precede foo()
        """

        rules = parse_str(rule)

        rule_fact = rules[0].fact.facts[0]
        chk1 = JarlCheckpoint("bar")
        chk2 = JarlCheckpoint("foo")

        req = JarlRuleFactRequirementOrder(chk2)
        expected_fact = JarlRuleFactClause(chk1, req)
        self.assertEqual(expected_fact, rule_fact)

    def test_parse_fact_order_negated_err(self):
        rule = """
        rule test_parse_fact_order
        bar() must not precede foo()
        """

        self.assertRaises(JarlNegatedOrderRequirement, parse_str, rule)

    def test_parse_fact_undefined_args(self):
        rule = """
        rule test_parse_fact_undefined_args
        after foo()
        bar(e1) must happen
        """

        self.assertRaises(JarlArgumentNotDeclared, parse_str, rule)

    def test_parse_fact_with_argument_in_scope(self):
        rule = """
        rule test_parse_fact_with_argument_in_scope
        for every e1
        after foo()
        bar(e1) must happen
        """

        self.assertRaises(JarlArgumentNotDeclared, parse_str, rule)

    def test_parse_argument_in_fact_and_scope(self):
        rule = """
        rule test_parse_argument_in_fact_and_scope
        for every e1
        after foo(e1)
        bar(e1) must happen
        """

        self.assertRaises(JarlArgumentAlreadyUsed, parse_str, rule)

    def test_parse_argument_in_fact_with_scope(self):
        rule = """
        rule test_parse_argument_in_fact_with_scope
        after foo()
        for every e1
        bar(e1) must happen
        """

        rules = parse_str(rule)

        rule_fact = rules[0].fact.facts[0]
        chk = JarlCheckpoint("bar", ["e1"])
        req = JarlRuleFactRequirementCount()
        expected_fact = JarlRuleFactClause(chk, req)
        self.assertEqual(expected_fact, rule_fact)

    def test_define_argument_in_fact_and_scope(self):
        rule = """
        rule test_define_argument_in_fact_and_scope
        for every e1
        after foo(e1)
        for any e1
        bar(e1) must happen
        """

        self.assertRaises(JarlArgumentAlreadyDeclared, parse_str, rule)

    def test_parse_fact_argument_already_used(self):
        rule = """
        rule test_parse_fact_argument_already_used
        for every e1
        after foo()
        bar(e1) must precede foo(e1)
        """

        self.assertRaises(JarlArgumentNotDeclared, parse_str, rule)

    # Integration tests
    def test_parse_integration(self):
        rule = """
        rule test_parse_integration
        for every e1, e2, person_name, t with e2 = e1, t='tourist' :
        between employee_serve(e1, person_name, t) and next employee_ready(e2) :
        # Here is a comment
        for every employee_id, pn and any passport, traits with employee_id=e1, pn=person_name:
        tourist_show_passport(pn, passport, traits) must precede employee_request_passport(employee_id)
        """

        rules = parse_str(rule)

        rule_name = "test_parse_integration"

        filter_cond1 = JarlWithCondition("e2", JarlComparator.EQ, "e1")
        filter_cond2 = JarlWithCondition("t", JarlComparator.EQ, "tourist", is_literal=True)
        filter_wildcards = []
        filter_iterators = ["e1", "e2", "person_name", "t"]
        filter_condition = [filter_cond1, filter_cond2]
        filter = JarlFilterExpr(filter_iterators, filter_wildcards, filter_condition)

        selector_chk1 = JarlCheckpoint("employee_serve", ["e1", "person_name", "t"])
        selector_chk2 = JarlCheckpoint("employee_ready", ["e2"])
        selector = JarlSelectorExpr(JarlSelectorClauseType.BETWEEN_NEXT, selector_chk1, selector_chk2)

        scope = JarlRuleScope(filter, selector)

        fact_filter_cond1 = JarlWithCondition("employee_id", JarlComparator.EQ, "e1")
        fact_filter_cond2 = JarlWithCondition("pn", JarlComparator.EQ, "person_name")
        fact_filter_wildcards = ["passport", "traits"]
        fact_filter_iterators = ["employee_id", "pn"]
        fact_filter_condition = [fact_filter_cond1, fact_filter_cond2]
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_condition)

        fact_chk1 = JarlCheckpoint("tourist_show_passport", ["pn", "passport", "traits"])
        fact_chk2 = JarlCheckpoint("employee_request_passport", ["employee_id"])
        fact_req = JarlRuleFactRequirementOrder(fact_chk2)
        fact_clause = [JarlRuleFactClause(fact_chk1, fact_req)]

        fact = JarlRuleFact(fact_filter, fact_clause)

        expected_rule = JarlRule(rule_name, scope, fact)
        self.assertEqual(expected_rule, rules[0])

if __name__ == '__main__':
    unittest.main()
