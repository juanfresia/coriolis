from common.aggregation_steps import *
from common.jarl_rule import *

rule_1_statement = (
    "# Every item is produced only once\n"
    "rule produce_once\n"
    "for every i and any p:\n"
    "produce(p, i) must happen 1 time\n"
)
rule_1_header = "produce_once"
rule_1_fact = RuleFact([
    MatchCheckpoints(["produce"]),
    RenameArgs([["produce", "p", "i"]]),
    CrossAndGroupByArgs([["produce", "i"]]),
    CompareResultsQuantity("=", 1),
    ReduceResult()
])
rule_1 = JARLRule(rule_1_statement, rule_1_header, rule_1_fact, passed_by_default=True)

rule_2_statement = (
    "# Every item is consumed only once\n"
    "rule consume_once\n"
    "for every i and any c:\n"
    "consume(c, i) must happen 1 time\n"
)
rule_2_header = "consume_once"
rule_2_fact = RuleFact([
    MatchCheckpoints(["consume"]),
    RenameArgs([["consume", "c", "i"]]),
    CrossAndGroupByArgs([["consume", "i"]]),
    CompareResultsQuantity("=", 1),
    ReduceResult()
])
rule_2 = JARLRule(rule_2_statement, rule_2_header, rule_2_fact, passed_by_default=True)

rule_3_statement = (
    "# 10 items are produced\n"
    "rule produce_ten\n"
    "for any p, i:\n"
    "produce(p, i) must happen 10 times\n"
)
rule_3_header = "produce_ten"
rule_3_fact = RuleFact([
    MatchCheckpoints(["produce"]),
    RenameArgs([["produce", "p", "i"]]),
    CrossAndGroupByArgs([["produce"]]),
    CompareResultsQuantity("=", 10),
    ReduceResult()
])
rule_3 = JARLRule(rule_3_statement, rule_3_header, rule_3_fact, passed_by_default=False)

rule_4_statement = (
    "# 10 items are consumed\n"
    "rule consume_ten\n"
    "for any c, i:\n"
    "consume(c, i) must happen 10 times\n"
)
rule_4_header = "consume_ten"
rule_4_fact = RuleFact([
    MatchCheckpoints(["consume"]),
    RenameArgs([["consume", "c", "i"]]),
    CrossAndGroupByArgs([["consume"]]),
    CompareResultsQuantity("=", 10),
    ReduceResult()
])
rule_4 = JARLRule(rule_4_statement, rule_4_header, rule_4_fact, passed_by_default=False)

rule_5_statement = (
    "# Every item is produced before consumed\n"
    "rule produce_then_consume\n"
    "for every iid and any c:\n"
    "before consume(c, iid):\n"
    "  for every i and any p with i=iid:\n"
    "  produce(p, i) must happen 1 times\n"
)
rule_5_header = "produce_then_consume"
rule_5_scope = RuleScope([
    MatchCheckpoints(["consume"]),
    RenameArgs([["consume", "c", "iid"]]),
    CrossAndGroupByArgs([["consume", "iid"]]),
    ScopeBefore("consume")
])
rule_5_fact = RuleFact([
    MatchCheckpoints(["produce"]),
    RenameArgs([["produce", "p", "i"]]),
    CrossAndGroupByArgs([["produce", "i"]]),
    ImposeIteratorCondition("i", "=", "#iid", True),
    CompareResultsQuantity("=", 1),
    ReduceResult()
])
rule_5 = JARLRule(rule_5_statement, rule_5_header, rule_5_fact, rule_5_scope, passed_by_default=True)
rule_5.set_dynamic_scope_arg("iid", False)

rule_6_statement = (
    "# Items are produced in order\n"
    "rule produce_in_order\n"
    "for every i, j and any p, q with j>i:\n"
    "produce(p, i) must precede produce(q, j)\n"
)
rule_6_header = "produce_in_order"
rule_6_fact = RuleFact([
    MatchCheckpoints(["produce"]),
    RenameArgs([["produce", "p", "i"], ["produce", "q", "j"]]),
    CrossAndGroupByArgs([["produce", "i"], ["produce", "j"]]),
    ImposeIteratorCondition("j", ">", "i"),
    CompareResultsPrecedence("produce", "produce"),
    ReduceResult()
])
rule_6 = JARLRule(rule_6_statement, rule_6_header, rule_6_fact, passed_by_default=True)

