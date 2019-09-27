from common.aggregation_steps import *
from common.jarl_rule import *

rule_1_statement = (
    "# Santa prepares his sleigh at most once when awake\n"
    "between santa_wake and next santa_sleep:\n"
    "  prepare_sleigh() must happen at most 1 times\n"
)
rule_1_scope = RuleScope([
    MatchCheckpoints(["santa_wake", "santa_sleep"]),
    RenameArgs([ ["santa_wake", "null"], ["santa_sleep", "null"] ]),
    CrossAndGroupByArgs(["santa_wake", "santa_sleep"], [["null"], ["null"]]),
    ScopeBetween("santa_wake1", "santa_sleep2")
])
rule_1_fact = RuleFact([
    MatchCheckpoints(["prepare_sleigh"]),
    RenameArgs([ ["prepare_sleigh", "null"] ]),
    CrossAndGroupByArgs(["prepare_sleigh"], [["null"]]),
    CompareResultsQuantity("<=", 1),
    ReduceResult()
])
rule_1 = JARLRule(rule_1_statement, rule_1_fact, rule_1_scope, passed_by_default=True)

rule_2_statement = (
    "# Santa helps the elves at most once when awake\n"
    "between santa_wake and next santa_sleep:\n"
    "  help_elves() must happen at most 1 times\n"
)
rule_2_scope = RuleScope([
    MatchCheckpoints(["santa_wake", "santa_sleep"]),
    RenameArgs([ ["santa_wake", "null"], ["santa_sleep", "null"] ]),
    CrossAndGroupByArgs(["santa_wake", "santa_sleep"], [["null"], ["null"]]),
    ScopeBetween("santa_wake1", "santa_sleep2")
])
rule_2_fact = RuleFact([
    MatchCheckpoints(["help_elves"]),
    RenameArgs([ ["help_elves", "null"] ]),
    CrossAndGroupByArgs(["help_elves"], [["null"]]),
    CompareResultsQuantity("<=", 1),
    ReduceResult()
])
rule_2 = JARLRule(rule_2_statement, rule_2_fact, rule_2_scope, passed_by_default=True)

rule_3_statement = (
    "# Santa cant prepare his sleigh if asleep\n"
    "between santa_sleep and next santa_wake:\n"
    "  prepare_sleigh() must happen 0 times\n"
)
rule_3_scope = RuleScope([
    MatchCheckpoints(["santa_sleep", "santa_wake"]),
    RenameArgs([ ["santa_sleep", "null"], ["santa_wake", "null"] ]),
    CrossAndGroupByArgs(["santa_sleep", "santa_wake"], [["null"], ["null"]]),
    ScopeBetween("santa_sleep1", "santa_wake2")
])
rule_3_fact = RuleFact([
    MatchCheckpoints(["prepare_sleigh"]),
    RenameArgs([ ["prepare_sleigh", "null"] ]),
    CrossAndGroupByArgs(["prepare_sleigh"], [["null"]]),
    CompareResultsQuantity("=", 0),
    ReduceResult()
])
rule_3 = JARLRule(rule_3_statement, rule_3_fact, rule_3_scope, passed_by_default=True)

rule_4_statement = (
    "# Santa cant help the elves if asleep\n"
    "between santa_sleep and next santa_wake:\n"
    "  help_elves() must happen 0 times\n"
)
rule_4_scope = RuleScope([
    MatchCheckpoints(["santa_sleep", "santa_wake"]),
    RenameArgs([ ["santa_sleep", "null"], ["santa_wake", "null"] ]),
    CrossAndGroupByArgs(["santa_sleep", "santa_wake"], [["null"], ["null"]]),
    ScopeBetween("santa_sleep1", "santa_wake2")
])
rule_4_fact = RuleFact([
    MatchCheckpoints(["help_elves"]),
    RenameArgs([ ["help_elves", "null"] ]),
    CrossAndGroupByArgs(["help_elves"], [["null"]]),
    CompareResultsQuantity("=", 0),
    ReduceResult()
])
rule_4 = JARLRule(rule_4_statement, rule_4_fact, rule_4_scope, passed_by_default=True)

