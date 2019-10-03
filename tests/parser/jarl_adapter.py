import unittest

from parser.JarlParserCLI import parse_str, parse_file
from parser.JarlRule import *
from parser.JarlParserExceptions import *
from parser.JarlRuleAdapter import *
from common.aggregation_steps import *
from common.jarl_rule import *

class TestAdapter(unittest.TestCase):
    def test_basic_adapter(self):
        rule = """
        rule readers_read_two_times
        for every r and any room, msg
        read_room(r, room, msg) must happen 2 times
        """
        rules = parse_str(rule)

        steps = JarlRuleAdapter().rule_to_steps(rules[0])

        rule_header = "readers_read_two_times"
        rule_fact = RuleFact([
            MatchCheckpoints(["read_room"]),
            RenameArgs([["read_room", "r", "room", "msg"]]),
            CrossAndGroupByArgs([["read_room", "r"]]),
            CompareResultsQuantity("=", 2),
            ReduceResult()
        ])
        expected_rule_adapted = JARLRule("", rule_header, rule_fact, passed_by_default=False)

        self.assertEqual(expected_rule_adapted, steps)

if __name__ == '__main__':
    unittest.main()
