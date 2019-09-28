import unittest

from parser.JarlParserCLI import parse_str
from parser.JarlRule import *

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

    def test_parse_basic_scope(self):
        rule = """
        rule test_parse_rule_name
        after foo():
            bar() must happen
        """

        rules = parse_str(rule)

        # sanity checks
        self.assertEqual(len(rules), 1)
        self.assertEqual(rules[0].name, "test_parse_rule_name")

        rule_scope = rules[0].scope
        expected_selector =  JarlSelectorExpr("after", JarlCheckpoint("foo"))
        self.assertIsNone(rule_scope.filter)
        self.assertEqual(expected_selector, rule_scope.selector)

if __name__ == '__main__':
    unittest.main()
