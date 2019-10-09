import unittest

from parser.jarl_parser_cli import adapt_file

class TestAdapterProdCons(unittest.TestCase):
    parsed_rules = adapt_file("resources/prod_cons_1_rules.jarl", False)
    exec(open("resources/prod_cons_1_rules.py").read())

    def test_all_prod_cons_rules(self):
        for i in range(len(self.parsed_rules)):
            self.assertEqual(self.all_rules[i], self.parsed_rules[i])

class TestAdapterSmokers(unittest.TestCase):
    parsed_rules = adapt_file("resources/smokers_1_rules.jarl", False)
    exec(open("resources/smokers_1_rules.py").read())

    def test_all_smoker_rules(self):
        for i in range(len(self.parsed_rules)):
            self.assertEqual(self.all_rules[i], self.parsed_rules[i])

class TestAdapterReadersWriters(unittest.TestCase):
    parsed_rules = adapt_file("resources/readers_writers_1_rules.jarl", False)
    exec(open("resources/readers_writers_1_rules.py").read())

    def test_all_readers_writers_rules(self):
        for i in range(len(self.parsed_rules)):
            self.assertEqual(self.all_rules[i], self.parsed_rules[i])

class TestAdapterConculand(unittest.TestCase):
    parsed_rules = adapt_file("resources/conculand_1_rules.jarl", False)
    exec(open("resources/conculand_1_rules.py").read())

    def test_all_conculand_rules(self):
        for i in range(len(self.parsed_rules)):
            self.assertEqual(self.all_rules[i], self.parsed_rules[i])

class TestAdapterH2O(unittest.TestCase):
    parsed_rules = adapt_file("resources/h2o_1_rules.jarl", False)
    exec(open("resources/h2o_1_rules.py").read())

    def test_all_h2o_rules(self):
        for i in range(len(self.parsed_rules)):
            self.assertEqual(self.all_rules[i], self.parsed_rules[i])

class TestAdapterSanta(unittest.TestCase):
    parsed_rules = adapt_file("resources/santa_1_rules.jarl", False)
    exec(open("resources/santa_1_rules.py").read())

    def test_all_santa_rules(self):
        for i in range(len(self.parsed_rules)):
            self.assertEqual(self.all_rules[i], self.parsed_rules[i])


if __name__ == '__main__':
    unittest.main()
