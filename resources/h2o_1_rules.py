from common.aggregation_steps import *
from common.jarl_rule import *

rule_1_statement = (
    "# 60 atoms are spawned in total\n"
    "for any atom_type, atom_id:\n"
    "atom_spawn(atom_type, atom_id) must happen 60 times\n"
)
rule_1_fact = RuleFact([
    MatchCheckpoints(["atom_spawn"]),
    RenameArgs([["atom_spawn", "atom_type", "atom_id"]]),
    CrossAndGroupByArgs([ ["atom_spawn", "null"] ]),
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
    RenameArgs([ ["atom_die", "atom_type", "atom_id"] ]),
    CrossAndGroupByArgs([ ["atom_die", "null"] ]),
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
    RenameArgs([["atom_spawn", "atom_type", "atom_id"]]),
    CrossAndGroupByArgs([ ["atom_spawn", "atom_id"] ]),
    ScopeAfter("atom_spawn1")
])
rule_3_fact = RuleFact([
    MatchCheckpoints(["atom_die"]),
    RenameArgs([ ["atom_die", "at", "aid"] ]),
    CrossAndGroupByArgs([ ["atom_die", "aid"] ]),
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
    RenameArgs([ ["bond", "atom_type", "atom_id"] ]),
    CrossAndGroupByArgs([ ["bond", "null"] ]),
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
    RenameArgs([["atom_spawn", "at1", "aid1"], ["atom_die", "at2", "aid2"]]),
    CrossAndGroupByArgs([ ["atom_spawn", "aid1"], ["atom_die", "aid2"] ]),
    ImposeIteratorCondition("aid1", "=", "aid2"),
    ScopeBetween("atom_spawn1", "atom_die2")
])
rule_5_fact = RuleFact([
    MatchCheckpoints(["bond"]),
    RenameArgs([ ["bond", "atom_type", "atom_id"] ]),
    CrossAndGroupByArgs([ ["bond", "atom_id"] ]),
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
    RenameArgs([ ["water_made", "null"] ]),
    CrossAndGroupByArgs([ ["water_made", "null"] ]),
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
    RenameArgs([ ["water_made", "null"] ]),
    CrossAndGroupByArgs([ ["water_made", "null"], ["water_made", "null"] ]),
    ScopeBetween("water_made1", "water_made2")
])
rule_7_fact = RuleFact([
    MatchCheckpoints(["bond"]),
    RenameArgs([ ["bond", "atom_type", "atom_id"] ]),
    CrossAndGroupByArgs([ ["bond", "atom_type"] ]),
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
    RenameArgs([["water_made", "null"]]),
    CrossAndGroupByArgs([ ["water_made", "null"], ["water_made", "null"] ]),
    ScopeBetween("water_made1", "water_made2")
])
rule_8_fact = RuleFact([
    MatchCheckpoints(["bond"]),
    RenameArgs([["bond", "atom_type", "atom_id"]]),
    CrossAndGroupByArgs([ ["bond", "atom_type"] ]),
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
    RenameArgs([["water_made", "null"]]),
    CrossAndGroupByArgs([ ["water_made", "null"], ["water_made", "null"] ]),
    ScopeBetween("water_made1", "water_made2")
])
rule_9_fact = RuleFact([
    MatchCheckpoints(["bond"]),
    RenameArgs([["bond", "atom_type", "atom_id"]]),
    CrossAndGroupByArgs([ ["bond", "null"] ]),
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
    RenameArgs([["bond", "at1", "aid1"], ["bond", "at2", "aid2"]]),
    CrossAndGroupByArgs([ ["bond", "at1"], ["bond", "at2"] ]),
    ImposeIteratorCondition("at1", "=", "H", True),
    ImposeIteratorCondition("at2", "=", "H", True),
    ScopeBetween("bond1", "bond2")
])
rule_10_fact = RuleFact([
    MatchCheckpoints(["bond"]),
    RenameArgs([["bond", "atom_type", "atom_id"]]),
    CrossAndGroupByArgs([ ["bond", "null"] ]),
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
    RenameArgs([["bond", "at1", "aid1"], ["bond", "at2", "aid2"]]),
    CrossAndGroupByArgs([ ["bond", "at1"], ["bond", "at2"] ]),
    ImposeIteratorCondition("at1", "=", "O", True),
    ImposeIteratorCondition("at2", "=", "O", True),
    ScopeBetween("bond1", "bond2")
])
rule_11_fact = RuleFact([
    MatchCheckpoints(["bond"]),
    RenameArgs([["bond", "atom_type", "atom_id"]]),
    CrossAndGroupByArgs([ ["bond", "null"] ]),
    ImposeWildcardCondition("atom_type", "!=", "O", True),
    CompareResultsQuantity("<=", 4),
    ReduceResult()
])
rule_11 = JARLRule(rule_11_statement, rule_11_fact, rule_11_scope)

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