from common.aggregation_steps import *
from common.jarl_rule import *

rule_1_statement = (
    "# If a writer is on a room, readers cannot enter\n"
    "rule readers_cant_enter_if_writer_inside\n"
    "for every w1, w2, room1, room2 with w2=w1, room2=room1:\n"
    "between writer_enter(w1, room1) and next writer_exit(w2, room2):\n"
    "  for every room and any r with room=room1:\n"
    "  reader_enter(r, room) must not happen\n"
)
rule_1_header = "readers_cant_enter_if_writer_inside"
rule_1_scope = RuleScope([
    MatchCheckpoints(["writer_enter", "writer_exit"]),
    RenameArgs([["writer_enter", "w1", "room1"], ["writer_exit", "w2", "room2"]]),
    CrossAndGroupByArgs([["writer_enter", "w1", "room1"], ["writer_exit", "w2", "room2"]]),
    ImposeIteratorCondition("w2", "=", "w1"),
    ImposeIteratorCondition("room2", "=", "room1"),
    ScopeBetween("writer_enter", "writer_exit")
])
rule_1_fact = RuleFact([
    MatchCheckpoints(["reader_enter"]),
    RenameArgs([["reader_enter", "r", "room"]]),
    CrossAndGroupByArgs([["reader_enter", "room"]]),
    ImposeIteratorCondition("room", "=", "#room1", True),
    CompareResultsQuantity("=", 0),
    ReduceResult()
])
rule_1 = JARLRule(rule_1_statement, rule_1_header, rule_1_fact, rule_1_scope, passed_by_default=True)
rule_1.set_dynamic_scope_arg("room1", True)

rule_2_statement = (
    "# If a reader is on a room, writers cannot enter\n"
    "rule writers_cant_enter_if_reader_inside\n"
    "for every r1, r2, room1, room2 with r2=r1, room2=room1:\n"
    "between reader_enter(r1, room1) and next reader_exit(r2, room2):\n"
    "  for every room and any w with room=room1:\n"
    "  writer_enter(w, room) must not happen\n"
)
rule_2_header = "writers_cant_enter_if_reader_inside"
rule_2_scope = RuleScope([
    MatchCheckpoints(["reader_enter", "reader_exit"]),
    RenameArgs([["reader_enter", "r1", "room1"], ["reader_exit", "r2", "room2"]]),
    CrossAndGroupByArgs([["reader_enter", "r1", "room1"], ["reader_exit", "r2", "room2"]]),
    ImposeIteratorCondition("r2", "=", "r1"),
    ImposeIteratorCondition("room2", "=", "room1"),
    ScopeBetween("reader_enter", "reader_exit")
])
rule_2_fact = RuleFact([
    MatchCheckpoints(["writer_enter"]),
    RenameArgs([["writer_enter", "w", "room"]]),
    CrossAndGroupByArgs([["writer_enter", "room"]]),
    ImposeIteratorCondition("room", "=", "#room1", True),
    CompareResultsQuantity("=", 0),
    ReduceResult()
])
rule_2 = JARLRule(rule_2_statement, rule_2_header, rule_2_fact, rule_2_scope, passed_by_default=True)
rule_2.set_dynamic_scope_arg("room1", True)

rule_3_statement = (
    "# Each reader reads a room 2 times\n"
    "rule readers_read_two_times\n"
    "for every r and any room, msg:\n"
    "read_room(r, room, msg) must happen 2 times\n"
)
rule_3_header = "readers_read_two_times"
rule_3_fact = RuleFact([
    MatchCheckpoints(["read_room"]),
    RenameArgs([["read_room", "r", "room", "msg"]]),
    CrossAndGroupByArgs([["read_room", "r"]]),
    CompareResultsQuantity("=", 2),
    ReduceResult()
])
rule_3 = JARLRule(rule_3_statement, rule_3_header, rule_3_fact, passed_by_default=False)

rule_4_statement = (
    "# Each writer writes a room 4 times\n"
    "rule writers_write_four_times\n"
    "for every w and any room, msg:\n"
    "write_room(w, room, msg) must happen 4 times\n"
)
rule_4_header = "writers_write_four_times"
rule_4_fact = RuleFact([
    MatchCheckpoints(["write_room"]),
    RenameArgs([["write_room", "w", "room", "msg"]]),
    CrossAndGroupByArgs([["write_room", "w"]]),
    CompareResultsQuantity("=", 4),
    ReduceResult()
])
rule_4 = JARLRule(rule_4_statement, rule_4_header, rule_4_fact, passed_by_default=False)

