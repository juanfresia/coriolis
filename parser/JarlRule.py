#!/usr/bin/env python3

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

