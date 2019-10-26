import unittest

from parser.parser_cli import adapt_file

class TestAdapterProdCons(unittest.TestCase):
    exec(open("resources/prod_cons_1_rules.py").read())

    def test_all_prod_cons_rules(self):
        parsed_rules = adapt_file("resources/prod_cons_1_rules.jarl", False)
        for i in range(len(parsed_rules)):
            self.assertEqual(self.all_rules[i], parsed_rules[i])

class TestAdapterSmokers(unittest.TestCase):
    exec(open("resources/smokers_1_rules.py").read())

    def test_all_smoker_rules(self):
        parsed_rules = adapt_file("resources/smokers_1_rules.jarl", False)
        for i in range(len(parsed_rules)):
            self.assertEqual(self.all_rules[i], parsed_rules[i])

class TestAdapterReadersWriters(unittest.TestCase):
    exec(open("resources/readers_writers_1_rules.py").read())

    def test_all_readers_writers_rules(self):
        parsed_rules = adapt_file("resources/readers_writers_1_rules.jarl", False)
        for i in range(len(parsed_rules)):
            self.assertEqual(self.all_rules[i], parsed_rules[i])

class TestAdapterConculand(unittest.TestCase):
    exec(open("resources/conculand_1_rules.py").read())

    def test_all_conculand_rules(self):
        parsed_rules = adapt_file("resources/conculand_1_rules.jarl", False)
        for i in range(len(parsed_rules)):
            self.assertEqual(self.all_rules[i], parsed_rules[i])

class TestAdapterH2O(unittest.TestCase):
    exec(open("resources/h2o_1_rules.py").read())

    def test_all_h2o_rules(self):
        parsed_rules = adapt_file("resources/h2o_1_rules.jarl", False)
        for i in range(len(parsed_rules)):
            self.assertEqual(self.all_rules[i], parsed_rules[i])

class TestAdapterSanta(unittest.TestCase):
    exec(open("resources/santa_1_rules.py").read())

    def test_all_santa_rules(self):
        parsed_rules = adapt_file("resources/santa_1_rules.jarl", False)
        for i in range(len(parsed_rules)):
            self.assertEqual(self.all_rules[i], parsed_rules[i])

class TestAdapterPhilos(unittest.TestCase):
    exec(open("resources/philos_1_rules.py").read())

    def test_all_philos_rules(self):
        parsed_rules = adapt_file("resources/philos_1_rules.jarl", False)
        for i in range(len(parsed_rules)):
            self.assertEqual(self.all_rules[i], parsed_rules[i])

class TestAdapterConcuspring(unittest.TestCase):
    exec(open("resources/concuspring_1_rules.py").read())

    def test_all_philos_rules(self):
        parsed_rules = adapt_file("resources/concuspring_1_rules.jarl", False)
        for i in range(len(parsed_rules)):
            self.assertEqual(self.all_rules[i], parsed_rules[i])


if __name__ == '__main__':
    unittest.main(buffer=True)
