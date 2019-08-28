import unittest

from verifier.rule_checker import *


class TestH2O(unittest.TestCase):
    log_file = "/vagrant/resources/h2o_1.log"
    checkpoint_file = "/vagrant/resources/h2o.chk"

    rule_1_statement = (
        "# 60 atoms are spawned in total\n"
        "for any atom_type, atom_id:\n"
        "atom_spawn(atom_type, atom_id) must happen 60 times\n"
    )
    rule_1_fact = RuleFact([
        MatchCheckpoints(["atom_spawn"]),
        RenameArgs(["atom_spawn"], [["atom_type", "atom_id"]]),
        CrossAndGroupByArgs(["atom_spawn"], [["null"]]),
        CompareResultsQuantity("=", 60),
        ReduceResult()
    ])
    rule_1 = JARLRule(rule_1_statement, rule_1_fact)

    rule_2_statement = (
        "# All 60 atoms eventually die\n"
        "for any atom_type, atom_id:\n"
        "atom_die(atom_type, atom_id) must happen 60 times\n"
    )
    rule_2_fact = RuleFact([
        MatchCheckpoints(["atom_die"]),
        RenameArgs(["atom_die"], [["atom_type", "atom_id"]]),
        CrossAndGroupByArgs(["atom_die"], [["null"]]),
        CompareResultsQuantity("=", 60),
        ReduceResult()
    ])
    rule_2 = JARLRule(rule_2_statement, rule_2_fact)

    rule_3_statement = (
        "# Atoms die after spawning\n"
        "for every atom_id and any atom_type:\n"
        "after atom_spawn(atom_type, atom_id):\n"
        "  for every aid=atom_id and any at=atom_type:\n"
        "  atom_die(at, aid) must happen 1 times\n"
    )
    rule_3_scope = RuleScope([
        MatchCheckpoints(["atom_spawn"]),
        RenameArgs(["atom_spawn"], [["atom_type", "atom_id"]]),
        CrossAndGroupByArgs(["atom_spawn"], [["atom_id"]]),
        ScopeAfter("atom_spawn1")
    ])
    rule_3_fact = RuleFact([
        MatchCheckpoints(["atom_die"]),
        RenameArgs(["atom_die"], [["at", "aid"]]),
        CrossAndGroupByArgs(["atom_die"], [["aid"]]),
        ImposeIteratorCondition("aid", "=", "#atom_id", True),
        ImposeWildcardCondition("at", "=", "#atom_type", True),
        CompareResultsQuantity("=", 1),
        ReduceResult()
    ])
    rule_3 = JARLRule(rule_3_statement, rule_3_fact, rule_3_scope)
    rule_3.set_dynamic_scope_arg("atom_id", True)
    rule_3.set_dynamic_scope_arg("atom_type", True)

    rule_4_statement = (
        "# All 60 atoms eventually bond\n"
        "for any atom_type, atom_id:\n"
        "bond(atom_type, atom_id) must happen 60 times\n"
    )
    rule_4_fact = RuleFact([
        MatchCheckpoints(["bond"]),
        RenameArgs(["bond"], [["atom_type", "atom_id"]]),
        CrossAndGroupByArgs(["bond"], [["null"]]),
        CompareResultsQuantity("=", 60),
        ReduceResult()
    ])
    rule_4 = JARLRule(rule_4_statement, rule_4_fact)

    rule_5_statement = (
        "# Atoms bond while being alive\n"
        "for every aid1, aid2=aid1 and any at1, at2=at1:\n"
        "between atom_spawn(at1, aid1) and next atom_die(at2, aid2):\n"
        "  for every atom_id=aid1 and any atom_type=at1:\n"
        "  bond(atom_type, atom_id) must happen 1 times\n"
    )
    rule_5_scope = RuleScope([
        MatchCheckpoints(["atom_spawn", "atom_die"]),
        RenameArgs(["atom_spawn", "atom_die"], [["at1", "aid1"], ["at2", "aid2"]]),
        CrossAndGroupByArgs(["atom_spawn", "atom_die"], [["aid1"], ["aid2"]]),
        ImposeIteratorCondition("aid1", "=", "aid2"),
        ScopeBetween("atom_spawn1", "atom_die2")
    ])
    rule_5_fact = RuleFact([
        MatchCheckpoints(["bond"]),
        RenameArgs(["bond"], [["atom_type", "atom_id"]]),
        CrossAndGroupByArgs(["bond"], [["atom_id"]]),
        ImposeIteratorCondition("atom_id", "=", "#aid1", True),
        ImposeWildcardCondition("atom_type", "=", "#at1", True),
        CompareResultsQuantity("=", 1),
        ReduceResult()
    ])
    rule_5 = JARLRule(rule_5_statement, rule_5_fact, rule_5_scope)
    rule_5.set_dynamic_scope_arg("aid1", True)
    rule_5.set_dynamic_scope_arg("at1", True)

    rule_6_statement = (
        "# 20 water molecules are made\n"
        "water_made must happen 20 times\n"
    )
    rule_6_fact = RuleFact([
        MatchCheckpoints(["water_made"]),
        RenameArgs(["water_made"], [["null"]]),
        CrossAndGroupByArgs(["water_made"], [["null"]]),
        CompareResultsQuantity("=", 20),
        ReduceResult()
    ])
    rule_6 = JARLRule(rule_6_statement, rule_6_fact)

    rule_7_statement = (
        "# 2 hydrogen atoms must bond to make a new water molecule\n"
        "between water_made and next water_made:\n"
        "  for every atom_type='H' and any atom_id:\n"
        "  bond(atom_type, atom_id) must happen 2 times\n"
    )
    rule_7_scope = RuleScope([
        MatchCheckpoints(["water_made"]),
        RenameArgs(["water_made"], [["null"]]),
        CrossAndGroupByArgs(["water_made", "water_made"], [["null"], ["null"]]),
        ScopeBetween("water_made1", "water_made2")
    ])
    rule_7_fact = RuleFact([
        MatchCheckpoints(["bond"]),
        RenameArgs(["bond"], [["atom_type", "atom_id"]]),
        CrossAndGroupByArgs(["bond"], [["atom_type"]]),
        ImposeIteratorCondition("atom_type", "=", "H", True),
        CompareResultsQuantity("=", 2),
        ReduceResult()
    ])
    rule_7 = JARLRule(rule_7_statement, rule_7_fact, rule_7_scope)

    rule_8_statement = (
        "# 1 oxygen atom must bond to make a new water molecule\n"
        "between water_made and next water_made:\n"
        "  for every atom_type='O' and any atom_id:\n"
        "  bond(atom_type, atom_id) must happen 1 times\n"
    )
    rule_8_scope = RuleScope([
        MatchCheckpoints(["water_made"]),
        RenameArgs(["water_made"], [["null"]]),
        CrossAndGroupByArgs(["water_made", "water_made"], [["null"], ["null"]]),
        ScopeBetween("water_made1", "water_made2")
    ])
    rule_8_fact = RuleFact([
        MatchCheckpoints(["bond"]),
        RenameArgs(["bond"], [["atom_type", "atom_id"]]),
        CrossAndGroupByArgs(["bond"], [["atom_type"]]),
        ImposeIteratorCondition("atom_type", "=", "O", True),
        CompareResultsQuantity("=", 1),
        ReduceResult()
    ])
    rule_8 = JARLRule(rule_8_statement, rule_8_fact, rule_8_scope)

    rule_9_statement = (
        "# In total, 3 atoms bond to make a new water molecule\n"
        "between water_made and next water_made:\n"
        "  for any atom_type, atom_id:\n"
        "  bond(atom_type, atom_id) must happen 3 times\n"
    )
    rule_9_scope = RuleScope([
        MatchCheckpoints(["water_made"]),
        RenameArgs(["water_made"], [["null"]]),
        CrossAndGroupByArgs(["water_made", "water_made"], [["null"], ["null"]]),
        ScopeBetween("water_made1", "water_made2")
    ])
    rule_9_fact = RuleFact([
        MatchCheckpoints(["bond"]),
        RenameArgs(["bond"], [["atom_type", "atom_id"]]),
        CrossAndGroupByArgs(["bond"], [["null"]]),
        CompareResultsQuantity("=", 3),
        ReduceResult()
    ])
    rule_9 = JARLRule(rule_9_statement, rule_9_fact, rule_9_scope)

    rule_10_statement = (
        "# At most 2 bonds can happen between consecutive hydrogen bonds\n"
        "for every at1='H',at2='H' and any aid1, aid2:\n"
        "between bond(at1, aid1) and next bond(at2, aid2):\n"
        "  for any atom_type!='H', atom_id:\n"
        "  bond(atom_type, atom_id) must happen at most 2 times\n"
    )
    rule_10_scope = RuleScope([
        MatchCheckpoints(["bond"]),
        RenameArgs(["bond", "bond"], [["at1", "aid1"], ["at2", "aid2"]]),
        CrossAndGroupByArgs(["bond", "bond"], [["at1"], ["at2"]]),
        ImposeIteratorCondition("at1", "=", "H", True),
        ImposeIteratorCondition("at2", "=", "H", True),
        ScopeBetween("bond1", "bond2")
    ])
    rule_10_fact = RuleFact([
        MatchCheckpoints(["bond"]),
        RenameArgs(["bond"], [["atom_type", "atom_id"]]),
        CrossAndGroupByArgs(["bond"], [["null"]]),
        ImposeWildcardCondition("atom_type", "!=", "H", True),
        CompareResultsQuantity("<=", 2),
        ReduceResult()
    ])
    rule_10 = JARLRule(rule_10_statement, rule_10_fact, rule_10_scope)

    rule_11_statement = (
        "# At most 4 bonds can happen between consecutive oxygen bonds\n"
        "for every at1='O',at2='O' and any aid1, aid2:\n"
        "between bond(at1, aid1) and next bond(at2, aid2):\n"
        "  for any atom_type!='O', atom_id:\n"
        "  bond(atom_type, atom_id) must happen at most 4 times\n"
    )
    rule_11_scope = RuleScope([
        MatchCheckpoints(["bond"]),
        RenameArgs(["bond", "bond"], [["at1", "aid1"], ["at2", "aid2"]]),
        CrossAndGroupByArgs(["bond", "bond"], [["at1"], ["at2"]]),
        ImposeIteratorCondition("at1", "=", "O", True),
        ImposeIteratorCondition("at2", "=", "O", True),
        ScopeBetween("bond1", "bond2")
    ])
    rule_11_fact = RuleFact([
        MatchCheckpoints(["bond"]),
        RenameArgs(["bond"], [["atom_type", "atom_id"]]),
        CrossAndGroupByArgs(["bond"], [["null"]]),
        ImposeWildcardCondition("atom_type", "!=", "O", True),
        CompareResultsQuantity("<=", 4),
        ReduceResult()
    ])
    rule_11 = JARLRule(rule_11_statement, rule_11_fact, rule_11_scope)

    def check_one_rule(self, rule):
        rc = RuleChecker([ rule ], self.log_file, self.checkpoint_file)
        rule = rc.check_all_rules()[0]
        self.assertTrue(rule.has_passed())

    def test_60_atoms_spawned(self):
        self.check_one_rule(self.rule_1)

    def test_60_atoms_died(self):
        self.check_one_rule(self.rule_2)

    def test_atoms_die_after_spawn(self):
        self.check_one_rule(self.rule_3)

    def test_60_atoms_bond(self):
        self.check_one_rule(self.rule_4)

    def test_atoms_bond_being_alive(self):
        self.check_one_rule(self.rule_5)

    def test_20_water_molecules_made(self):
        self.check_one_rule(self.rule_6)

    def test_hydrogen_bonds_twice_per_molecule(self):
        self.check_one_rule(self.rule_7)

    def test_oxygen_bonds_once_per_molecule(self):
        self.check_one_rule(self.rule_8)

    def test_3_atoms_bond_per_molecule(self):
        self.check_one_rule(self.rule_9)

    def test_at_most_2_bonds_between_hydrogen_bonds(self):
        self.check_one_rule(self.rule_10)

    def test_at_most_4_bonds_between_oxygen_bonds(self):
        self.check_one_rule(self.rule_11)

    def test_all_rules(self):
        all_rules = [
            self.rule_1,
            self.rule_2,
            self.rule_3,
            self.rule_4,
            self.rule_5,
            self.rule_6,
            self.rule_7,
            self.rule_8,
            self.rule_9,
            self.rule_10,
            self.rule_11,
        ]
        rc = RuleChecker(all_rules, self.log_file, self.checkpoint_file)
        all_rules = rc.check_all_rules()

        all_passed = True
        for rule in all_rules:
            if rule.has_failed(): all_passed = False

        #VerifierPrinter(True).print_verifier_summary(all_rules)
        self.assertTrue(all_passed)

