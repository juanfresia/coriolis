from common.aggregation_steps import *
from common.jarl_rule import *


rule_1_statement = (
    "# 60 atoms are spawned in total\n"
    "rule sixty_spawn\n"
    "for any atom_type, atom_id:\n"
    "atom_spawn(atom_type, atom_id) must happen 60 times\n"
)
rule_1_header = "sixty_spawn"
rule_1_fact = RuleFact([
    MatchCheckpoints(["atom_spawn"]),
    RenameArgs([["atom_spawn", "atom_type", "atom_id"]]),
    CrossAndGroupByArgs([["atom_spawn"]]),
    CompareResultsQuantity("=", 60),
    ReduceResult()
])
rule_1 = JARLRule(rule_1_statement, rule_1_header, rule_1_fact, passed_by_default=False)

rule_2_statement = (
    "# All 60 atoms eventually die\n"
    "rule sixty_die\n"
    "for any atom_type, atom_id:\n"
    "atom_die(atom_type, atom_id) must happen 60 times\n"
)
rule_2_header = "sixty_die"
rule_2_fact = RuleFact([
    MatchCheckpoints(["atom_die"]),
    RenameArgs([["atom_die", "atom_type", "atom_id"]]),
    CrossAndGroupByArgs([["atom_die"]]),
    CompareResultsQuantity("=", 60),
    ReduceResult()
])
rule_2 = JARLRule(rule_2_statement, rule_2_header, rule_2_fact, passed_by_default=False)

rule_3_statement = (
    "# Atoms die after spawning\n"
    "rule die_after_spawn\n"
    "for every atom_id and any atom_type:\n"
    "after atom_spawn(atom_type, atom_id):\n"
    "  for every aid and any aty with aid=atom_id, aty=atom_type:\n"
    "  atom_die(aty, aid) must happen 1 times\n"
)
rule_3_header = "die_after_spawn"
rule_3_scope = RuleScope([
    MatchCheckpoints(["atom_spawn"]),
    RenameArgs([["atom_spawn", "atom_type", "atom_id"]]),
    CrossAndGroupByArgs([["atom_spawn", "atom_id"]]),
    ScopeAfter("atom_spawn")
])
rule_3_fact = RuleFact([
    MatchCheckpoints(["atom_die"]),
    RenameArgs([["atom_die", "aty", "aid"]]),
    CrossAndGroupByArgs([["atom_die", "aid"]]),
    ImposeIteratorCondition("aid", "=", "#atom_id", True),
    ImposeWildcardCondition("aty", "=", "#atom_type", True),
    CompareResultsQuantity("=", 1),
    ReduceResult()
])
rule_3 = JARLRule(rule_3_statement, rule_3_header, rule_3_fact, rule_3_scope, passed_by_default=True)
rule_3.set_dynamic_scope_arg("atom_id", True)
rule_3.set_dynamic_scope_arg("atom_type", True)

rule_4_statement = (
    "# All 60 atoms eventually bond\n"
    "rule sixty_bond\n"
    "for any atom_type, atom_id:\n"
    "bond(atom_type, atom_id) must happen 60 times\n"
)
rule_4_header = "sixty_bond"
rule_4_fact = RuleFact([
    MatchCheckpoints(["bond"]),
    RenameArgs([["bond", "atom_type", "atom_id"]]),
    CrossAndGroupByArgs([["bond"]]),
    CompareResultsQuantity("=", 60),
    ReduceResult()
])
rule_4 = JARLRule(rule_4_statement, rule_4_header, rule_4_fact, passed_by_default=False)