rule_5_statement = (
    "# Only one writer can be on a room at the same time\n"
    "rule one_writer_at_room\n"
    "for every w1, w2, room1, room2 with w2=w1, room2=room1:\n"
    "between writer_enter(w1, room1) and next writer_exit(w2, room2):\n"
    "  for every room and any w with room=room1, w!=w1:\n"
    "  writer_enter(w, room) must not happen\n"
)
rule_5_header = "one_writer_at_room"
rule_5_scope = RuleScope([
    MatchCheckpoints(["writer_enter", "writer_exit"]),
    RenameArgs([["writer_enter", "w1", "room1"], ["writer_exit", "w2", "room2"]]),
    CrossAndGroupByArgs([["writer_enter", "w1", "room1"], ["writer_exit", "w2", "room2"]]),
    ImposeIteratorCondition("w2", "=", "w1"),
    ImposeIteratorCondition("room2", "=", "room1"),
    ScopeBetween("writer_enter", "writer_exit")
])
rule_5_fact = RuleFact([
    MatchCheckpoints(["writer_enter"]),
    RenameArgs([["writer_enter", "w", "room"]]),
    CrossAndGroupByArgs([["writer_enter", "room"]]),
    ImposeIteratorCondition("room", "=", "#room1", True),
    ImposeWildcardCondition("w", "!=", "#w1", True),
    CompareResultsQuantity("=", 0),
    ReduceResult()
])
rule_5 = JARLRule(rule_5_statement, rule_5_header, rule_5_fact, rule_5_scope, passed_by_default=True)
rule_5.set_dynamic_scope_arg("w1", True)
rule_5.set_dynamic_scope_arg("room1", True)

rule_6_statement = (
    "# Writer writes the room (only one time) when inside\n"
    "rule writer_writes_room_when_inside\n"
    "for every w1, w2, room1, room2 with w2=w1, room2=room1:\n"
    "between writer_enter(w1, room1) and next writer_exit(w2, room2):\n"
    "  for every room, w and any msg with room=room1, w=w1:\n"
    "  write_room(w, room, msg) must happen 1 times\n"
)
rule_6_header = "writer_writes_room_when_inside"
rule_6_scope = RuleScope([
    MatchCheckpoints(["writer_enter", "writer_exit"]),
    RenameArgs([["writer_enter", "w1", "room1"], ["writer_exit", "w2", "room2"]]),
    CrossAndGroupByArgs([["writer_enter", "w1", "room1"], ["writer_exit", "w2", "room2"]]),
    ImposeIteratorCondition("w2", "=", "w1"),
    ImposeIteratorCondition("room2", "=", "room1"),
    ScopeBetween("writer_enter", "writer_exit")
])
rule_6_fact = RuleFact([
    MatchCheckpoints(["write_room"]),
    RenameArgs([["write_room", "w", "room", "msg"]]),
    CrossAndGroupByArgs([["write_room", "w", "room"]]),
    ImposeIteratorCondition("room", "=", "#room1", True),
    ImposeIteratorCondition("w", "=", "#w1", True),
    CompareResultsQuantity("=", 1),
    ReduceResult()
])
rule_6 = JARLRule(rule_6_statement, rule_6_header, rule_6_fact, rule_6_scope, passed_by_default=False)
rule_6.set_dynamic_scope_arg("w1", True)
rule_6.set_dynamic_scope_arg("room1", True)