rule_5_statement = (
    "# Elves leave only after getting help\n"
    "for every e1, e2=e1:\n"
    "between elf_arrive(e1) and next elf_leave(e2):\n"
    "  for every e=e1:\n"
    "  get_help(e) must happen 1 times\n"
)
rule_5_scope = RuleScope([
    MatchCheckpoints(["elf_arrive", "elf_leave"]),
    RenameArgs([ ["elf_arrive", "e1"], ["elf_leave", "e2"] ]),
    CrossAndGroupByArgs(["elf_arrive", "elf_leave"], [["e1"], ["e2"]]),
    ImposeIteratorCondition("e1", "=", "e2"),
    ScopeBetween("elf_arrive1", "elf_leave2")
])
rule_5_fact = RuleFact([
    MatchCheckpoints(["get_help"]),
    RenameArgs([ ["get_help", "e"] ]),
    CrossAndGroupByArgs(["get_help"], [["e"]]),
    ImposeIteratorCondition("e", "=", "#e1", True),
    CompareResultsQuantity("=", 1),
    ReduceResult()
])
rule_5 = JARLRule(rule_5_statement, rule_5_fact, rule_5_scope, passed_by_default=False)
rule_5.set_dynamic_scope_arg("e1", True)

rule_6_statement = (
    "# Reindeer leave only after getting hitched\n"
    "for every r1, r2=r1:\n"
    "between reindeer_arrive(r1) and next reindeer_leave(r2):\n"
    "  for every r=r1:\n"
    "  get_hitched(r) must happen 1 times\n"
)
rule_6_scope = RuleScope([
    MatchCheckpoints(["reindeer_arrive", "reindeer_leave"]),
    RenameArgs([ ["reindeer_arrive", "r1"], ["reindeer_leave", "r2"] ]),
    CrossAndGroupByArgs(["reindeer_arrive", "reindeer_leave"], [["r1"], ["r2"]]),
    ImposeIteratorCondition("r1", "=", "r2"),
    ScopeBetween("reindeer_arrive1", "reindeer_leave2")
])
rule_6_fact = RuleFact([
    MatchCheckpoints(["get_hitched"]),
    RenameArgs([ ["get_hitched", "r"] ]),
    CrossAndGroupByArgs(["get_hitched"], [["r"]]),
    ImposeIteratorCondition("r", "=", "#r1", True),
    CompareResultsQuantity("=", 1),
    ReduceResult()
])
rule_6 = JARLRule(rule_6_statement, rule_6_fact, rule_6_scope, passed_by_default=False)
rule_6.set_dynamic_scope_arg("r1", True)

rule_7_statement = (
    "# Santa helps the elves in groups of 3\n"
    "for every e:\n"
    "between get_help(e) and previous help_elves():\n"
    "  for any elf:\n"
    "  get_help(elf) must happen at most 3 times\n"
)
rule_7_scope = RuleScope([
    MatchCheckpoints(["get_help", "help_elves"]),
    RenameArgs([ ["get_help", "e"], ["help_elves", "null"] ]),
    CrossAndGroupByArgs(["get_help", "help_elves"], [["e"], ["null"]]),
    ScopeBetween("get_help1", "help_elves2", False)
])
rule_7_fact = RuleFact([
    MatchCheckpoints(["get_help"]),
    RenameArgs([ ["get_help", "elf"] ]),
    CrossAndGroupByArgs(["get_help"], [["null"]]),
    CompareResultsQuantity("<=", 3),
    ReduceResult()
])
rule_7 = JARLRule(rule_7_statement, rule_7_fact, rule_7_scope, passed_by_default=True)

rule_8_statement = (
    "# Santa hitches the reindeers in groups of 9\n"
    "for every r:\n"
    "between get_hitched(r) and previous prepare_sleigh():\n"
    "  for any reindeer:\n"
    "  get_hitched(reindeer) must happen at most 9 times\n"
)
rule_8_scope = RuleScope([
    MatchCheckpoints(["get_hitched", "prepare_sleigh"]),
    RenameArgs([ ["get_hitched", "r"], ["prepare_sleigh", "null"] ]),
    CrossAndGroupByArgs(["get_hitched", "prepare_sleigh"], [["r"], ["null"]]),
    ScopeBetween("get_hitched1", "prepare_sleigh2", False)
])
rule_8_fact = RuleFact([
    MatchCheckpoints(["get_hitched"]),
    RenameArgs([ ["get_hitched", "reindeer"] ]),
    CrossAndGroupByArgs(["get_hitched"], [["null"]]),
    CompareResultsQuantity("<=", 9),
    ReduceResult()
])
rule_8 = JARLRule(rule_8_statement, rule_8_fact, rule_8_scope, passed_by_default=True)