rule_5_statement = (
    "# Atoms bond while being alive\n"
    "rule bond_while_alive\n"
    "for every aid1, aid2 and any at1, at2 with aid2=aid1, at2=at1:\n"
    "between atom_spawn(at1, aid1) and next atom_die(at2, aid2):\n"
    "  for every atom_id and any atom_type with atom_id=aid1, atom_type=at1:\n"
    "  bond(atom_type, atom_id) must happen 1 times\n"
)
rule_5_header = "bond_while_alive"
rule_5_scope = RuleScope([
    MatchCheckpoints(["atom_spawn", "atom_die"]),
    RenameArgs([["atom_spawn", "at1", "aid1"], ["atom_die", "at2", "aid2"]]),
    CrossAndGroupByArgs([["atom_spawn", "aid1"], ["atom_die", "aid2"]]),
    ImposeIteratorCondition("aid2", "=", "aid1"),
    ImposeWildcardCondition("at2", "=", "at1"),
    ScopeBetween("atom_spawn", "atom_die")
])
rule_5_fact = RuleFact([
    MatchCheckpoints(["bond"]),
    RenameArgs([["bond", "atom_type", "atom_id"]]),
    CrossAndGroupByArgs([["bond", "atom_id"]]),
    ImposeIteratorCondition("atom_id", "=", "#aid1", True),
    ImposeWildcardCondition("atom_type", "=", "#at1", True),
    CompareResultsQuantity("=", 1),
    ReduceResult()
])
rule_5 = JARLRule(rule_5_statement, rule_5_header, rule_5_fact, rule_5_scope, passed_by_default=True)
rule_5.set_dynamic_scope_arg("at1", True)
rule_5.set_dynamic_scope_arg("aid1", True)

rule_6_statement = (
    "# 20 water molecules are made\n"
    "rule twenty_molecules_made\n"
    "water_made() must happen 20 times\n"
)
rule_6_header = "twenty_molecules_made"
rule_6_fact = RuleFact([
    MatchCheckpoints(["water_made"]),
    CrossAndGroupByArgs([["water_made"]]),
    CompareResultsQuantity("=", 20),
    ReduceResult()
])
rule_6 = JARLRule(rule_6_statement, rule_6_header, rule_6_fact, passed_by_default=False)

rule_7_statement = (
    "# 2 hydrogen atoms must bond to make a new water molecule\n"
    "rule two_hydrogen_per_molecule\n"
    "between water_made() and next water_made():\n"
    "  for every atom_type and any atom_id with atom_type='H':\n"
    "  bond(atom_type, atom_id) must happen 2 times\n"
)
rule_7_header = "two_hydrogen_per_molecule"
rule_7_scope = RuleScope([
    MatchCheckpoints(["water_made"]),
    CrossAndGroupByArgs([["water_made"], ["water_made"]]),
    ScopeBetween("water_made", "water_made")
])
rule_7_fact = RuleFact([
    MatchCheckpoints(["bond"]),
    RenameArgs([["bond", "atom_type", "atom_id"]]),
    CrossAndGroupByArgs([["bond", "atom_type"]]),
    ImposeIteratorCondition("atom_type", "=", "H", True),
    CompareResultsQuantity("=", 2),
    ReduceResult()
])
rule_7 = JARLRule(rule_7_statement, rule_7_header, rule_7_fact, rule_7_scope, passed_by_default=True)

rule_8_statement = (
    "# 1 oxygen atom must bond to make a new water molecule\n"
    "rule one_oxygen_per_molecule\n"
    "between water_made() and next water_made():\n"
    "  for every atom_type and any atom_id with atom_type='O':\n"
    "  bond(atom_type, atom_id) must happen 1 times\n"
)
rule_8_header = "one_oxygen_per_molecule"
rule_8_scope = RuleScope([
    MatchCheckpoints(["water_made"]),
    CrossAndGroupByArgs([["water_made"], ["water_made"]]),
    ScopeBetween("water_made", "water_made")
])
rule_8_fact = RuleFact([
    MatchCheckpoints(["bond"]),
    RenameArgs([["bond", "atom_type", "atom_id"]]),
    CrossAndGroupByArgs([["bond", "atom_type"]]),
    ImposeIteratorCondition("atom_type", "=", "O", True),
    CompareResultsQuantity("=", 1),
    ReduceResult()
])
rule_8 = JARLRule(rule_8_statement, rule_8_header, rule_8_fact, rule_8_scope, passed_by_default=True)

