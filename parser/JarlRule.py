#!/usr/bin/env python3

from common.aggregation_steps import *
from common.jarl_rule import *
from enum import Enum

class JarlRule():
    def __init__(self, text):
        self.text = text
        self.name = ""
        self.scope = None
        self.fact = None

    def __eq__(self, other):
        return isinstance(other, JarlRuleScope) and \
                self.name == other.name and \
                self.scope == other.scope and \
                self.fact == other.fact

    def __repr__(self):
        return "<name: {} scope: {} fact: {}>".format(self.name, self.scope, self.fact)

class JarlRuleScope():
    def __init__(self):
        self.filter = None
        self.selector = None

    def toSteps(self):
        checkpoints = self.selector.getCheckpoints()

        ## TODO: check validity of checkpoint arguments

        chk_names = {chk.name for chk in checkpoints}
        # 1)
        print("MatchCheckpoints({})".format([c for c in chk_names]))

        # 2) and 3)
        names = []
        args = []
        for chk in checkpoints:
            names.append(chk.name)
            args.append(chk.arguments)
        print("RenameArgs({}, {})".format(names, args))
        print("CrossAndGroupByArgs({}, {})".format(names, args))

        # 4)
        for cond in self.filter.conditions:
            print("ImposeIteratorCondition({}, {}, {})".format(cond.l, cond.c, cond.r))

        # 5)
        print(self.selector.toSteps())

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
        - A list of identifiers from the any clause
        - A list of identifiers from the every clause
        - A list of comparations from the with clause
    """
    def __init__(self):
        self.every = []
        self.any = []
        self.conditions = []

    def add(self, elem):
        # print("Attemting to add {} to a filter {}".format(elem, self.text))
        if elem.type == JarlFilterClauseType.ANY:
            self.any += elem.identifiers
        elif elem.type == JarlFilterClauseType.EVERY:
            self.every += elem.identifiers
        elif elem.type == JarlFilterClauseType.WITH:
            self.conditions += elem.conditions
        else:
            raise Exception("Jarl Filter Exception received an unknown sub-element type {}".format(elem.type.name))

    def __eq__(self, other):
        return isinstance(other, JarlFilterExpr) and \
                self.any == other.any and \
                self.every == other.every and \
                self.conditions == other.conditions

    def __repr__(self):
        return "<any: {} every: {} condition: {}>".format(self.any, self.every, self.conditions)

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
        return "<{}>".self.conditions

class JarlComparator(Enum):
    EQ = 0
    NE = 1
    LT = 2
    LE = 3
    GT = 4
    GE = 5

    def from_symbol(s):
        _from_symbol = {
            "=": JarlComparator.EQ,
            "!=": JarlComparator.NE,
            "<": JarlComparator.LT,
            "<=": JarlComparator.LE,
            ">": JarlComparator.GT,
            ">=": JarlComparator.GE,
        }
        return _from_symbol[s]


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
    AFTER = 0
    BEFORE = 1
    BETWEEN = 2

class JarlSelectorExpr():
    def __init__(self, type, start=None, end=None):
        self.start = start
        self.end = end
        self.type = type

    def getCheckpoints(self):
        checkpoints = []
        if self.start:
            checkpoints.append(self.start)
        if self.end:
            checkpoints.append(self.end)

        return checkpoints

    def toSteps(self):
        if self.type == JarlSelectorClauseType.AFTER:
            return "ScopeAfter({})".format(self.start.name)
        if self.type == JarlSelectorClauseType.BEFORE:
            return "ScopeBefore({})".format(self.end.name)
        if self.type == JarlSelectorClauseType.BETWEEN:
            return "ScopeBetween({}, {})".format(self.start.name, self.end.name)
        raise Exception("Invalid type of selector expression")

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
        if not facts:
            self.facts = []

    def __eq__(self, other):
        return isinstance(other, JarlRuleScope) and \
                self.filter == other.filter and \
                self.facts == other.facts

    def __repr__(self):
        return "<filter: {} facts: {}>".format(self.filter, self.facts)

class JarlRuleFactClause():
    def __init__(self, checkpoint, requirement):
        self.checkpoint = checkpoint
        self.requirement = requirement

    def __eq__(self, other):
        return isinstance(other, JarlRuleFactClause) and \
                self.checkpoint == other.checkpoint and \
                self.requirement == other.requirement

    def __repr__(self):
        return "<{} {}>".format(self.checkpoint, self.requirement)

class JarlRuleFactRequirementCount():
    def __init__(self, type="eq", count=1, negated=False):
        self.type = type
        self.count = count
        self.negated = negated

    def __eq__(self, other):
        return isinstance(other, JarlRuleFactRequirementCount) and \
                self.count == other.count and \
                self.negated == other.negated and \
                self.type == other.type

    def __repr__(self):
        return "<{} {} {}>".format("not" if self.negated else "", self.type, self.count)

class JarlRuleFactRequirementOrder():
    def __init__(self, checkpoint, type="after", negated=False):
        self.checkpoint = checkpoint
        self.type = type
        self.negated = negated

    def __eq__(self, other):
        return isinstance(other, JarlRuleFactRequirementOrder) and \
                self.checkpoint == other.checkpoint and \
                self.negated == other.negated and \
                self.type == other.type

    def __repr__(self):
        return "<{} {} {}>".format("not" if self.negated else "", self.type, self.checkpoint)

