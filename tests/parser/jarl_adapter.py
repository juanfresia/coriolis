import unittest

from parser.JarlParserCLI import parse_str, parse_file
from parser.JarlRule import *
from parser.JarlParserExceptions import *
from parser.JarlRuleAdapter import *
from common.aggregation_steps import *
from common.jarl_rule import *

class TestAdapter(unittest.TestCase):
    def test_adapter_with_basic_fact(self):
        rule = """
        rule readers_read_two_times
        for every r and any room, msg
        read_room(r, room, msg) must happen 2 times
        """
        rules = parse_str(rule)

        steps = JarlRuleAdapter().rule_to_steps(rules[0])

        rule_header = "readers_read_two_times"
        rule_fact = RuleFact([
            MatchCheckpoints(["read_room"]),
            RenameArgs([["read_room", "r", "room", "msg"]]),
            CrossAndGroupByArgs([["read_room", "r"]]),
            CompareResultsQuantity("=", 2),
            ReduceResult()
        ])
        expected_rule_adapted = JARLRule(rule, rule_header, rule_fact, passed_by_default=False)

        self.assertEqual(expected_rule_adapted, steps)

    def test_adapter_with_basic_scope(self):

        rule = """
        rule two_hydrogen_per_molecule
        between water_made() and next water_made()
        for every atom_type and any atom_id with atom_type='H'
        bond(atom_type, atom_id) must happen 2 times
        """

        rules = parse_str(rule)
        steps = JarlRuleAdapter().rule_to_steps(rules[0])

        rule_header = "two_hydrogen_per_molecule"
        rule_scope = RuleScope([
            MatchCheckpoints(["water_made"]),
            CrossAndGroupByArgs([["water_made"], ["water_made"]]),
            ScopeBetween("water_made", "water_made")
        ])
        rule_fact = RuleFact([
            MatchCheckpoints(["bond"]),
            RenameArgs([["bond", "atom_type", "atom_id"]]),
            CrossAndGroupByArgs([["bond", "atom_type"]]),
            ImposeIteratorCondition("atom_type", "=", "H", True),
            CompareResultsQuantity("=", 2),
            ReduceResult()
        ])
        expected_rule_adapted = JARLRule(rule, rule_header, rule_fact, rule_scope, passed_by_default=False)

        self.assertEqual(expected_rule_adapted, steps)

    def test_adapter_with_reference_to_scope(self):
        rule = """
        rule reader_reads_what_was_last_written
        for every r1, m1, r2, m2 and any r, w with m1!='NULL', r1=r2, m1=m2
        between read_room(r, r1, m1) and previous write_room(w, r2, m2)
        for any wid, roomid, m with roomid=r2, m!=m2
        write_room(wid, roomid, m) must happen 0 times
        """
        rules = parse_str(rule)

        steps = JarlRuleAdapter().rule_to_steps(rules[0])

        rule_header = "reader_reads_what_was_last_written"
        rule_scope = RuleScope([
            MatchCheckpoints(["read_room", "write_room"]),
            RenameArgs([["read_room", "r", "r1", "m1"], ["write_room", "w", "r2", "m2"]]),
            CrossAndGroupByArgs([["read_room", "r1", "m1"], ["write_room", "r2", "m2"]]),
            ImposeIteratorCondition("m1", "!=", "NULL", True),
            ImposeIteratorCondition("r1", "=", "r2"),
            ImposeIteratorCondition("m1", "=", "m2"),
            ScopeBetween("read_room", "write_room", False)
        ])
        rule_fact = RuleFact([
            MatchCheckpoints(["write_room"]),
            RenameArgs([["write_room", "wid", "roomid", "m"]]),
            CrossAndGroupByArgs([["write_room"]]),
            ImposeWildcardCondition("roomid", "=", "#r2", True),
            ImposeWildcardCondition("m", "!=", "#m2", True),
            CompareResultsQuantity("=", 0),
            ReduceResult()
        ])
        expected_rule_adapted = JARLRule(rule, rule_header, rule_fact, rule_scope, passed_by_default=True)
        expected_rule_adapted.set_dynamic_scope_arg("r2", True)
        expected_rule_adapted.set_dynamic_scope_arg("m2", True)

        self.assertEqual(expected_rule_adapted, steps)

    def test_adapter_with_both_dynamic_args(self):

        rule = """
        rule seal_needed_to_seal_passport
        for every e1, e2, person_name, t, passport with e1=e2, t='tourist'
        between employee_serve(e1, person_name, t) and next employee_allow_tourist(e2, passport)
        for every eid1, eid2, p with eid1=e1, eid2=e1, p=passport
        employee_take_seal(eid1) must precede employee_seal_passport(eid2, p)
        """
        rules = parse_str(rule)

        steps = JarlRuleAdapter().rule_to_steps(rules[0])

        rule_header = "seal_needed_to_seal_passport"
        rule_scope = RuleScope([
            MatchCheckpoints(["employee_serve", "employee_allow_tourist"]),
            RenameArgs([ ["employee_serve", "e1", "person_name", "t"], ["employee_allow_tourist", "e2", "passport"] ]),
            CrossAndGroupByArgs([ ["employee_serve", "e1", "person_name", "t"], ["employee_allow_tourist", "e2", "passport"] ]),
            ImposeIteratorCondition("e1", "=", "e2"),
            ImposeIteratorCondition("t", "=", "tourist", True),
            ScopeBetween("employee_serve", "employee_allow_tourist")
        ])
        rule_fact = RuleFact([
            MatchCheckpoints(["employee_take_seal", "employee_seal_passport"]),
            RenameArgs([ ["employee_take_seal", "eid1"], ["employee_seal_passport", "eid2", "p"] ]),
            CrossAndGroupByArgs([ ["employee_take_seal", "eid1"], ["employee_seal_passport", "eid2", "p"] ]),
            ImposeIteratorCondition("eid1", "=", "#e1", True),
            ImposeIteratorCondition("eid2", "=", "#e1", True),
            ImposeIteratorCondition("p", "=", "#passport", True),
            CompareResultsPrecedence("employee_take_seal", "employee_seal_passport"),
            ReduceResult()
        ])
        expected_rule_adapted = JARLRule(rule, rule_header, rule_fact, rule_scope)
        expected_rule_adapted.set_dynamic_scope_arg("e1", True)
        expected_rule_adapted.set_dynamic_scope_arg("passport", False)

        self.assertEqual(expected_rule_adapted, steps)

if __name__ == '__main__':
    unittest.main()
