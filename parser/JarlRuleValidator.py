from .JarlParserExceptions import *

class JarlRuleValidator():
    def validate_filter_arguments(self, filter, scope_filter=None):
        """Validates filter arguments (iterators and wildcards) alone.
        Rules to apply:
        - Each argument must have an unique identifier. The same identifier
        cannot be used twice.

        If validating a filter expression of the rule fact, the filter expression
        of the rule scope is needed for the validation.
        """

        args = filter.wildcards + filter.iterators
        # Include filter arguments from scope, if any
        if scope_filter: args = args + scope_filter.wildcards + scope_filter.iterators

        seen = set()
        for arg in args:
            if arg in seen:
                raise JarlArgumentAlreadyDeclared(arg)
            seen.add(arg)

    def validate_condition_arguments(self, filter, scope_filter=None):
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
        scope_arguments = scope_filter.iterators + scope_filter.wildcards if scope_filter else []

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

    def validate_selector(self, selector, filter=None):
        """Validates selector alone.
        Rules to apply:
        - Arguments in all checkpoints must have been previously declared.
        - Arguments may appear only once among the arguments of all scope checkpoints

        The scope filter, if any, is needed to completely validate a selector.
        """

        # Get known arguments for checkpoints
        filter_args = filter.arguments() if filter else []

        # Make sure every argument is defined and used at most only once
        seen = set()
        for chk in selector.get_checkpoints():
            for arg in chk.arguments:
                if not arg in filter_args:
                    raise JarlArgumentNotDeclared(arg)
                if arg in seen:
                    raise JarlArgumentAlreadyUsed(arg)
                seen.add(arg)

    def validate_fact(self, fact, fact_filter=None, scope_selector=None):
        """Validates selector alone.
        Rules to apply:
        - Arguments in all checkpoints must have been previously declared in fact filter.
        - Arguments may appear only once among the arguments of all fact _and_ scope checkpoints

        The fact filter and scope selector, if any, are needed to completely validate a fact.
        """

        # Get known arguments for checkpoints
        known_args = fact_filter.arguments() if fact_filter else []
        scope_selector_chk = scope_selector.get_checkpoints() if scope_selector else []

        # Get arguments used in scope selector
        used_args = []
        for chk in scope_selector_chk:
            used_args += chk.arguments

        # Make sure every argument is defined and used at most only once
        seen = set()
        for chk in fact.get_checkpoints():
            for arg in chk.arguments:
                if arg in used_args:
                    raise JarlArgumentAlreadyUsed(arg)
                if not arg in known_args:
                    raise JarlArgumentNotDeclared(arg)
                if arg in seen:
                    raise JarlArgumentAlreadyUsed(arg)
                seen.add(arg)

    def validate_rule(self, rule):
        scope_filter = None
        scope_selector = None

        # Validate scope, if any
        if rule.scope:
            scope_selector = rule.scope.selector
            if rule.scope.filter:
                scope_filter = rule.scope.filter
                self.validate_filter_arguments(scope_filter)
                self.validate_condition_arguments(scope_filter)
            self.validate_selector(scope_selector, scope_filter)

        # Validate fact
        fact_filter = None
        if rule.fact.filter:
            fact_filter = rule.fact.filter
            self.validate_filter_arguments(fact_filter, scope_filter=scope_filter)
            self.validate_condition_arguments(fact_filter, scope_filter=scope_filter)

        for fact in rule.fact.facts:
            self.validate_fact(fact, fact_filter, scope_selector)
