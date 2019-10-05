import unittest

from parser.JarlParserCLI import parse_str, parse_file
from parser.JarlRule import *
from parser.JarlParserExceptions import *

class TestExamplesFromSpec(unittest.TestCase):
    def test_jarl_spec_example_rule1(self):
        rule = """
        rule readers_read_two_times
        for every r and any room, msg
        read_room(r, room, msg) must happen 2 times
        """

        rules = parse_str(rule)

        scope = None

        rule_name = "readers_read_two_times"
        fact_filter_wildcards = ["room", "msg"]
        fact_filter_iterators = ["r"]
        fact_filter_condition = []
        fact_filter = JarlFilterExpr(fact_filter_iterators, fact_filter_wildcards, fact_filter_condition)

        fact_chk = JarlCheckpoint("read_room", ["r", "room", "msg"])
        fact_req = JarlRuleFactRequirementCount(count=2, type=JarlComparator.EQ)
        fact_clause = [JarlRuleFactClause(fact_chk, fact_req)]

        fact = JarlRuleFact(fact_filter, fact_clause)

        expected_rule = JarlRule(rule_name, scope, fact)
        self.assertEqual(expected_rule, rules[0])


if __name__ == '__main__':
    unittest.main()
