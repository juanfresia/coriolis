#!/usr/bin/env python3

from enum import Enum

class JarlRule():
    def __init__(self, name="", scope=None, fact=None, text=""):
        self.text = text
        self.name = name
        self.scope = scope
        self.fact = fact

    def __eq__(self, other):
        return isinstance(other, JarlRule) and \
                self.name == other.name and \
                self.scope == other.scope and \
                self.fact == other.fact

    def __repr__(self):
        return "<name: {} scope: {} fact: {}>".format(self.name, self.scope, self.fact)

class JarlRuleScope():
    def __init__(self, filter=None, selector=None):
        self.filter = filter
        self.selector = selector

    def toSteps(self):
        pass

    def __eq__(self, other):
        return isinstance(other, JarlRuleScope) and \
                self.filter == other.filter and \
                self.selector == other.selector

    def __repr__(self):
        return "<filter: {} selector: {}>".format(self.filter, self.selector)

class JarlFilterClauseType(Enum):
    ANY = 0
    EVERY = 1
    WITH = 2

class JarlFilterExpr():
    """
    Represents a Filter expression in the JARL rule language.
    It is composed for three things:
        - A list of identifiers from the wildcards clause (any)
        - A list of identifiers from the iterators clause
        - A list of comparations from the with clause
    """
    def __init__(self, iterators=None, wildcards=None, conditions=None):
        self.iterators = iterators if iterators else []
        self.wildcards = wildcards if wildcards else []
        self.conditions = conditions if conditions else []

    def add(self, elem):
        # Since elements are traversed in a DFS fashion, we prepend
        # them to the respective list to preserve the original order.
        if elem.type == JarlFilterClauseType.ANY:
            self.wildcards = elem.identifiers + self.wildcards
        elif elem.type == JarlFilterClauseType.EVERY:
            self.iterators = elem.identifiers + self.iterators
        elif elem.type == JarlFilterClauseType.WITH:
            self.conditions = elem.conditions + self.conditions
        else:
            raise Exception("Jarl Filter Exception received an unknown sub-element type {}".format(elem.type.name))

    def arguments(self):
        return self.wildcards + self.iterators

    def __eq__(self, other):
        return isinstance(other, JarlFilterExpr) and \
                self.wildcards == other.wildcards and \
                self.iterators == other.iterators and \
                self.conditions == other.conditions

    def __repr__(self):
        return "<wildcards: {} iterators: {} condition: {}>".format(self.wildcards, self.iterators, self.conditions)

class JarlQuantifierClause():
    def __init__(self, type, identifiers):
        self.type = type
        self.identifiers = identifiers

    def __eq__(self, other):
        return isinstance(other, JarlQuantifierClause) and \
                self.type == other.type and \
                self.identifiers == other.identifiers

    def __repr__(self):
        return "<{} {}>".format(self.type, self.identifiers)

class JarlWithClause():
    def __init__(self, conditions):
        self.type = JarlFilterClauseType.WITH
        self.conditions = conditions

    def __eq__(self, other):
        return isinstance(other, JarlWithClause) and \
                self.type == other.type and \
                self.conditions == other.conditions

    def __repr__(self):
        return "<{}>".format(self.conditions)

class JarlComparator(Enum):
    EQ = "="
    NE = "!="
    LT = "<"
    LE = "<="
    GT = ">"
    GE = ">="

class JarlWithCondition():
    def __init__(self, l, c, r, is_literal=False):
        self.l = l
        self.c = c
        self.r = r
        self.is_literal = is_literal

    def __eq__(self, other):
        return isinstance(other, JarlWithCondition) and \
                self.l == other.l and \
                self.c == other.c and \
                self.r == other.r and \
                self.is_literal == other.is_literal

    def __repr__(self):
        return "<{} {} {}>".format(self.l, self.c, self.r)

class JarlSelectorClauseType(Enum):
    AFTER = "after"
    BEFORE = "before"
    BETWEEN_NEXT = "between_next"
    BETWEEN_PREV = "between_prev"

class JarlSelectorExpr():
    def __init__(self, type, start=None, end=None):
        self.start = start
        self.end = end
        self.type = type

    def get_checkpoints(self):
        checkpoints = []
        if self.start:
            checkpoints.append(self.start)
        if self.end:
            checkpoints.append(self.end)

        return checkpoints

    def toSteps(self):
        end_name = ", {}".format(self.end.name) if self.type == JarlSelectorClauseType.BETWEEN_NEXT or self.type == JarlSelectorClauseType.BETWEEN_PREV else ""
        return "Scope{}({}{})".format(self.type, self.start.name, end_name)

    def __eq__(self, other):
        return isinstance(other, JarlSelectorExpr) and \
                self.type == other.type and \
                self.start == other.start and \
                self.end == other.end

    def __repr__(self):
        return "<{} {} {}>".format(self.type, self.start, self.end)

class JarlCheckpoint():
    def __init__(self, name, arguments=None):
        self.name = name
        if arguments is None:
            arguments = []
        self.arguments = arguments

    def __eq__(self, other):
        return isinstance(other, JarlCheckpoint) and \
                self.name == other.name and \
                self.arguments == other.arguments

    def __repr__(self):
        return "<{} {}>".format(self.name, self.arguments)

class JarlRuleFact():
    def __init__(self, filter=None, facts=None):
        self.filter = filter
        self.facts = []
        if facts:
            self.facts = facts

    def __eq__(self, other):
        return isinstance(other, JarlRuleFact) and \
                self.filter == other.filter and \
                self.facts == other.facts

    def __repr__(self):
        return "<filter: {} facts: {}>".format(self.filter, self.facts)

class JarlRuleFactClause():
    def __init__(self, checkpoint, requirement):
        self.checkpoint = checkpoint
        self.requirement = requirement

    def get_checkpoints(self):
        checkpoints = [self.checkpoint]
        checkpoints += self.requirement.get_checkpoints()
        return checkpoints


    def __eq__(self, other):
        return isinstance(other, JarlRuleFactClause) and \
                self.checkpoint == other.checkpoint and \
                self.requirement == other.requirement

    def __repr__(self):
        return "<{} {}>".format(self.checkpoint, self.requirement)

class JarlRuleFactRequirementCount():
    def __init__(self, type=JarlComparator.EQ, count=1, negated=False):
        self.type = type
        self.count = count
        self.negated = negated

    def get_checkpoints(self):
        return []

    def __eq__(self, other):
        return isinstance(other, JarlRuleFactRequirementCount) and \
                self.count == other.count and \
                self.negated == other.negated and \
                self.type == other.type

    def __repr__(self):
        return "<{} {} {}>".format("not" if self.negated else "", self.type, self.count)

class JarlRuleFactRequirementOrder():
    def __init__(self, checkpoint, negated=False):
        self.checkpoint = checkpoint
        self.negated = negated

    def get_checkpoints(self):
        return [self.checkpoint]

    def __eq__(self, other):
        return isinstance(other, JarlRuleFactRequirementOrder) and \
                self.checkpoint == other.checkpoint and \
                self.negated == other.negated

    def __repr__(self):
        return "<{} precedes {}>".format("not" if self.negated else "", self.checkpoint)

