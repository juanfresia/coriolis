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


    def test_adapter_rule_checker_smokers_2(self):
        rule = """
        rule smoker_took_two_elements
        for any s
        between agent_wake() and next smoker_smoke(s)
        for any sid, e with sid=s
        smoker_take_element(sid, e) must happen 2 times
        """
        rule_header = "smoker_took_two_elements"
        rule_scope = RuleScope([
            MatchCheckpoints(["agent_wake", "smoker_smoke"]),
            RenameArgs([ ["smoker_smoke", "s"] ]),
            CrossAndGroupByArgs([ ["agent_wake"], ["smoker_smoke"] ]),
            ScopeBetween("agent_wake", "smoker_smoke")
        ])
        rule_fact = RuleFact([
            MatchCheckpoints(["smoker_take_element"]),
            RenameArgs([ ["smoker_take_element", "sid", "e"] ]),
            CrossAndGroupByArgs([ ["smoker_take_element"] ]),
            ImposeWildcardCondition("sid", "=", "#s", True),
            CompareResultsQuantity("=", 2),
            ReduceResult()
        ])
        expected_rule = JARLRule(rule, rule_header, rule_fact, rule_scope, passed_by_default=False)
        expected_rule.set_dynamic_scope_arg("s", False)

        rules = parse_str(rule)
        steps = JarlRuleAdapter().rule_to_steps(rules[0])
        self.assertEqual(expected_rule, steps)

    def test_adapter_rule_checker_smokers_5(self):
        rule = (
            "# Agent produces 2 items per round\n"
            "rule two_produce_per_round\n"
            "between agent_wake() and next agent_sleep():\n"
            "  for any e:\n"
            "  agent_produce(e) must happen 2 times\n"
        )
        rule_header = "two_produce_per_round"
        rule_scope = RuleScope([
            MatchCheckpoints(["agent_wake", "agent_sleep"]),
            CrossAndGroupByArgs([["agent_wake"], ["agent_sleep"]]),
            ScopeBetween("agent_wake", "agent_sleep")
        ])
        rule_fact = RuleFact([
            MatchCheckpoints(["agent_produce"]),
            RenameArgs([["agent_produce", "e"]]),
            CrossAndGroupByArgs([["agent_produce"]]),
            CompareResultsQuantity("=", 2),
            ReduceResult()
        ])
        expected_rule = JARLRule(rule, rule_header, rule_fact, rule_scope, passed_by_default=False)

        rules = parse_str(rule)
        steps = JarlRuleAdapter().rule_to_steps(rules[0])
        self.assertEqual(expected_rule, steps)

    def test_adapter_rule_checker_smokers_8(self):
        rule = """
        rule smokers_smoke_while_awake
        for every s1, s2 with s1=s2
        between smoker_sleep(s1) and next smoker_sleep(s2)
        for any s with s=s1
        smoker_smoke(s) must happen 1 times
        """
        rule_header = "smokers_smoke_while_awake"
        rule_scope = RuleScope([
            MatchCheckpoints(["smoker_sleep"]),
            RenameArgs([ ["smoker_sleep", "s1"], ["smoker_sleep", "s2"] ]),
            CrossAndGroupByArgs([ ["smoker_sleep", "s1"], ["smoker_sleep", "s2"] ]),
            ImposeIteratorCondition("s1", "=", "s2"),
            ScopeBetween("smoker_sleep", "smoker_sleep")
        ])
        rule_fact = RuleFact([
            MatchCheckpoints(["smoker_smoke"]),
            RenameArgs([ ["smoker_smoke", "s"] ]),
            CrossAndGroupByArgs([ ["smoker_smoke"] ]),
            ImposeWildcardCondition("s", "=", "#s1", True),
            CompareResultsQuantity("=", 1),
            ReduceResult()
        ])
        expected_rule = JARLRule(rule, rule_header, rule_fact, rule_scope, passed_by_default=False)
        expected_rule.set_dynamic_scope_arg("s1", True)

        rules = parse_str(rule)
        steps = JarlRuleAdapter().rule_to_steps(rules[0])
        self.assertEqual(expected_rule, steps)

    def test_adapter_rule_checker_readers_writers_5(self):
        rule = """
        rule one_writer_at_room
        for every w1, w2, room1, room2 with w1=w2, room1=room2
        between writer_enter(w1, room1) and next writer_exit(w2, room2)
        for every room and any w with room=room1, w!=w1
        writer_enter(w, room) must not happen
        """

        rule_header = "one_writer_at_room"
        rule_scope = RuleScope([
            MatchCheckpoints(["writer_enter", "writer_exit"]),
            RenameArgs([["writer_enter", "w1", "room1"], ["writer_exit", "w2", "room2"]]),
            CrossAndGroupByArgs([["writer_enter", "w1", "room1"], ["writer_exit", "w2", "room2"]]),
            ImposeIteratorCondition("w1", "=", "w2"),
            ImposeIteratorCondition("room1", "=", "room2"),
            ScopeBetween("writer_enter", "writer_exit")
        ])
        rule_fact = RuleFact([
            MatchCheckpoints(["writer_enter"]),
            RenameArgs([["writer_enter", "w", "room"]]),
            CrossAndGroupByArgs([["writer_enter", "room"]]),
            ImposeIteratorCondition("room", "=", "#room1", True),
            ImposeWildcardCondition("w", "!=", "#w1", True),
            CompareResultsQuantity("=", 0),
            ReduceResult()
        ])
        expected_rule = JARLRule(rule, rule_header, rule_fact, rule_scope, passed_by_default=True)
        expected_rule.set_dynamic_scope_arg("w1", True)
        expected_rule.set_dynamic_scope_arg("room1", True)

        rules = parse_str(rule)
        steps = JarlRuleAdapter().rule_to_steps(rules[0])
        self.assertEqual(expected_rule, steps)

    def test_adapter_rule_checker_readers_writers_8(self):
        rule = (
            "# Writers cannot write before entering a room first\n"
            "rule writers_cant_write_when_outside\n"
            "for every w1, w2 and any room1, room2 with w2=w1:\n"
            "between writer_exit(w1, room1) and next writer_enter(w2, room2):\n"
            "  for every w and any room, msg with w=w1:\n"
            "  write_room(w, room, msg) must happen 0 times\n"
        )
        rule_header = "writers_cant_write_when_outside"
        rule_scope = RuleScope([
            MatchCheckpoints(["writer_exit", "writer_enter"]),
            RenameArgs([["writer_exit", "w1", "room1"], ["writer_enter", "w2", "room2"]]),
            CrossAndGroupByArgs([["writer_exit", "w1"], ["writer_enter", "w2"]]),
            ImposeIteratorCondition("w2", "=", "w1"),
            ScopeBetween("writer_exit", "writer_enter")
        ])
        rule_fact = RuleFact([
            MatchCheckpoints(["write_room"]),
            RenameArgs([["write_room", "w", "room", "msg"]]),
            CrossAndGroupByArgs([["write_room", "w"]]),
            ImposeIteratorCondition("w", "=", "#w1", True),
            CompareResultsQuantity("=", 0),
            ReduceResult()
        ])
        expected_rule = JARLRule(rule, rule_header, rule_fact, rule_scope, passed_by_default=True)
        expected_rule.set_dynamic_scope_arg("w1", True)

        rules = parse_str(rule)
        steps = JarlRuleAdapter().rule_to_steps(rules[0])
        self.assertEqual(expected_rule, steps)

    def test_adapter_rule_checker_readers_writers_10(self):
        rule = """
        # If a reader reads something, a writer wrote it
        rule reader_reads_something_written
        for every r, room, msg with msg!='NULL':
        before read_room(r, room, msg):
          for any roomid, m, w with roomid=room, m=msg:
          write_room(w, roomid, m) must happen at least 1 times
        """

        rule_header = "reader_reads_something_written"
        rule_scope = RuleScope([
            MatchCheckpoints(["read_room"]),
            RenameArgs([["read_room", "r", "room", "msg"]]),
            CrossAndGroupByArgs([["read_room", "r", "room", "msg"]]),
            ImposeIteratorCondition("msg", "!=", "NULL", True),
            ScopeBefore("read_room")
        ])
        rule_fact = RuleFact([
            MatchCheckpoints(["write_room"]),
            RenameArgs([["write_room", "w", "roomid", "m"]]),
            CrossAndGroupByArgs([["write_room"]]),
            ImposeWildcardCondition("roomid", "=", "#room", True),
            ImposeWildcardCondition("m", "=", "#msg", True),
            CompareResultsQuantity(">=", 1),
            ReduceResult()
        ])
        expected_rule = JARLRule(rule, rule_header, rule_fact, rule_scope, passed_by_default=False)
        expected_rule.set_dynamic_scope_arg("room", False)
        expected_rule.set_dynamic_scope_arg("msg", False)

        rules = parse_str(rule)
        steps = JarlRuleAdapter().rule_to_steps(rules[0])
        self.assertEqual(expected_rule, steps)

    def test_adapter_rule_checker_santa_1(self):
        rule = """
        rule prepare_sleigh_once_per_round
        between santa_wake() and next santa_sleep()
        prepare_sleigh() must happen at most 1 times
        """

        rule_header = "prepare_sleigh_once_per_round"
        rule_scope = RuleScope([
            MatchCheckpoints(["santa_wake", "santa_sleep"]),
            CrossAndGroupByArgs([ ["santa_wake"], ["santa_sleep"] ]),
            ScopeBetween("santa_wake", "santa_sleep")
        ])
        rule_fact = RuleFact([
            MatchCheckpoints(["prepare_sleigh"]),
            CrossAndGroupByArgs([ ["prepare_sleigh"] ]),
            CompareResultsQuantity("<=", 1),
            ReduceResult()
        ])
        expected_rule = JARLRule(rule, rule_header, rule_fact, rule_scope, passed_by_default=True)

        rules = parse_str(rule)
        steps = JarlRuleAdapter().rule_to_steps(rules[0])
        self.assertEqual(expected_rule, steps)

    def test_adapter_rule_checker_santa_6(self):
        rule = """
        rule reindeer_get_hitched_before_leaving
        for every r1, r2 with r1=r2
        between reindeer_arrive(r1) and next reindeer_leave(r2)
        for every r with r=r1
        get_hitched(r) must happen 1 times
        """

        rule_header = "reindeer_get_hitched_before_leaving"
        rule_scope = RuleScope([
            MatchCheckpoints(["reindeer_arrive", "reindeer_leave"]),
            RenameArgs([ ["reindeer_arrive", "r1"], ["reindeer_leave", "r2"] ]),
            CrossAndGroupByArgs([ ["reindeer_arrive", "r1"], ["reindeer_leave", "r2"] ]),
            ImposeIteratorCondition("r1", "=", "r2"),
            ScopeBetween("reindeer_arrive", "reindeer_leave")
        ])
        rule_fact = RuleFact([
            MatchCheckpoints(["get_hitched"]),
            RenameArgs([ ["get_hitched", "r"] ]),
            CrossAndGroupByArgs([ ["get_hitched", "r"] ]),
            ImposeIteratorCondition("r", "=", "#r1", True),
            CompareResultsQuantity("=", 1),
            ReduceResult()
        ])
        expected_rule = JARLRule(rule, rule_header, rule_fact, rule_scope, passed_by_default=False)
        expected_rule.set_dynamic_scope_arg("r1", True)

        rules = parse_str(rule)
        steps = JarlRuleAdapter().rule_to_steps(rules[0])
        self.assertEqual(expected_rule, steps)

    def test_adapter_rule_checker_santa_10(self):
        rule = """
        # Reindeers cannot be hitched if they dont arrive with Santa
        rule reindeers_cannot_be_helped_when_left
        for every r1, r2 with r1=r2:
        between reindeer_leave(r1) and next reindeer_arrive(r2):
          for every r with r=r1:
          get_hitched(r) must happen 0 times
        """

        rule_header = "reindeers_cannot_be_helped_when_left"
        rule_scope = RuleScope([
            MatchCheckpoints(["reindeer_leave", "reindeer_arrive"]),
            RenameArgs([["reindeer_leave", "r1"], ["reindeer_arrive", "r2"]]),
            CrossAndGroupByArgs([["reindeer_leave", "r1"], ["reindeer_arrive", "r2"]]),
            ImposeIteratorCondition("r1", "=", "r2"),
            ScopeBetween("reindeer_leave", "reindeer_arrive")
        ])
        rule_fact = RuleFact([
            MatchCheckpoints(["get_hitched"]),
            RenameArgs([["get_hitched", "r"]]),
            CrossAndGroupByArgs([["get_hitched", "r"]]),
            ImposeIteratorCondition("r", "=", "#r1", True),
            CompareResultsQuantity("=", 0),
            ReduceResult()
        ])
        expected_rule = JARLRule(rule, rule_header, rule_fact, rule_scope, passed_by_default=True)
        expected_rule.set_dynamic_scope_arg("r1", True)

        rules = parse_str(rule)
        steps = JarlRuleAdapter().rule_to_steps(rules[0])
        self.assertEqual(expected_rule, steps)

    def test_adapter_prod_cons_7(self):
        rule = (
            "# Items are consumed in order\n"
            "rule consume_in_order\n"
            "for every i, j and any c, d with j>i:\n"
            "consume(c, i) must precede consume(d, j)\n"
        )
        rule_header = "consume_in_order"
        rule_fact = RuleFact([
            MatchCheckpoints(["consume"]),
            RenameArgs([["consume", "c", "i"], ["consume", "d", "j"]]),
            CrossAndGroupByArgs([["consume", "i"], ["consume", "j"]]),
            ImposeIteratorCondition("j", ">", "i"),
            CompareResultsPrecedence("consume", "consume"),
            ReduceResult()
        ])
        expected_rule = JARLRule(rule, rule_header, rule_fact)

        rules = parse_str(rule)
        steps = JarlRuleAdapter().rule_to_steps(rules[0])
        self.assertEqual(expected_rule, steps)

    def test_adapter_prod_cons_9(self):
        rule = """
        # Item is consumed only once (written differently)
        rule consume_once_alt
        for any cid, iid:
        after consume(cid, iid):
          for every i and any c:
          consume(c, i) must happen 1 times
        """

        rule_header = "consume_once_alt"
        rule_scope = RuleScope([
            MatchCheckpoints(["consume"]),
            RenameArgs([["consume", "cid", "iid"]]),
            CrossAndGroupByArgs([["consume"]]),
            ScopeAfter("consume")
        ])
        rule_9_fact = RuleFact([
            MatchCheckpoints(["consume"]),
            RenameArgs([["consume", "c", "i"]]),
            CrossAndGroupByArgs([["consume", "i"]]),
            CompareResultsQuantity("=", 1),
            ReduceResult()
        ])
        expected_rule = JARLRule(rule, rule_header, rule_9_fact, rule_scope, passed_by_default=False)

        rules = parse_str(rule)
        steps = JarlRuleAdapter().rule_to_steps(rules[0])
        self.assertEqual(expected_rule, steps)

    def test_adapter_prod_cons_10(self):
        rule = """
        # Item is produced only once (written differently)
        rule produce_once_alt
        for any pid, iid:
        before produce(pid, iid):
          for every i and any p:
          produce(p, i) must happen 1 times
        """

        rule_header = "produce_once_alt"
        rule_scope = RuleScope([
            MatchCheckpoints(["produce"]),
            RenameArgs([["produce", "pid", "iid"]]),
            CrossAndGroupByArgs([["produce"]]),
            ScopeBefore("produce")
        ])
        rule_fact = RuleFact([
            MatchCheckpoints(["produce"]),
            RenameArgs([["produce", "p", "i"]]),
            CrossAndGroupByArgs([["produce", "i"]]),
            CompareResultsQuantity("=", 1),
            ReduceResult()
        ])
        expected_rule = JARLRule(rule, rule_header, rule_fact, rule_scope, passed_by_default=False)

        rules = parse_str(rule)
        steps = JarlRuleAdapter().rule_to_steps(rules[0])
        self.assertEqual(expected_rule, steps)

    # TODO(jfresia) This is a helper to migrate tests, remove when tests are migrated
    def test_skel(self):
        return

        rule = """
        """

        rules = parse_str(rule)
        steps = JarlRuleAdapter().rule_to_steps(rules[0])
        steps = JarlRuleAdapter().rule_to_steps(rules[0])
        i = 5
        self.assertEqual(expected_rule.fact.steps[i], steps.fact.steps[i])
        self.assertEqual(expected_rule.fact, steps.fact)
        i = 0
        self.assertEqual(expected_rule.scope.steps[i], steps.scope.steps[i])
        self.assertEqual(expected_rule.scope, steps.scope)
        self.assertEqual(expected_rule.passed_by_default, steps.passed_by_default)
        self.assertEqual(expected_rule._dynamic_args, steps._dynamic_args)
        self.assertEqual(expected_rule, steps)

if __name__ == '__main__':
    unittest.main()
