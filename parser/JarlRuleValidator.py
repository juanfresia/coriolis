from .JarlParserExceptions import *

def validate_filter_arguments(filter):
    seen = set()
    args = filter.every + filter.any
    for arg in args:
        if arg in seen:
            raise JarlIteratorAlreadyDefined()
        seen.add(arg)

def validate_rule(rule):
    if rule.scope:
        if rule.scope.filter:
            validate_filter_arguments(rule.scope.filter)

