#!/usr/bin/env python3

from common.aggregation_steps import *
from common.jarl_rule import *

class JarlRule():
    def __init__(self, text):
        self.text = text
        self.name = ""
        self.scope = None
        self.fact = None

    def __repr__(self):
        return "( name: {} scope: {} fact: {} )".format(self.name, self.scope, self.fact)

class JarlRuleScope():
    def __init__(self, text):
        self.text = text
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


    def __repr__(self):
        return "( filter: {} selector: {} )".format(self.filter, self.selector)

class JarlFilterExpr():
    """
    Represents a Filter expression in the JARL rule language.
    It is composed for three things:
        - A list of identifiers from the any clause
        - A list of identifiers from the every clause
        - A list of comparations from the with clause
    """
    def __init__(self, text):
        self.text = text
        self.every = []
        self.any = []
        self.conditions = []

    def add(self, elem):
        # print("Attemting to add {} to a filter {}".format(elem, self.text))
        if elem.type == "any":
            self.any += elem.identifiers
        elif elem.type == "every":
            self.every += elem.identifiers
        elif elem.type == "with":
            self.conditions += elem.conditions
        else:
            raise Exception("Jarl Filter Exception received an unknown sub-element type {}".format(elem.type))

    def __repr__(self):
        return "( any: {} every: {} condition: {} )".format(self.any, self.every, self.conditions)

class JarlQuantifierClause():
    def __init__(self, type, identifiers):
        self.type = type
        self.identifiers = identifiers

    def __repr__(self):
        return "{} {}".format(self.type, self.identifiers)

class JarlWithClause():
    def __init__(self, text, conditions):
        self.text = text
        self.type = "with"
        self.conditions = conditions

    def __repr__(self):
        return "{}".self.conditions

class JarlWithCondition():
    def __init__(self, l, c, r, is_literal=False):
        self.l = l
        self.c = c
        self.r = r
        self.is_literal = is_literal

    def __repr__(self):
        return "{} {} {}".format(self.l, self.c, self.r)

class JarlSelectorExpr():
    def __init__(self, type, start, end):
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
        if self.type == "after":
            return "ScopeAfter({})".format(self.start.name)
        if self.type == "before":
            return "ScopeBefore({})".format(self.end.name)
        if self.type == "between":
            return "ScopeBetween({}, {})".format(self.start.name, self.end.name)
        raise Exception("Invalid type of selector expression")

    def __repr__(self):
        return "{} {} {}".format(self.type, self.start, self.end)

class JarlCheckpoint():
    def __init__(self, name, arguments=None):
        self.name = name
        if arguments is None:
            arguments = []
        self.arguments = arguments

    def __repr__(self):
        return "{}({})".format(self.name, self.arguments)