rule_9_statement = (
    "# Elves cannot be helped if they dont arrive with Santa\n"
    "for every e1, e2=e1:\n"
    "between elf_leave(e1) and next elf_arrive(e2):\n"
    "  for every e=e1:\n"
    "  get_help(e) must happen 0 times\n"
)
rule_9_scope = RuleScope([
    MatchCheckpoints(["elf_leave", "elf_arrive"]),
    RenameArgs([ ["elf_leave", "e1"], ["elf_arrive", "e2"] ]),
    CrossAndGroupByArgs(["elf_leave", "elf_arrive"], [["e1"], ["e2"]]),
    ImposeIteratorCondition("e1", "=", "e2"),
    ScopeBetween("elf_leave1", "elf_arrive2")
])
rule_9_fact = RuleFact([
    MatchCheckpoints(["get_help"]),
    RenameArgs([ ["get_help","e"] ]),
    CrossAndGroupByArgs(["get_help"], [["e"]]),
    ImposeIteratorCondition("e", "=", "#e1", True),
    CompareResultsQuantity("=", 0),
    ReduceResult()
])
rule_9 = JARLRule(rule_9_statement, rule_9_fact, rule_9_scope, passed_by_default=True)
rule_9.set_dynamic_scope_arg("e1", True)

rule_10_statement = (
    "# Reindeers cannot be hitched if they dont arrive with Santa\n"
    "for every r1, r2=r1:\n"
    "between reindeer_leave(r1) and next reindeer_arrive(r2):\n"
    "  for every r=r1:\n"
    "  get_hitched(r) must happen 0 times\n"
)
rule_10_scope = RuleScope([
    MatchCheckpoints(["reindeer_leave", "reindeer_arrive"]),
    RenameArgs([ ["reindeer_leave", "r1"], ["reindeer_arrive", "r2"] ]),
    CrossAndGroupByArgs(["reindeer_leave", "reindeer_arrive"], [["r1"], ["r2"]]),
    ImposeIteratorCondition("r1", "=", "r2"),
    ScopeBetween("reindeer_leave1", "reindeer_arrive2")
])
rule_10_fact = RuleFact([
    MatchCheckpoints(["get_hitched"]),
    RenameArgs([ ["get_hitched", "r"] ]),
    CrossAndGroupByArgs(["get_hitched"], [["r"]]),
    ImposeIteratorCondition("r", "=", "#r1", True),
    CompareResultsQuantity("=", 0),
    ReduceResult()
])
rule_10 = JARLRule(rule_10_statement, rule_10_fact, rule_10_scope, passed_by_default=True)
rule_10.set_dynamic_scope_arg("r1", True)

rule_11_statement = (
    "# Reindeer gets hitched after Santa prepares his sleigh\n"
    "for every r1, r2=r1:\n"
    "between reindeer_arrive(r1) and next reindeer_leave(r2):\n"
    "  for every r=r1:\n"
    "  prepare_sleigh() must precede get_hitched(r)\n"
)
rule_11_scope = RuleScope([
    MatchCheckpoints(["reindeer_arrive", "reindeer_leave"]),
    RenameArgs([ ["reindeer_arrive", "r1"], ["reindeer_leave", "r2"] ]),
    CrossAndGroupByArgs(["reindeer_arrive", "reindeer_leave"], [["r1"], ["r2"]]),
    ImposeIteratorCondition("r1", "=", "r2"),
    ScopeBetween("reindeer_arrive1", "reindeer_leave2")
])
rule_11_fact = RuleFact([
    MatchCheckpoints(["prepare_sleigh", "get_hitched"]),
    RenameArgs([ ["prepare_sleigh", "null"], ["get_hitched", "r"] ]),
    CrossAndGroupByArgs(["prepare_sleigh", "get_hitched"], [["null"], ["r"]]),
    ImposeIteratorCondition("r", "=", "#r1", True),
    CompareResultsPrecedence("prepare_sleigh1", "get_hitched2"),
    ReduceResult()
])
rule_11 = JARLRule(rule_11_statement, rule_11_fact, rule_11_scope)
rule_11.set_dynamic_scope_arg("r1", True)




all_rules = [
    #rule_1,
    #rule_2,
    #rule_3,
    #rule_4,
    #rule_5,
    #rule_6,
    #rule_7,
    #rule_8,
    #rule_9,
    #rule_10,
    rule_11,
]