rule_9_statement = (
    "# In total, 3 atoms bond to make a new water molecule\n"
    "rule three_bonds\n"
    "between water_made() and next water_made():\n"
    "  for any atom_type, atom_id:\n"
    "  bond(atom_type, atom_id) must happen 3 times\n"
)
rule_9_header = "three_bonds"
rule_9_scope = RuleScope([
    MatchCheckpoints(["water_made"]),
    CrossAndGroupByArgs([["water_made"], ["water_made"]]),
    ScopeBetween("water_made", "water_made")
])
rule_9_fact = RuleFact([
    MatchCheckpoints(["bond"]),
    RenameArgs([["bond", "atom_type", "atom_id"]]),
    CrossAndGroupByArgs([["bond"]]),
    CompareResultsQuantity("=", 3),
    ReduceResult()
])
rule_9 = JARLRule(rule_9_statement, rule_9_header, rule_9_fact, rule_9_scope, passed_by_default=False)

rule_10_statement = (
    "# At most 2 bonds can happen between consecutive hydrogen bonds\n"
    "rule bonds_between_hydrogen\n"
    "for every at1, at2 and any aid1, aid2 with at1='H', at2='H':\n"
    "between bond(at1, aid1) and next bond(at2, aid2):\n"
    "  for any atom_type, atom_id with atom_type!='H':\n"
    "  bond(atom_type, atom_id) must happen at most 2 times\n"
)
rule_10_header = "bonds_between_hydrogen"
rule_10_scope = RuleScope([
    MatchCheckpoints(["bond"]),
    RenameArgs([["bond", "at1", "aid1"], ["bond", "at2", "aid2"]]),
    CrossAndGroupByArgs([["bond", "at1"], ["bond", "at2"]]),
    ImposeIteratorCondition("at1", "=", "H", True),
    ImposeIteratorCondition("at2", "=", "H", True),
    ScopeBetween("bond", "bond")
])
rule_10_fact = RuleFact([
    MatchCheckpoints(["bond"]),
    RenameArgs([["bond", "atom_type", "atom_id"]]),
    CrossAndGroupByArgs([["bond"]]),
    ImposeWildcardCondition("atom_type", "!=", "H", True),
    CompareResultsQuantity("<=", 2),
    ReduceResult()
])
rule_10 = JARLRule(rule_10_statement, rule_10_header, rule_10_fact, rule_10_scope, passed_by_default=True)

rule_11_statement = (
    "# At most 4 bonds can happen between consecutive oxygen bonds\n"
    "rule bonds_between_oxygen\n"
    "for every at1, at2 and any aid1, aid2 with at1='O', at2='O':\n"
    "between bond(at1, aid1) and next bond(at2, aid2):\n"
    "  for any atom_type, atom_id with atom_type!='O':\n"
    "  bond(atom_type, atom_id) must happen at most 4 times\n"
)
rule_11_header = "bonds_between_oxygen"
rule_11_scope = RuleScope([
    MatchCheckpoints(["bond"]),
    RenameArgs([["bond", "at1", "aid1"], ["bond", "at2", "aid2"]]),
    CrossAndGroupByArgs([["bond", "at1"], ["bond", "at2"]]),
    ImposeIteratorCondition("at1", "=", "O", True),
    ImposeIteratorCondition("at2", "=", "O", True),
    ScopeBetween("bond", "bond")
])
rule_11_fact = RuleFact([
    MatchCheckpoints(["bond"]),
    RenameArgs([["bond", "atom_type", "atom_id"]]),
    CrossAndGroupByArgs([["bond"]]),
    ImposeWildcardCondition("atom_type", "!=", "O", True),
    CompareResultsQuantity("<=", 4),
    ReduceResult()
])
rule_11 = JARLRule(rule_11_statement, rule_11_header, rule_11_fact, rule_11_scope, passed_by_default=True)

all_rules = [
    rule_1,
    rule_2,
    rule_3,
    rule_4,
    rule_5,
    rule_6,
    rule_7,
    rule_8,
    rule_9,
    rule_10,
    rule_11,
]
