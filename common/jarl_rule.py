#!/usr/bin/env python3
import copy
from common.aggregation_steps import *

class JARLRule:
    def __init__(self, statement_text, rule_header, fact, scope=None, passed_by_default=True):
        self.text = statement_text
        self.rule_header = rule_header
        self.fact = fact
        self.scope = scope
        self.status = "Pending"
        self.passed_by_default = passed_by_default
        self.failed_info = ""
        self.failed_scope = None
        self._dynamic_args = {}

    def set_dynamic_scope_arg(self, scope_arg, first_checkpoint=True):
        self._dynamic_args["#{}".format(scope_arg)] = (scope_arg, first_checkpoint)
        return self

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

    def __eq__(self, other):
        return isinstance(other, JARLRule) and \
            self.rule_header == other.rule_header and \
            self.fact == other.fact and \
            self.scope == other.scope and \
            self.status == other.status and \
            self.passed_by_default == other.passed_by_default and \
            self.failed_info == other.failed_info and \
            self.failed_scope == other.failed_scope and \
            self._dynamic_args == other._dynamic_args

    def __repr__(self):
        fact = str(self.fact).replace("\n", "\n\t")
        scope = str(self.scope).replace("\n", "\n\t")
        text = str(self.text).replace("\n", "\\n\"\n\t\"").replace("\"\\n\"", "")
        s = """JARLRule(
        (\"{}\"),
        \"{}\",
        {},
        {},
        passed_by_default={}
        )""".format(text, self.rule_header, fact, scope, self.passed_by_default)
        # We add the dynamic args
        for (k, v) in self._dynamic_args.items():
            s += "\\\n.set_dynamic_scope_arg(\"{}\", {})".format(v[0], v[1])
        return s


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

    def __eq__(self, other):
        return isinstance(other, RuleScope) and self.steps == other.steps

    def __repr__(self):
        return "RuleScope([\n\t{}\n])".format(", \n\t".join(map(str, self.steps)))

class RuleFact:
    def __init__(self, aggregation_steps):
        self.steps = aggregation_steps

    def evaluate_steps(self, dynamic_args={}):
        steps = copy.deepcopy(self.steps)
        steps = [s.evaluate(dynamic_args) for s in steps]
        return [s for subs in steps for s in subs]

    def __eq__(self, other):
        return isinstance(other, RuleFact) and self.steps == other.steps

    def __repr__(self):
        return "RuleFact([\n\t{}\n])".format(", \n\t".join(map(str, self.steps)))