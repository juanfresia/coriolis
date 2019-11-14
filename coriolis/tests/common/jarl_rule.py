import unittest

from common.jarl_rule import *


class TestJarlRule(unittest.TestCase):

    def _create_scopeless_rule(self):
        rule_statement = (
            "# f(x) called just once\n"
            "rule f_once\n"
            "for any x:\n"
            "f(x) must happen 1 times\n"
        )
        rule_header = "f_once"
        rule_fact = RuleFact([
            MatchCheckpoints(["f"]),
            RenameArgs([["f", "x"]]),
            CrossAndGroupByArgs([["f"]]),
            CompareResultsQuantity("=", 1),
            ReduceResult()
        ])
        return JARLRule(rule_statement, rule_header, rule_fact, passed_by_default=False)

    def _create_scoped_rule(self):
        rule_statement = (
            "# g(y) called twice after f(x)\n"
            "rule g_twice_after_f\n"
            "for every x:\n"
            "after f(x):"
            "for any y:\n"
            "g(y) must happen 2 times\n"
        )
        rule_header = "g_twice_after_f"
        rule_scope = RuleScope([
            MatchCheckpoints(["f"]),
            RenameArgs([["f", "x"]]),
            CrossAndGroupByArgs([["f"]]),
            ScopeAfter("f")
        ])
        rule_fact = RuleFact([
            MatchCheckpoints(["g"]),
            RenameArgs([["g", "y"]]),
            CrossAndGroupByArgs([["g"]]),
            CompareResultsQuantity("=", 2),
            ReduceResult()
        ])
        return JARLRule(rule_statement, rule_header, rule_fact, rule_scope, passed_by_default=False)

    def _create_fact_for_dynamic_arged_rule(self, value_to_eval="#x1"):
        return RuleFact([
            MatchCheckpoints(["g"]),
            RenameArgs([["g", "x2", "y"]]),
            CrossAndGroupByArgs([["g"]]),
            ImposeWildcardCondition("x2", "=", value_to_eval, True),
            CompareResultsQuantity("=", 3),
            ReduceResult()
        ])

    def _create_dynamic_arged_rule(self):
        rule_statement = (
            "# g(x, y) called three times after f(x)\n"
            "rule g_three_times_after_f\n"
            "for every x1:\n"
            "after f(x1):"
            "for any x2, y with x2=x1:\n"
            "g(x2, y) must happen 3 times\n"
        )
        rule_header = "g_three_times_after_f"
        rule_scope = RuleScope([
            MatchCheckpoints(["f"]),
            RenameArgs([["f", "x1"]]),
            CrossAndGroupByArgs([["f"]]),
            ScopeAfter("f")
        ])
        rule_fact = self._create_fact_for_dynamic_arged_rule()
        rule = JARLRule(rule_statement, rule_header, rule_fact, rule_scope, passed_by_default=False)
        return rule.set_dynamic_scope_arg("x1", True)


    def test_scopeless_rule_creation(self):
        rule = self._create_scopeless_rule()

        self.assertFalse(rule.has_passed())
        self.assertFalse(rule.has_failed())
        self.assertFalse(rule.has_scope())

    def test_scopeless_rules_equality(self):
        rule_1 = self._create_scopeless_rule()
        rule_2 = self._create_scopeless_rule()

        self.assertEquals(rule_1, rule_2)

    def test_scopeless_failing_rule(self):
        rule = self._create_scopeless_rule()
        rule.set_failed(failed_info="Failed, just a test")

        self.assertFalse(rule.has_passed())
        self.assertTrue(rule.has_failed())
        self.assertEquals(rule.get_failed_info(), "Failed, just a test")

    def test_scopeless_passing_rule(self):
        rule = self._create_scopeless_rule()
        rule.set_passed()

        self.assertFalse(rule.has_failed())
        self.assertTrue(rule.has_passed())

    def test_scoped_rule_creation(self):
        rule = self._create_scoped_rule()

        self.assertFalse(rule.has_passed())
        self.assertFalse(rule.has_failed())
        self.assertTrue(rule.has_scope())

    def test_scoped_rules_equality(self):
        rule_1 = self._create_scoped_rule()
        rule_2 = self._create_scoped_rule()

        self.assertEquals(rule_1, rule_2)

    def test_scoped_failing_rule(self):
        rule = self._create_scoped_rule()
        failed_scope = {"c1": {"log_line": 8}, "c2": {"log_line": 17}}
        rule.set_failed(failed_scope=failed_scope, failed_info="Failed, just a test")

        self.assertFalse(rule.has_passed())
        self.assertTrue(rule.has_failed())
        self.assertEquals(rule.get_failed_info(), "Failed, just a test")
        self.assertEquals(rule.get_failed_scope(), (8, 17))

    def test_scoped_passing_rule(self):
        rule = self._create_scoped_rule()
        rule.set_passed()

        self.assertFalse(rule.has_failed())
        self.assertTrue(rule.has_passed())

    def test_dynamic_arged_rules_equality(self):
        rule_1 = self._create_dynamic_arged_rule()
        rule_2 = self._create_dynamic_arged_rule()

        self.assertEquals(rule_1, rule_2)

    def test_dynamic_arged_rules_args_evaluated_to_str(self):
        rule = self._create_dynamic_arged_rule()
        scope = {"c1": {"log_line": 8, "arg_x1": "hi117"}, "c2": {"log_line": "MAX"}}
        rule_fact = self._create_fact_for_dynamic_arged_rule(value_to_eval="hi117")
        evaluated_rule_fact = rule.evaluate_fact_steps(scope)

        self.assertEquals(evaluated_rule_fact[1], rule_fact.evaluate_steps()[0])

    def test_dynamic_arged_rules_args_evaluated_to_int(self):
        rule = self._create_dynamic_arged_rule()
        scope = {"c1": {"log_line": 8, "arg_x1": 1514}, "c2": {"log_line": "MAX"}}
        rule_fact = self._create_fact_for_dynamic_arged_rule(value_to_eval=1514)
        evaluated_rule_fact = rule.evaluate_fact_steps(scope)

        self.assertEquals(evaluated_rule_fact[1], rule_fact.evaluate_steps()[0])