@unittest.skip("Skipping because it is a load test")
class TestHighLoadH2O(unittest.TestCase):
    log_file = "/vagrant/resources/h2o_2.log"
    checkpoint_file = "/vagrant/resources/h2o.chk"

    rule_1_statement = (
        "# 1500 atoms are spawned in total\n"
        "for any atom_type, atom_id:\n"
        "atom_spawn(atom_type, atom_id) must happen 1500 times\n"
    )
    rule_1_fact = RuleFact([
        MatchCheckpoints(["atom_spawn"]),
        RenameArgs(["atom_spawn"], [["atom_type", "atom_id"]]),
        CrossAndGroupByArgs(["atom_spawn"], [["null"]]),
        CompareResultsQuantity("=", 1500),
        ReduceResult()
    ])
    rule_1 = JARLRule(rule_1_statement, rule_1_fact)

    rule_2_statement = (
        "# All 1500 atoms eventually die\n"
        "for any atom_type, atom_id:\n"
        "atom_die(atom_type, atom_id) must happen 1500 times\n"
    )
    rule_2_fact = RuleFact([
        MatchCheckpoints(["atom_die"]),
        RenameArgs(["atom_die"], [["atom_type", "atom_id"]]),
        CrossAndGroupByArgs(["atom_die"], [["null"]]),
        CompareResultsQuantity("=", 1500),
        ReduceResult()
    ])
    rule_2 = JARLRule(rule_2_statement, rule_2_fact)

    rule_3_statement = (
        "# Atoms die after spawning\n"
        "for every atom_id and any atom_type:\n"
        "after atom_spawn(atom_type, atom_id):\n"
        "  for every aid=atom_id and any at=atom_type:\n"
        "  atom_die(at, aid) must happen 1 times\n"
    )
    rule_3_scope = RuleScope([
        MatchCheckpoints(["atom_spawn"]),
        RenameArgs(["atom_spawn"], [["atom_type", "atom_id"]]),
        CrossAndGroupByArgs(["atom_spawn"], [["atom_id"]]),
        ScopeAfter("atom_spawn1")
    ])
    rule_3_fact = RuleFact([
        MatchCheckpoints(["atom_die"]),
        RenameArgs(["atom_die"], [["at", "aid"]]),
        CrossAndGroupByArgs(["atom_die"], [["aid"]]),
        ImposeIteratorCondition("aid", "=", "#atom_id", True),
        ImposeWildcardCondition("at", "=", "#atom_type", True),
        CompareResultsQuantity("=", 1),
        ReduceResult()
    ])
    rule_3 = JARLRule(rule_3_statement, rule_3_fact, rule_3_scope)
    rule_3.set_dynamic_scope_arg("atom_id", True)
    rule_3.set_dynamic_scope_arg("atom_type", True)

    rule_4_statement = (
        "# All 1500 atoms eventually bond\n"
        "for any atom_type, atom_id:\n"
        "bond(atom_type, atom_id) must happen 1500 times\n"
    )
    rule_4_fact = RuleFact([
        MatchCheckpoints(["bond"]),
        RenameArgs(["bond"], [["atom_type", "atom_id"]]),
        CrossAndGroupByArgs(["bond"], [["null"]]),
        CompareResultsQuantity("=", 1500),
        ReduceResult()
    ])
    rule_4 = JARLRule(rule_4_statement, rule_4_fact)

    rule_5_statement = (
        "# Atoms bond while being alive\n"
        "for every aid1, aid2=aid1 and any at1, at2=at1:\n"
        "between atom_spawn(at1, aid1) and next atom_die(at2, aid2):\n"
        "  for every atom_id=aid1 and any atom_type=at1:\n"
        "  bond(atom_type, atom_id) must happen 1 times\n"
    )
    rule_5_scope = RuleScope([
        MatchCheckpoints(["atom_spawn", "atom_die"]),
        RenameArgs(["atom_spawn", "atom_die"], [["at1", "aid1"], ["at2", "aid2"]]),
        CrossAndGroupByArgs(["atom_spawn", "atom_die"], [["aid1"], ["aid2"]]),
        ImposeIteratorCondition("aid1", "=", "aid2"),
        ScopeBetween("atom_spawn1", "atom_die2")
    ])
    rule_5_fact = RuleFact([
        MatchCheckpoints(["bond"]),
        RenameArgs(["bond"], [["atom_type", "atom_id"]]),
        CrossAndGroupByArgs(["bond"], [["atom_id"]]),
        ImposeIteratorCondition("atom_id", "=", "#aid1", True),
        ImposeWildcardCondition("atom_type", "=", "#at1", True),
        CompareResultsQuantity("=", 1),
        ReduceResult()
    ])
    rule_5 = JARLRule(rule_5_statement, rule_5_fact, rule_5_scope)
    rule_5.set_dynamic_scope_arg("aid1", True)
    rule_5.set_dynamic_scope_arg("at1", True)

    rule_6_statement = (
        "# 500 water molecules are made\n"
        "water_made must happen 20 times\n"
    )
    rule_6_fact = RuleFact([
        MatchCheckpoints(["water_made"]),
        RenameArgs(["water_made"], [["null"]]),
        CrossAndGroupByArgs(["water_made"], [["null"]]),
        CompareResultsQuantity("=", 500),
        ReduceResult()
    ])
    rule_6 = JARLRule(rule_6_statement, rule_6_fact)

    rule_7_statement = (
        "# 2 hydrogen atoms must bond to make a new water molecule\n"
        "between water_made and next water_made:\n"
        "  for every atom_type='H' and any atom_id:\n"
        "  bond(atom_type, atom_id) must happen 2 times\n"
    )
    rule_7_scope = RuleScope([
        MatchCheckpoints(["water_made"]),
        RenameArgs(["water_made"], [["null"]]),
        CrossAndGroupByArgs(["water_made", "water_made"], [["null"], ["null"]]),
        ScopeBetween("water_made1", "water_made2")
    ])
    rule_7_fact = RuleFact([
        MatchCheckpoints(["bond"]),
        RenameArgs(["bond"], [["atom_type", "atom_id"]]),
        CrossAndGroupByArgs(["bond"], [["atom_type"]]),
        ImposeIteratorCondition("atom_type", "=", "H", True),
        CompareResultsQuantity("=", 2),
        ReduceResult()
    ])
    rule_7 = JARLRule(rule_7_statement, rule_7_fact, rule_7_scope)

    rule_8_statement = (
        "# 1 oxygen atom must bond to make a new water molecule\n"
        "between water_made and next water_made:\n"
        "  for every atom_type='O' and any atom_id:\n"
        "  bond(atom_type, atom_id) must happen 1 times\n"
    )
    rule_8_scope = RuleScope([
        MatchCheckpoints(["water_made"]),
        RenameArgs(["water_made"], [["null"]]),
        CrossAndGroupByArgs(["water_made", "water_made"], [["null"], ["null"]]),
        ScopeBetween("water_made1", "water_made2")
    ])
    rule_8_fact = RuleFact([
        MatchCheckpoints(["bond"]),
        RenameArgs(["bond"], [["atom_type", "atom_id"]]),
        CrossAndGroupByArgs(["bond"], [["atom_type"]]),
        ImposeIteratorCondition("atom_type", "=", "O", True),
        CompareResultsQuantity("=", 1),
        ReduceResult()
    ])
    rule_8 = JARLRule(rule_8_statement, rule_8_fact, rule_8_scope)

    rule_9_statement = (
        "# In total, 3 atoms bond to make a new water molecule\n"
        "between water_made and next water_made:\n"
        "  for any atom_type, atom_id:\n"
        "  bond(atom_type, atom_id) must happen 3 times\n"
    )
    rule_9_scope = RuleScope([
        MatchCheckpoints(["water_made"]),
        RenameArgs(["water_made"], [["null"]]),
        CrossAndGroupByArgs(["water_made", "water_made"], [["null"], ["null"]]),
        ScopeBetween("water_made1", "water_made2")
    ])
    rule_9_fact = RuleFact([
        MatchCheckpoints(["bond"]),
        RenameArgs(["bond"], [["atom_type", "atom_id"]]),
        CrossAndGroupByArgs(["bond"], [["null"]]),
        CompareResultsQuantity("=", 3),
        ReduceResult()
    ])
    rule_9 = JARLRule(rule_9_statement, rule_9_fact, rule_9_scope)

    rule_10_statement = (
        "# At most 2 bonds can happen between consecutive hydrogen bonds\n"
        "for every at1='H',at2='H' and any aid1, aid2:\n"
        "between bond(at1, aid1) and next bond(at2, aid2):\n"
        "  for any atom_type!='H', atom_id:\n"
        "  bond(atom_type, atom_id) must happen at most 2 times\n"
    )
    rule_10_scope = RuleScope([
        MatchCheckpoints(["bond"]),
        RenameArgs(["bond", "bond"], [["at1", "aid1"], ["at2", "aid2"]]),
        CrossAndGroupByArgs(["bond", "bond"], [["at1"], ["at2"]]),
        ImposeIteratorCondition("at1", "=", "H", True),
        ImposeIteratorCondition("at2", "=", "H", True),
        ScopeBetween("bond1", "bond2")
    ])
    rule_10_fact = RuleFact([
        MatchCheckpoints(["bond"]),
        RenameArgs(["bond"], [["atom_type", "atom_id"]]),
        CrossAndGroupByArgs(["bond"], [["null"]]),
        ImposeWildcardCondition("atom_type", "!=", "H", True),
        CompareResultsQuantity("<=", 2),
        ReduceResult()
    ])
    rule_10 = JARLRule(rule_10_statement, rule_10_fact, rule_10_scope)

    rule_11_statement = (
        "# At most 4 bonds can happen between consecutive oxygen bonds\n"
        "for every at1='O',at2='O' and any aid1, aid2:\n"
        "between bond(at1, aid1) and next bond(at2, aid2):\n"
        "  for any atom_type!='O', atom_id:\n"
        "  bond(atom_type, atom_id) must happen at most 4 times\n"
    )
    rule_11_scope = RuleScope([
        MatchCheckpoints(["bond"]),
        RenameArgs(["bond", "bond"], [["at1", "aid1"], ["at2", "aid2"]]),
        CrossAndGroupByArgs(["bond", "bond"], [["at1"], ["at2"]]),
        ImposeIteratorCondition("at1", "=", "O", True),
        ImposeIteratorCondition("at2", "=", "O", True),
        ScopeBetween("bond1", "bond2")
    ])
    rule_11_fact = RuleFact([
        MatchCheckpoints(["bond"]),
        RenameArgs(["bond"], [["atom_type", "atom_id"]]),
        CrossAndGroupByArgs(["bond"], [["null"]]),
        ImposeWildcardCondition("atom_type", "!=", "O", True),
        CompareResultsQuantity("<=", 4),
        ReduceResult()
    ])
    rule_11 = JARLRule(rule_11_statement, rule_11_fact, rule_11_scope)

    def check_one_rule(self, rule):
        rc = RuleChecker([ rule ], self.log_file, self.checkpoint_file)
        rule = rc.check_all_rules()[0]
        self.assertTrue(rule.has_passed())

    def test_1500_atoms_spawned(self):
        self.check_one_rule(self.rule_1)

    def test_1500_atoms_died(self):
        self.check_one_rule(self.rule_2)

    def test_atoms_die_after_spawn(self):
        self.check_one_rule(self.rule_3)

    def test_1500_atoms_bond(self):
        self.check_one_rule(self.rule_4)

    def test_atoms_bond_being_alive(self):
        self.check_one_rule(self.rule_5)

    def test_500_water_molecules_made(self):
        self.check_one_rule(self.rule_6)

    def test_hydrogen_bonds_twice_per_molecule(self):
        self.check_one_rule(self.rule_7)

    def test_oxygen_bonds_once_per_molecule(self):
        self.check_one_rule(self.rule_8)

    def test_3_atoms_bond_per_molecule(self):
        self.check_one_rule(self.rule_9)

    def test_at_most_2_bonds_between_hydrogen_bonds(self):
        self.check_one_rule(self.rule_10)

    def test_at_most_4_bonds_between_oxygen_bonds(self):
        self.check_one_rule(self.rule_11)

    def test_all_rules(self):
        all_rules = [
            self.rule_1,
            self.rule_2,
            self.rule_3,
            self.rule_4,
            self.rule_5,
            self.rule_6,
            self.rule_7,
            self.rule_8,
            self.rule_9,
            self.rule_10,
            self.rule_11,
        ]
        rc = RuleChecker(all_rules, self.log_file, self.checkpoint_file)
        all_rules = rc.check_all_rules()

        all_passed = True
        for rule in all_rules:
            if rule.has_failed(): all_passed = False

        #VerifierPrinter(True).print_verifier_summary(all_rules)
        self.assertTrue(all_passed)


if __name__ == '__main__':
    unittest.main()