rule_7_statement = (
    "# Reader reads the room (only one time) when inside\n"
    "rule reader_reads_room_when_inside\n"
    "for every r1, r2, room1, room2 with r2=r1, room2=room1:\n"
    "between reader_enter(r1, room1) and next reader_exit(r2, room2):\n"
    "  for every room, r and any msg with room=room1, r=r1:\n"
    "  read_room(r, room, msg) must happen 1 times\n"
)
rule_7_header = "reader_reads_room_when_inside"
rule_7_scope = RuleScope([
    MatchCheckpoints(["reader_enter", "reader_exit"]),
    RenameArgs([["reader_enter", "r1", "room1"], ["reader_exit", "r2", "room2"]]),
    CrossAndGroupByArgs([["reader_enter", "r1", "room1"], ["reader_exit", "r2", "room2"]]),
    ImposeIteratorCondition("r2", "=", "r1"),
    ImposeIteratorCondition("room2", "=", "room1"),
    ScopeBetween("reader_enter", "reader_exit")
])
rule_7_fact = RuleFact([
    MatchCheckpoints(["read_room"]),
    RenameArgs([["read_room", "r", "room", "msg"]]),
    CrossAndGroupByArgs([["read_room", "room", "r"]]),
    ImposeIteratorCondition("room", "=", "#room1", True),
    ImposeIteratorCondition("r", "=", "#r1", True),
    CompareResultsQuantity("=", 1),
    ReduceResult()
])
rule_7 = JARLRule(rule_7_statement, rule_7_header, rule_7_fact, rule_7_scope, passed_by_default=False)
rule_7.set_dynamic_scope_arg("r1", True)
rule_7.set_dynamic_scope_arg("room1", True)

rule_8_statement = (
    "# Writers cannot write before entering a room first\n"
    "rule writers_cant_write_when_outside\n"
    "for every w1, w2 and any room1, room2 with w2=w1:\n"
    "between writer_exit(w1, room1) and next writer_enter(w2, room2):\n"
    "  for every w and any room, msg with w=w1:\n"
    "  write_room(w, room, msg) must happen 0 times\n"
)
rule_8_header = "writers_cant_write_when_outside"
rule_8_scope = RuleScope([
    MatchCheckpoints(["writer_exit", "writer_enter"]),
    RenameArgs([["writer_exit", "w1", "room1"], ["writer_enter", "w2", "room2"]]),
    CrossAndGroupByArgs([["writer_exit", "w1"], ["writer_enter", "w2"]]),
    ImposeIteratorCondition("w2", "=", "w1"),
    ScopeBetween("writer_exit", "writer_enter")
])
rule_8_fact = RuleFact([
    MatchCheckpoints(["write_room"]),
    RenameArgs([["write_room", "w", "room", "msg"]]),
    CrossAndGroupByArgs([["write_room", "w"]]),
    ImposeIteratorCondition("w", "=", "#w1", True),
    CompareResultsQuantity("=", 0),
    ReduceResult()
])
rule_8 = JARLRule(rule_8_statement, rule_8_header, rule_8_fact, rule_8_scope, passed_by_default=True)
rule_8.set_dynamic_scope_arg("w1", True)

rule_9_statement = (
    "# Readers cannot read before entering a room first\n"
    "rule readers_cant_read_when_outside\n"
    "for every r1, r2 and any room1, room2 with r2=r1:\n"
    "between reader_exit(r1, room1) and next reader_enter(r2, room2):\n"
    "  for every r and any room, msg with r=r1:\n"
    "  read_room(r, room, msg) must happen 0 times\n"
)
rule_9_header = "readers_cant_read_when_outside"
rule_9_scope = RuleScope([
    MatchCheckpoints(["reader_exit", "reader_enter"]),
    RenameArgs([["reader_exit", "r1", "room1"], ["reader_enter", "r2", "room2"]]),
    CrossAndGroupByArgs([["reader_exit", "r1"], ["reader_enter", "r2"]]),
    ImposeIteratorCondition("r2", "=", "r1"),
    ScopeBetween("reader_exit", "reader_enter")
])
rule_9_fact = RuleFact([
    MatchCheckpoints(["read_room"]),
    RenameArgs([["read_room", "r", "room", "msg"]]),
    CrossAndGroupByArgs([["read_room", "r"]]),
    ImposeIteratorCondition("r", "=", "#r1", True),
    CompareResultsQuantity("=", 0),
    ReduceResult()
])
rule_9 = JARLRule(rule_9_statement, rule_9_header, rule_9_fact, rule_9_scope, passed_by_default=True)
rule_9.set_dynamic_scope_arg("r1", True)

