import unittest

from parser.JarlParserCLI import parse_str, parse_file
from parser.JarlRule import *
from parser.JarlParserExceptions import *

class TestExamplesFromSpec(unittest.TestCase):
    def test_jarl_spec_example_rule1(self):
        rules = parse_file("resources/jarl_spec_examples.jarl")

        rule_fact_filter = rules[0].fact.filter
        fact_filter_wildcards = []
        fact_filter_iterators = ["msg"]
        fact_filter_conditions = []
        self.assertEqual(fact_filter_wildcards, rule_fact_filter.wildcards)
        self.assertEqual(fact_filter_iterators, rule_fact_filter.iterators)
        self.assertEqual(fact_filter_conditions, rule_fact_filter.conditions)

        rule_fact = rules[0].fact.facts[0]
        fact_chk1 = JarlCheckpoint("write", ["msg"])
        fact_chk2 = JarlCheckpoint("read_everything")
        fact_req = JarlRuleFactRequirementOrder(fact_chk2)
        expected_fact_expr = JarlRuleFactClause(fact_chk1, fact_req)
        self.assertEqual(expected_fact_expr, rule_fact)



if __name__ == '__main__':
    unittest.main()
