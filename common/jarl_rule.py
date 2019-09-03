#!/usr/bin/env python3
import copy
from common.aggregation_steps import *

class JARLRule:
    def __init__(self, statement_text, fact, scope=None, passed_by_default=True):
        self.text = statement_text
        self.fact = fact
        self.scope = scope
        self.status = "Pending"
        self.passed_by_default = passed_by_default
        self.failed_info = ""
        self.failed_scope = None
        self._dynamic_args = {}

    def set_dynamic_scope_arg(self, scope_arg, first_checkpoint=True):
        self._dynamic_args["#{}".format(scope_arg)] = (scope_arg, first_checkpoint)

    def evaluate_scope_steps(self):
        return self.scope.evaluate_steps()

    def evaluate_fact_steps(self, s):
        l_first, l_second = RuleScope.parse_scope_log_lines(s)

        dynamic_args = {}
        for (k, v) in self._dynamic_args.items():
            dynamic_args[k] = RuleScope.parse_scope_arg(s, v[0], v[1])
        return FilterByLogLines(l_first, l_second).evaluate() + self.fact.evaluate_steps(dynamic_args)

    def set_passed(self):
        self.status = "Passed"

    def set_failed(self, failed_scope=None, failed_info=""):
        self.status = "Failed"
        self.failed_scope = failed_scope
        self.failed_info = failed_info

    def set_default(self, scope=None, info=""):
        self.set_passed() if self.passed_by_default else self.set_failed(scope, info)

    def get_failed_info(self):
        return self.failed_info

    def get_failed_scope(self):
        return RuleScope.parse_scope_log_lines(self.failed_scope)

    def has_passed(self):
        return self.status == "Passed"

    def has_failed(self):
        return self.status == "Failed"

    def has_scope(self):
        return self.scope is not None

class RuleScope:
    def __init__(self, aggregation_steps):
        self.steps = aggregation_steps

    def evaluate_steps(self):
        steps = [s.evaluate() for s in self.steps]
        return [s for subs in steps for s in subs]

    @staticmethod
    def parse_scope_log_lines(sub_scope):
        return sub_scope["c1"]["log_line"], sub_scope["c2"]["log_line"]

    @staticmethod
    def parse_scope_arg(sub_scope, arg_name, first=True):
        return sub_scope["c1" if first else "c2"]["arg_{}".format(arg_name)]

    @staticmethod
    def get_default_scope():
        return [ {"c1": {"log_line": "MIN"}, "c2": {"log_line": "MAX"}} ]

class RuleFact:
    def __init__(self, aggregation_steps):
        self.steps = aggregation_steps

    def evaluate_steps(self, dynamic_args={}):
        steps = copy.deepcopy(self.steps)
        steps = [s.evaluate(dynamic_args) for s in steps]
        return [s for subs in steps for s in subs]