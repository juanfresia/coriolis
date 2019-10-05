from common.aggregation_steps import *
from common.jarl_rule import *
from parser.JarlRule import *

class JarlRuleAdapter():
    def __init__(self):
        self.dynamic_args = []

    def unique_checkpoints(self, checkpoints):
        unique = []
        for chk in checkpoints:
            if not chk in unique:
                unique.append(chk)
        return unique

    def concat_checkpoint(self, chk):
        concat = [chk.name]
        concat += [arg for arg in chk.arguments]
        return concat

    def concat_checkpoint_only_iters(self, chk, iterators=[]):
        concat = [chk.name]
        concat += [arg for arg in chk.arguments if arg in iterators]
        return concat

    def any_checkpoint_has_args(self, checkpoints):
        for chk in checkpoints:
            if chk.arguments:
                return True
        return False

    def adapt_scope_filter_condition(self, condition, scope_filter):
        # 1) Define condition type:
        # - if condition.left is wildcard -> ImposeWildcardCondition
        # - if condition.right is iterator -> ImposeIteratorCondition
        #
        # 2) If condition is literal:
        # - last parameter is True

        left = condition.l
        operator = condition.c.value
        right = condition.r
        literal = condition.is_literal

        if left in scope_filter.wildcards:
            return ImposeWildcardCondition(left, operator, right, literal)
        elif left in scope_filter.iterators:
            return ImposeIteratorCondition(left, operator, right, literal)
        else:
            raise Exception("Comparison argument was not declared!")

    def adapt_fact_filter_condition(self, condition, fact_filter, scope_filter=None):
        # 1) Define condition type:
        # - if condition.left is wildcard -> ImposeWildcardCondition
        # - if condition.right is iterator -> ImposeIteratorCondition
        #
        # 2) If right de is from scope_filter:
        # - prepend a # to the argument name
        # - last parameter is True
        #
        # 3) If condition is literal:
        # - last parameter is True

        scope_args = []
        if scope_filter:
            scope_args = scope_filter.arguments()

        left = condition.l
        operator = condition.c.value
        right = condition.r
        literal = condition.is_literal

        # From 2)
        if right in scope_args:
            # We store these parameters to later call set_dynamic_scope_args
            self.dynamic_args.append(right)
            right = "#" + right
            literal = True

        if left in fact_filter.wildcards:
            return ImposeWildcardCondition(left, operator, right, literal)
        elif left in fact_filter.iterators:
            return ImposeIteratorCondition(left, operator, right, literal)
        else:
            raise Exception("Comparison argument was not declared!")

    def get_rule_text(self, rule):
        return rule.text

    def get_rule_header(self, rule):
        return rule.name

    def get_rule_scope(self, rule):
        scope = rule.scope
        if not scope:
            return None

        checkpoints = scope.selector.get_checkpoints()
        iterators = []
        if scope.filter:
            iterators = scope.filter.iterators

        scope_steps = []

        match_checkpoints = MatchCheckpoints([chk.name for chk in self.unique_checkpoints(checkpoints)])
        scope_steps.append(match_checkpoints)

        if self.any_checkpoint_has_args(checkpoints):
            flattened_checkpoints = [self.concat_checkpoint(chk) for chk in checkpoints]
            rename_args = RenameArgs(flattened_checkpoints)
            scope_steps.append(rename_args)

        flattened_checkpoints = [self.concat_checkpoint_only_iters(chk, iterators) for chk in checkpoints]
        cross_and_group = CrossAndGroupByArgs(flattened_checkpoints)
        scope_steps.append(cross_and_group)

        # Conditions
        conditions = []
        if scope.filter:
            conditions = scope.filter.conditions

        for cond in conditions:
            scope_steps.append(self.adapt_scope_filter_condition(cond, scope.filter))

        if scope.selector.type == JarlSelectorClauseType.BETWEEN_NEXT:
            scope_selector = ScopeBetween(scope.selector.start.name, scope.selector.end.name)
        elif scope.selector.type == JarlSelectorClauseType.BETWEEN_PREV:
            scope_selector = ScopeBetween(scope.selector.start.name, scope.selector.end.name, False)
        elif scope.selector.type == JarlSelectorClauseType.AFTER:
            scope_selector = ScopeBetween(scope.selector.start.name)
        elif scope.selector.type == JarlSelectorClauseType.BEFORE:
            scope_selector = ScopeBetween(scope.selector.end.name)
        else:
            raise Exception("Unexpected Selector Clause type")

        scope_steps.append(scope_selector)
        return RuleScope(scope_steps)

    def get_rule_fact(self, rule):
        fact = rule.fact
        checkpoints = fact.facts[0].get_checkpoints()
        iterators = []
        if fact.filter:
            iterators = fact.filter.iterators

        scope_filter = rule.scope.filter if rule.scope else None

        fact_steps = []

        match_checkpoints = MatchCheckpoints([chk.name for chk in checkpoints])
        fact_steps.append(match_checkpoints)

        if self.any_checkpoint_has_args(checkpoints):
            flattened_checkpoints = [self.concat_checkpoint(chk) for chk in checkpoints]
            rename_args = RenameArgs(flattened_checkpoints)
            fact_steps.append(rename_args)

        flattened_checkpoints = [self.concat_checkpoint_only_iters(chk, iterators) for chk in checkpoints]
        cross_and_group = CrossAndGroupByArgs(flattened_checkpoints)
        fact_steps.append(cross_and_group)

        # Conditions
        conditions = []
        if fact.filter:
            conditions = fact.filter.conditions

        for cond in conditions:
            fact_steps.append(self.adapt_fact_filter_condition(cond, fact.filter, scope_filter))

        requirement = fact.facts[0].requirement
        if requirement.get_checkpoints():
            # It is a precedence requirement
            compare_results = CompareResultsPrecedence(fact.facts[0].checkpoint.name, requirement.checkpoint.name)
        else:
            # It is an order requirement
            compare_results = CompareResultsQuantity(requirement.type.value, requirement.count)
        fact_steps.append(compare_results)

        fact_steps.append(ReduceResult())

        return RuleFact(fact_steps)

    def set_rule_dynamic_scope_args(self, rule, adapted_rule):
        is_in_first_chk = True
        for dynamic_arg in self.dynamic_args:
            selector = rule.scope.selector
            if selector.start and selector.end:
                if dynamic_arg in selector.end.arguments:
                    is_in_first_chk = False

            print(dynamic_arg, is_in_first_chk)
            adapted_rule.set_dynamic_scope_arg(dynamic_arg, is_in_first_chk)

    def rule_to_steps(self, rule):
        # TODO(jfresia) add validation of the rule here

        # Get each part of a rule
        rule_text = self.get_rule_text(rule)
        rule_header = self.get_rule_header(rule)
        rule_scope = self.get_rule_scope(rule)
        rule_fact = self.get_rule_fact(rule)

        # TODO(jfresia) Somehow infer the passed_by_default part of the rule

        # Compose rule and return
        adapted_rule = JARLRule(rule_text, rule_header, rule_fact, rule_scope, passed_by_default=False)
        self.set_rule_dynamic_scope_args(rule, adapted_rule)
        return adapted_rule