rule_7_statement = (
    "# Items are consumed in order\n"
    "rule consume_in_order\n"
    "for every i, j and any c, d with j>i:\n"
    "consume(c, i) must precede consume(d, j)\n"
)
rule_7_header = "consume_in_order"
rule_7_fact = RuleFact([
    MatchCheckpoints(["consume"]),
    RenameArgs([["consume", "c", "i"], ["consume", "d", "j"]]),
    CrossAndGroupByArgs([["consume", "i"], ["consume", "j"]]),
    ImposeIteratorCondition("j", ">", "i"),
    CompareResultsPrecedence("consume", "consume"),
    ReduceResult()
])
rule_7 = JARLRule(rule_7_statement, rule_7_header, rule_7_fact, passed_by_default=True)

rule_8_statement = (
    "# The buffer size is 5\n"
    "rule buffer_size_five"
    "for any pid, cid, i1, i2:\n"
    "between produce(pid, i1) and next consume(cid, i2):\n"
    "  for any p, i:\n"
    "  produce(p, i) must happen at most 5 times\n"
)
rule_8_header = "buffer_size_five"
rule_8_scope = RuleScope([
    MatchCheckpoints(["produce", "consume"]),
    RenameArgs([["produce", "pid", "i1"], ["consume", "cid", "i2"]]),
    CrossAndGroupByArgs([["produce"], ["consume"]]),
    ScopeBetween("produce", "consume")
])
rule_8_fact = RuleFact([
    MatchCheckpoints(["produce"]),
    RenameArgs([["produce", "p", "i"]]),
    CrossAndGroupByArgs([["produce"]]),
    CompareResultsQuantity("<=", 5),
    ReduceResult()
])
rule_8 = JARLRule(rule_8_statement, rule_8_header, rule_8_fact, rule_8_scope, passed_by_default=True)

rule_9_statement = (
    "# Item is consumed only once (written differently)\n"
    "rule consume_once_alt\n"
    "for any cid, iid:\n"
    "after consume(cid, iid):\n"
    "  for every i and any c:\n"
    "  consume(c, i) must happen 1 times\n"
)
rule_9_header = "consume_once_alt"
rule_9_scope = RuleScope([
    MatchCheckpoints(["consume"]),
    RenameArgs([["consume", "cid", "iid"]]),
    CrossAndGroupByArgs([["consume"]]),
    ScopeAfter("consume")
])
rule_9_fact = RuleFact([
    MatchCheckpoints(["consume"]),
    RenameArgs([["consume", "c", "i"]]),
    CrossAndGroupByArgs([["consume", "i"]]),
    CompareResultsQuantity("=", 1),
    ReduceResult()
])
rule_9 = JARLRule(rule_9_statement, rule_9_header, rule_9_fact, rule_9_scope, passed_by_default=True)

rule_10_statement = (
    "# Item is produced only once (written differently)\n"
    "rule produce_once_alt\n"
    "for any pid, iid:\n"
    "before produce(pid, iid):\n"
    "  for every i and any p:\n"
    "  produce(p, i) must happen 1 times\n"
)
rule_10_header = "produce_once_alt"
rule_10_scope = RuleScope([
    MatchCheckpoints(["produce"]),
    RenameArgs([["produce", "pid", "iid"]]),
    CrossAndGroupByArgs([["produce"]]),
    ScopeBefore("produce")
])
rule_10_fact = RuleFact([
    MatchCheckpoints(["produce"]),
    RenameArgs([["produce", "p", "i"]]),
    CrossAndGroupByArgs([["produce", "i"]]),
    CompareResultsQuantity("=", 1),
    ReduceResult()
])
rule_10 = JARLRule(rule_10_statement, rule_10_header, rule_10_fact, rule_10_scope, passed_by_default=True)

rule_11_statement = (
    "# Consumer cannot consume items smaller than their own ID\n"
    "rule consume_smaller\n"
    "for every c, i with i<c:\n"
    "consume(c, i) must not happen\n"
)
rule_11_header = "consume_smaller"
rule_11_fact = RuleFact([
    MatchCheckpoints(["consume"]),
    RenameArgs([["consume", "c", "i"]]),
    CrossAndGroupByArgs([["consume", "c", "i"]]),
    ImposeIteratorCondition("i", "<", "c"),
    CompareResultsQuantity("=", 0),
    ReduceResult()
])
rule_11 = JARLRule(rule_11_statement, rule_11_header, rule_11_fact, passed_by_default=True)

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
