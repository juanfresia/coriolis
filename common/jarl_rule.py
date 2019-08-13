#!/usr/bin/env python3

class JARLRule():
    def __init__(self, text, transformations, scope=None):
        self.text = text
        self.transformations = self._flatten_transformations(transformations)
        self.scope = self._flatten_transformations(scope)
        self.status = "Pending"

    def _flatten_transformations(self, transformations):
        if transformations is not None:
            transformations = [t for subt in transformations for t in subt]
        return transformations

    def set_passed_status(self, has_passed):
        self.status = "Passed" if has_passed else "Failed"

    def has_passed(self):
        return self.status == "Passed"

    def has_failed(self):
        return self.status == "Failed"

    def has_scope(self):
        return self.scope is not None