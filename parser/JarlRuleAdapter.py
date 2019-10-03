from common.aggregation_steps import *
from common.jarl_rule import *

class JarlRuleAdapter():
    def rule_to_steps(self, rule):
        rule_header = "readers_read_two_times"
        rule_fact = RuleFact([
            MatchCheckpoints(["read_room"]),
            RenameArgs([["read_room", "r", "room", "msg"]]),
            CrossAndGroupByArgs([["read_room", "r"]]),
            CompareResultsQuantity("=", 2),
            ReduceResult()
        ])
        expected_rule_adapted = JARLRule("", rule_header, rule_fact, passed_by_default=False)

        return expected_rule_adapted