class TestRuleScope(unittest.TestCase):

    def _create_after_scope(self):
        return RuleScope([
            MatchCheckpoints(["f"]),
            RenameArgs([["f", "x"]]),
            CrossAndGroupByArgs([["f"]]),
            ScopeAfter("f")
        ])

    def test_rule_scope_equality(self):
        scope_1 = self._create_after_scope()
        scope_2 = self._create_after_scope()

        self.assertEquals(scope_1, scope_2)

    def test_parse_scope_log_lines(self):
        scope_1 = {"c1": {"log_line": 6}, "c2": {"log_line": 19}}
        scope_2 = {"c1": {"log_line": "MIN"}, "c2": {"log_line": 67}}
        scope_3 = {"c1": {"log_line": 4}, "c2": {"log_line": "MAX"}}
        scope_4 = {"c1": {"log_line": "MIN"}, "c2": {"log_line": "MAX"}}

        self.assertEquals(RuleScope.parse_scope_log_lines(scope_1), (6, 19))
        self.assertEquals(RuleScope.parse_scope_log_lines(scope_2), ("MIN", 67))
        self.assertEquals(RuleScope.parse_scope_log_lines(scope_3), (4, "MAX"))
        self.assertEquals(RuleScope.parse_scope_log_lines(scope_4), ("MIN", "MAX"))

    def test_parse_scope_arg(self):
        scope = {"c1": {"log_line": 4, "arg_x": 64}, "c2": {"log_line": 19, "arg_y": "asdf"}}

        self.assertEquals(RuleScope.parse_scope_arg(scope, "x", first=True), 64)
        self.assertEquals(RuleScope.parse_scope_arg(scope, "y", first=False), "asdf")

    def test_get_default_scope(self):
        default_scope = RuleScope.get_default_scope()[0]

        self.assertEquals(RuleScope.parse_scope_log_lines(default_scope), ("MIN", "MAX"))


class TestRuleFact(unittest.TestCase):

    def _create_fact_with_dynamic_args(self, value_to_eval="#x1"):
        return RuleFact([
            MatchCheckpoints(["g"]),
            RenameArgs([["g", "x2", "y"]]),
            CrossAndGroupByArgs([["g"]]),
            ImposeWildcardCondition("x2", "=", value_to_eval, True),
            CompareResultsQuantity("=", 3),
            ReduceResult()
        ])

    def test_rule_fact_equality(self):
        fact_1 = self._create_fact_with_dynamic_args()
        fact_2 = self._create_fact_with_dynamic_args()

        self.assertEquals(fact_1, fact_2)

    def test_rule_fact_equality_after_evaluation(self):
        fact_1 = self._create_fact_with_dynamic_args(value_to_eval=19)
        fact_2 = self._create_fact_with_dynamic_args(value_to_eval=19)

        self.assertEquals(fact_1.evaluate_steps(), fact_2.evaluate_steps())







if __name__ == '__main__':
    unittest.main()
