from common.aggregation_steps import *
from common.jarl_rule import *
from parser.jarl_rule import *
from parser.jarl_rule_validator import *

class JarlRuleAdapter():
    def __init__(self):
        self.dynamic_args = []

    def unique_checkpoints(self, checkpoints):
        unique = []
        [unique.append(chk.name) for chk in checkpoints if chk.name not in unique]
        return unique

    def _concat_checkpoint(self, chk):
        return [chk.name] + [arg for arg in chk.arguments]

    def _concat_checkpoint_only_iters(self, chk, iterators=[]):
        return [chk.name] + [arg for arg in chk.arguments if arg in iterators]

    def any_checkpoint_has_args(self, checkpoints):
        return any(chk.arguments for chk in checkpoints)

    def _adapt_filter_condition(self, condition, this_filter, other_filter=None):
        # 1) Define condition type:
        # - if condition.left is wildcard -> ImposeWildcardCondition
        # - if condition.right is iterator -> ImposeIteratorCondition
        #
        # 2) If right argument is from other_filter:
        # - prepend a # to the argument name
        # - last parameter is True
        #
        # 3) If condition is literal:
        # - last parameter is True

        scope_args = other_filter.arguments() if other_filter else []
        right = condition.r
        is_literal = condition.is_literal

        # From 2)
        if right in scope_args:
            # We store these parameters to later call set_dynamic_scope_args
            self.dynamic_args.append(right)
            right = "#" + right
            is_literal = True

        if condition.l in this_filter.wildcards:
            return ImposeWildcardCondition(condition.l, condition.c.value, right, is_literal)
        if condition.l in this_filter.iterators:
            return ImposeIteratorCondition(condition.l, condition.c.value, right, is_literal)

        raise Exception("Comparison argument was not declared!")

    def _adapt_scope_filter_condition(self, condition, scope_filter):
        return self._adapt_filter_condition(condition, scope_filter)

    def _adapt_fact_filter_condition(self, condition, fact_filter, scope_filter=None):
        return self._adapt_filter_condition(condition, fact_filter, scope_filter)

    def adapt_rule_text(self, rule):
        return rule.text

    def adapt_rule_header(self, rule):
        return rule.name

    def _adapt_scope_type(self, scope_type, start_name, end_name):
        to_steps = {
            JarlSelectorClauseType.BETWEEN_NEXT: ScopeBetween(start_name, end_name),
            JarlSelectorClauseType.BETWEEN_PREV: ScopeBetween(start_name, end_name, False),
            JarlSelectorClauseType.AFTER: ScopeAfter(start_name),
            JarlSelectorClauseType.BEFORE: ScopeBefore(end_name)
        }
        if scope_type not in to_steps: raise Exception("Unexpected Selector Clause type")
        return to_steps[scope_type]

    def _adapt_checkpoints_names(self, checkpoints):
        return MatchCheckpoints([chk for chk in self.unique_checkpoints(checkpoints)])

    def _adapt_argument_names(self, checkpoints):
        flattened_checkpoints = [self._concat_checkpoint(chk) for chk in checkpoints if chk.arguments]
        return RenameArgs(flattened_checkpoints) if flattened_checkpoints else None

    def _adapt_checkpoints_cross_and_group(self, checkpoints, iterators):
        flattened_checkpoints = [self._concat_checkpoint_only_iters(chk, iterators) for chk in checkpoints]
        return CrossAndGroupByArgs(flattened_checkpoints)

    def _adapt_fact_requirement(self, requirement, other_checkpoint_name=None):
        if requirement.get_checkpoints(): # Order requirement
            return CompareResultsPrecedence(other_checkpoint_name, requirement.checkpoint.name)
        else: # Quantity requirement
            return CompareResultsQuantity(requirement.type.value, requirement.count)

    def adapt_rule_scope(self, rule):
        if not rule.scope: return None

        scope = rule.scope
        checkpoints = scope.selector.get_checkpoints()
        iterators = scope.filter.iterators if scope.filter else []

        scope_steps = [self._adapt_checkpoints_names(checkpoints)]

        adapter_arg_names = self._adapt_argument_names(checkpoints)
        if adapter_arg_names: scope_steps.append(adapter_arg_names)

        scope_steps.append(self._adapt_checkpoints_cross_and_group(checkpoints, iterators))

        conditions = scope.filter.conditions if scope.filter else []
        for cond in conditions:
            scope_steps.append(self._adapt_scope_filter_condition(cond, scope.filter))

        end_name = scope.selector.end.name if scope.selector.end else None
        start_name = scope.selector.start.name if scope.selector.start else None
        scope_steps.append(self._adapt_scope_type(scope.selector.type, start_name, end_name))
        return RuleScope(scope_steps)

    def adapt_rule_fact(self, rule):
        fact = rule.fact
        checkpoints = fact.facts[0].get_checkpoints()
        iterators = fact.filter.iterators if fact.filter else []
        scope_filter = rule.scope.filter if rule.scope else None

        fact_steps = [self._adapt_checkpoints_names(checkpoints)]

        adapter_arg_names = self._adapt_argument_names(checkpoints)
        if adapter_arg_names: fact_steps.append(adapter_arg_names)

        fact_steps.append(self._adapt_checkpoints_cross_and_group(checkpoints, iterators))

        conditions = fact.filter.conditions if fact.filter else []
        for cond in conditions:
            fact_steps.append(self._adapt_fact_filter_condition(cond, fact.filter, scope_filter))

        fact_steps.append(self._adapt_fact_requirement(fact.facts[0].requirement, fact.facts[0].checkpoint.name))
        fact_steps.append(ReduceResult())

        return RuleFact(fact_steps)

    def get_passed_by_default(self, rule):
        req = rule.fact.facts[0].requirement
        # If requirement is of order, passed_by_default is always true
        if req.get_checkpoints(): return True

        false_cases = [
            req.type == JarlComparator.EQ and req.count != 0,
            req.type == JarlComparator.GE and req.count != 0
        ]
        return True not in false_cases

    def set_rule_dynamic_scope_args(self, rule, adapted_rule):
        for dynamic_arg in self.dynamic_args:
            is_in_first_chk = True
            selector = rule.scope.selector
            if selector.type == JarlSelectorClauseType.BEFORE:
                is_in_first_chk = False

            if selector.type == JarlSelectorClauseType.BETWEEN_NEXT:
                if dynamic_arg in selector.end.arguments:
                    is_in_first_chk = False

            if selector.type == JarlSelectorClauseType.BETWEEN_PREV:
                if dynamic_arg in selector.start.arguments:
                    is_in_first_chk = False

            adapted_rule.set_dynamic_scope_arg(dynamic_arg, is_in_first_chk)

    def rule_to_steps(self, rule):
        JarlRuleValidator().validate_rule(rule)

        # Get each part of a rule
        rule_text = self.adapt_rule_text(rule)
        rule_header = self.adapt_rule_header(rule)
        rule_scope = self.adapt_rule_scope(rule)
        rule_fact = self.adapt_rule_fact(rule)
        passed_by_default = self.get_passed_by_default(rule)

        # Compose rule, set dynamic args and return adapted_rule
        adapted_rule = JARLRule(rule_text, rule_header, rule_fact, rule_scope, passed_by_default=passed_by_default)
        self.set_rule_dynamic_scope_args(rule, adapted_rule)

        return adapted_rule
