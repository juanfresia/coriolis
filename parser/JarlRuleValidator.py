from .JarlParserExceptions import *

def validate_filter_arguments(filter):
    seen = set()
    args = filter.wildcards + filter.iterators
    for arg in args:
        if arg in seen:
            raise JarlArgumentAlreadyDeclared(arg)
        seen.add(arg)

def validate_scope_condition_arguments(filter):
    iterators = filter.iterators
    wildcards = filter.wildcards

    arguments = iterators + wildcards

    for cond in filter.conditions:
        if not cond.l in arguments:
            raise JarlArgumentNotDeclared(cond.l)

        # TODO: add checks in literal
        if cond.is_literal:
            continue
        if not cond.r in arguments:
            raise JarlArgumentNotDeclared(cond.r)

        if cond.l in iterators and not cond.r in iterators:
            raise JarlConditionMixesArguments(cond.l, cond.r)
        if cond.l in wildcards and not cond.r in wildcards:
            raise JarlConditionMixesArguments(cond.l, cond.r)

def validate_selector(selector):
    pass

def validate_rule(rule):
    if rule.scope:
        if rule.scope.filter:
            validate_filter_arguments(rule.scope.filter)
            validate_scope_condition_arguments(rule.scope.filter)
        validate_selector(rule.scope.selector)

