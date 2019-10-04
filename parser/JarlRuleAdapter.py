from common.aggregation_steps import *
from common.jarl_rule import *

class JarlRuleAdapter():

    def concat_checkpoint(self, chk):
        concat = [chk.name]
        concat += [arg for arg in chk.arguments]
        return concat

    def concat_checkpoint_only_iters(self, chk, iterators=[]):
        concat = [chk.name]
        concat += [arg for arg in chk.arguments if arg in iterators]
        return concat

    def get_rule_text(self, rule):
        return rule.text

    def get_rule_header(self, rule):
        return rule.name

    def get_rule_scope(self, rule):
        return None

    def get_rule_fact(self, rule):
        fact = rule.fact
        checkpoints = fact.facts[0].get_checkpoints()
        iterators = []
        if fact.filter:
            iterators = fact.filter.iterators

        fact_steps = []

        match_checkpoints = MatchCheckpoints([chk.name for chk in checkpoints])
        fact_steps.append(match_checkpoints)

        flattened_checkpoints = [self.concat_checkpoint(chk) for chk in checkpoints]
        rename_args = RenameArgs(flattened_checkpoints)
        fact_steps.append(rename_args)

        flattened_checkpoints = [self.concat_checkpoint_only_iters(chk, iterators) for chk in checkpoints]
        cross_and_group = CrossAndGroupByArgs(flattened_checkpoints)
        fact_steps.append(cross_and_group)

        requirement = fact.facts[0].requirement
        if requirement.get_checkpoints():
            # It is a precedence requirement
            compare_results = CompareResultsPrecedence(fact.checkpoint.name, requirement.checkpoint.name)
        else:
            # It is an order requirement
            compare_results = CompareResultsQuantity(requirement.type.value, requirement.count)
        fact_steps.append(compare_results)

        fact_steps.append(ReduceResult())

        return RuleFact(fact_steps)

    def rule_to_steps(self, rule):
        # TODO add validation of the rule here

        # Get each part of a rule
        rule_text = self.get_rule_text(rule)
        rule_header = self.get_rule_header(rule)
        rule_scope = self.get_rule_scope(rule)
        rule_fact = self.get_rule_fact(rule)

        # Compose rule and return
        return JARLRule(rule_text, rule_header, rule_fact, rule_scope, passed_by_default=False)
