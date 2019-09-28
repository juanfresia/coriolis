from common.aggregation_steps import *
from common.jarl_rule import *

rule_1_statement = (
    "# m is called for every i,j combination\n"
    "for every i, j:\n"
    "m(i, j) must happen at least 1 time\n"
)

rule_1_fact = RuleFact([
    MatchCheckpoints(["m"]),
    RenameArgs(["m"], [["i", "j"]]),
    CrossAndGroupByArgs(["m"], [["i", "j"]]),
    #CompareResultsQuantity("=", 1),
    #ReduceResult()
])
rule_1 = JARLRule(rule_1_statement, rule_1_fact)




all_rules = [
    rule_1,
]