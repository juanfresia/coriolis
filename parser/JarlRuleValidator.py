from .JarlParserExceptions import *

def validate_filter_arguments(filter):
    seen = set()
    args = filter.wildcards + filter.iterators
    for arg in args:
        if arg in seen:
            raise JarlIteratorAlreadyDefined()
        seen.add(arg)

def validate_condition_arguments(filter):
    iterators = filter.iterators

    for cond in filter.conditions:
        if not cond.l in iterators:
            raise JarlIteratorUndefined
        if not cond.is_literal and not cond.r in iterators:
            raise JarlIteratorUndefined

def validate_selector(selector):
    pass

def validate_rule(rule):
    if rule.scope:
        if rule.scope.filter:
            validate_filter_arguments(rule.scope.filter)
            validate_condition_arguments(rule.scope.filter)
        validate_selector(rule.scope.selector)

