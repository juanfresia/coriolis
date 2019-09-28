import unittest

from parser.JarlParserCLI import parse_str

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

if __name__ == '__main__':
    unittest.main()
