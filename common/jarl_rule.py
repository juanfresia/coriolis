#!/usr/bin/env python3

class JARLRule():
    def __init__(self, text, transformations, between_clause=None):
        self.text = text
        self.transformations = transformations
        self.between_clause = between_clause
        self.status = "Pending"

    def set_passed_status(self, has_passed):
        self.status = "Passed" if has_passed else "Failed"

    def has_passed(self):
        return self.status == "Passed"

    def has_failed(self):
        return self.status == "Failed"

    def has_between_clause(self):
        return self.between_clause is not None