rule_10_statement = (
    "# If a reader reads something, a writer wrote it\n"
    "rule reader_reads_something_written\n"
    "for every r, room, msg with msg!='NULL':\n"
    "before read_room(r, room, msg):\n"
    "  for any roomid, m, w with roomid=room, m=msg:\n"
    "  write_room(w, roomid, m) must happen at least 1 times\n"
)
rule_10_header = "reader_reads_something_written"
rule_10_scope = RuleScope([
    MatchCheckpoints(["read_room"]),
    RenameArgs([["read_room", "r", "room", "msg"]]),
    CrossAndGroupByArgs([["read_room", "r", "room", "msg"]]),
    ImposeIteratorCondition("msg", "!=", "NULL", True),
    ScopeBefore("read_room")
])
rule_10_fact = RuleFact([
    MatchCheckpoints(["write_room"]),
    RenameArgs([["write_room", "w", "roomid", "m"]]),
    CrossAndGroupByArgs([["write_room"]]),
    ImposeWildcardCondition("roomid", "=", "#room", True),
    ImposeWildcardCondition("m", "=", "#msg", True),
    CompareResultsQuantity(">=", 1),
    ReduceResult()
])
rule_10 = JARLRule(rule_10_statement, rule_10_header, rule_10_fact, rule_10_scope, passed_by_default=False)
rule_10.set_dynamic_scope_arg("room", False)
rule_10.set_dynamic_scope_arg("msg", False)

rule_11_statement = (
    "# Reader always reads room last message\n"
    "rule reader_reads_what_was_last_written\n"
    "for every r1, m1, r2, m2 and any r, w with m1!='NULL', r2=r1, m2=m1:\n"
    "between read_room(r, r1, m1) and previous write_room(w, r2, m2):\n"
    "  for any wid, roomid, m with roomid=r2, m!=m2:\n"
    "  write_room(wid, roomid, m) must happen 0 times\n"
)
rule_11_header = "reader_reads_what_was_last_written"
rule_11_scope = RuleScope([
    MatchCheckpoints(["read_room", "write_room"]),
    RenameArgs([["read_room", "r", "r1", "m1"], ["write_room", "w", "r2", "m2"]]),
    CrossAndGroupByArgs([["read_room", "r1", "m1"], ["write_room", "r2", "m2"]]),
    ImposeIteratorCondition("m1", "!=", "NULL", True),
    ImposeIteratorCondition("r2", "=", "r1"),
    ImposeIteratorCondition("m2", "=", "m1"),
    ScopeBetween("read_room", "write_room", False)
])
rule_11_fact = RuleFact([
    MatchCheckpoints(["write_room"]),
    RenameArgs([["write_room", "wid", "roomid", "m"]]),
    CrossAndGroupByArgs([["write_room"]]),
    ImposeWildcardCondition("roomid", "=", "#r2", True),
    ImposeWildcardCondition("m", "!=", "#m2", True),
    CompareResultsQuantity("=", 0),
    ReduceResult()
])
rule_11 = JARLRule(rule_11_statement, rule_11_header, rule_11_fact, rule_11_scope, passed_by_default=True)
rule_11.set_dynamic_scope_arg("r2", True)
rule_11.set_dynamic_scope_arg("m2", True)

rule_12_statement = (
    "# If a reader read NULL it is because the room was never written\n"
    "rule reader_reads_null_on_pristine_room\n"
    "for every r, room, msg with msg='NULL':\n"
    "before read_room(r, room, msg):\n"
    "  for any roomid, m, w with roomid=room:\n"
    "  write_room(w, roomid, m) must happen 0 times\n"
)
rule_12_header = "reader_reads_null_on_pristine_room"
rule_12_scope = RuleScope([
    MatchCheckpoints(["read_room"]),
    RenameArgs([["read_room", "r", "room", "msg"]]),
    CrossAndGroupByArgs([["read_room", "r", "room", "msg"]]),
    ImposeIteratorCondition("msg", "=", "NULL", True),
    ScopeBefore("read_room")
])
rule_12_fact = RuleFact([
    MatchCheckpoints(["write_room"]),
    RenameArgs([["write_room", "w", "roomid", "m"]]),
    CrossAndGroupByArgs([["write_room"]]),
    ImposeWildcardCondition("roomid", "=", "#room", True),
    CompareResultsQuantity("=", 0),
    ReduceResult()
])
rule_12 = JARLRule(rule_12_statement, rule_12_header, rule_12_fact, rule_12_scope, passed_by_default=True)
rule_12.set_dynamic_scope_arg("room", False)

all_rules = [
    rule_1,
    rule_2,
    rule_3,
    rule_4,
    rule_5,
    rule_6,
    rule_7,
    rule_8,
    rule_9,
    rule_10,
    rule_11,
    rule_12,
]
