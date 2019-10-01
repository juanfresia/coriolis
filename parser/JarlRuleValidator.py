from .JarlParserExceptions import *

def validate_filter_arguments(filter, scope_filter=None):
    """Validates filter arguments (iterators and wildcards) alone.
    Rules to apply:
    - Each argument must have an unique identifier. The same identifier
    cannot be used twice.

    If validating a filter expression of the rule fact, the filter expression
    of the rule scope is needed for the validation.
    """

    args = filter.wildcards + filter.iterators
    # Include filter arguments from scope, if any
    if scope_filter:
        args = args + scope_filter.wildcards + scope_filter.iterators

    seen = set()
    for arg in args:
        if arg in seen:
            raise JarlArgumentAlreadyDeclared(arg)
        seen.add(arg)

def validate_condition_arguments(filter, scope_filter=None):
    """Validates filter conditions alone.
    Rules to apply:
    - Elements in a filter condition need previous declaration (in
    filter arguments or previous scope filter arguments)
    - Condition arguments must be of the same type (e.g. iterator vs iterator).
    - Left side of the condition must have been declared in same filter clause.

    If validating a filter expression of the rule fact, the filter expression
    of the rule scope is needed for the validation.
    """

    iterators = filter.iterators
    wildcards = filter.wildcards
    arguments = iterators + wildcards

    # Previous scope filter arguments need to be separated
    scope_arguments = []
    if scope_filter:
        scope_arguments = scope_filter.iterators + scope_filter.wildcards

    for cond in filter.conditions:
        # Left side should always be declared in current filter
        if not cond.l in arguments:
            raise JarlArgumentNotDeclared(cond.l)

        # TODO: add checks in literal
        # A literal condition needs no further checking (for now)
        if cond.is_literal:
            continue

        # Right side CAN be declared in either the previous scope or the current filter
        if not cond.r in arguments and not cond.r in scope_arguments:
            raise JarlArgumentNotDeclared(cond.r)

        # If right side is not in the previous scope, arguments must be of the same type
        if cond.l in iterators and cond.r in wildcards:
            raise JarlConditionMixesArguments(cond.l, cond.r)
        if cond.l in wildcards and cond.r in iterators:
            raise JarlConditionMixesArguments(cond.l, cond.r)

def validate_selector(selector, filter=None):
    """Validates selector alone.
    Rules to apply:
    - Arguments in all checkpoints must have been previously declared.
    - Arguments may appear only once among the arguments of all scope checkpoints

    The scope filter, if any, is needed to completely validate a selector.
    """

    # Get known arguments for checkpoints
    filter_args = []
    if filter:
        filter_args = filter.arguments()

    # Make sure every argument is defined and used at most only once
    seen = set()
    for chk in selector.get_checkpoints():
        for arg in chk.arguments:
            if not arg in filter_args:
                raise JarlArgumentNotDeclared(arg)
            if arg in seen:
                raise JarlArgumentAlreadyUsed(arg)
            seen.add(arg)

def validate_fact(fact, fact_filter=None, scope_filter=None):
    """Validates selector alone.
    Rules to apply:
    - Arguments in all checkpoints must have been previously declared.
    - Arguments may appear only once among the arguments of all scope checkpoints

    The scope filter and the fact filter, if any, are needed to completely validate a fact.
    """

    # Get known arguments for checkpoints
    known_args = []
    if fact_filter:
        known_args += fact_filter.arguments()
    if scope_filter:
        known_args += scope_filter.arguments()

    # Make sure every argument is defined and used at most only once
    seen = set()
    for chk in fact.get_checkpoints():
        for arg in chk.arguments:
            if not arg in known_args:
                raise JarlArgumentNotDeclared(arg)
            if arg in seen:
                raise JarlArgumentAlreadyUsed(arg)
            seen.add(arg)
    pass



def validate_rule(rule):
    scope_filter = None

    # Validate scope, if any
    if rule.scope:
        if rule.scope.filter:
            scope_filter = rule.scope.filter
            validate_filter_arguments(scope_filter)
            validate_condition_arguments(scope_filter)
        validate_selector(rule.scope.selector, scope_filter)

    # Validate fact
    fact_filter = None
    if rule.fact.filter:
        fact_filter = rule.fact.filter
        validate_filter_arguments(fact_filter, scope_filter=scope_filter)
        validate_condition_arguments(fact_filter, scope_filter=scope_filter)

    for fact in rule.fact.facts:
        validate_fact(fact, fact_filter, scope_filter) 

