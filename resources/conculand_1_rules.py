from common.aggregation_steps import *
from common.jarl_rule import *

rule_1_statement = (
    "# Employees serve a person per round (they are not gnocchi)\n"
    "rule serve_once_per_round\n"
    "for every e1, e2 with e2=e1:\n"
    "between employee_ready(e1) and next employee_ready(e2):\n"
    "  for any employee_id, person_name, type with employee_id=e1:\n"
    "  employee_serve(employee_id, person_name, type)must happen 1 times\n"
)
rule_1_header = "serve_once_per_round"
rule_1_scope = RuleScope([
    MatchCheckpoints(["employee_ready"]),
    RenameArgs([ ["employee_ready", "e1"], ["employee_ready", "e2"] ]),
    CrossAndGroupByArgs([ ["employee_ready", "e1"], ["employee_ready", "e2"] ]),
    ImposeIteratorCondition("e2", "=", "e1"),
    ScopeBetween("employee_ready", "employee_ready")
])
rule_1_fact = RuleFact([
    MatchCheckpoints(["employee_serve"]),
    RenameArgs([ ["employee_serve", "employee_id", "person_name", "type"] ]),
    CrossAndGroupByArgs([ ["employee_serve"] ]),
    ImposeWildcardCondition("employee_id", "=", "#e1", True),
    CompareResultsQuantity("=", 1),
    ReduceResult()
])
rule_1 = JARLRule(rule_1_statement, rule_1_header, rule_1_fact, rule_1_scope, passed_by_default=False)
rule_1.set_dynamic_scope_arg("e1", True)

rule_2_statement = (
    "# Every tourist must wait in queue before being served\n"
    "rule tourist_wait_before_served\n"
    "for every e, person_name, t with t='tourist':\n"
    "before employee_serve(e, person_name, t):\n"
    "  for any pn with pn=person_name:\n"
    "  tourist_queued(pn) must happen 1 times\n"
)
rule_2_header = "tourist_wait_before_served"
rule_2_scope = RuleScope([
    MatchCheckpoints(["employee_serve"]),
    RenameArgs([ ["employee_serve", "e", "person_name", "t"] ]),
    CrossAndGroupByArgs([ ["employee_serve", "e", "person_name", "t"] ]),
    ImposeIteratorCondition("t", "=", "tourist", True),
    ScopeBefore("employee_serve")
])
rule_2_fact = RuleFact([
    MatchCheckpoints(["tourist_queued"]),
    RenameArgs([ ["tourist_queued", "pn"] ]),
    CrossAndGroupByArgs([ ["tourist_queued"] ]),
    ImposeWildcardCondition("pn", "=", "#person_name", True),
    CompareResultsQuantity("=", 1),
    ReduceResult()
])
rule_2 = JARLRule(rule_2_statement, rule_2_header, rule_2_fact, rule_2_scope, passed_by_default=False)
rule_2.set_dynamic_scope_arg("person_name", False)

rule_3_statement = (
    "# Every resident must wait in queue before being served\n"
    "rule resident_wait_before_served\n"
    "for every e, person_name, t with t='resident':\n"
    "before employee_serve(e, person_name, t):\n"
    "  for any pn with pn=person_name:\n"
    "  resident_queued(pn) must happen 1 times\n"
)
rule_3_header = "resident_wait_before_served"
rule_3_scope = RuleScope([
    MatchCheckpoints(["employee_serve"]),
    RenameArgs([ ["employee_serve", "e", "person_name", "t"] ]),
    CrossAndGroupByArgs([ ["employee_serve", "e", "person_name", "t"] ]),
    ImposeIteratorCondition("t", "=", "resident", True),
    ScopeBefore("employee_serve")
])
rule_3_fact = RuleFact([
    MatchCheckpoints(["resident_queued"]),
    RenameArgs([ ["resident_queued", "pn"] ]),
    CrossAndGroupByArgs([ ["resident_queued"] ]),
    ImposeWildcardCondition("pn", "=", "#person_name", True),
    CompareResultsQuantity("=", 1),
    ReduceResult()
])
rule_3 = JARLRule(rule_3_statement, rule_3_header, rule_3_fact, rule_3_scope, passed_by_default=False)
rule_3.set_dynamic_scope_arg("person_name", False)

rule_4_statement = (
    "# Every tourist shows their passport after being asked for it\n"
    "rule tourist_show_passport_when_requested\n"
    "for every e1, e2, person_name, t with e2=e1, t='tourist':\n"
    "between employee_serve(e1, person_name, t) and next employee_ready(e2):\n"
    "  for every employee_id, pn and any passport, traits with employee_id=e1, pn=person_name:\n"
    "  employee_request_passport(employee_id) must precede tourist_show_passport(pn, passport, traits)\n"
)
rule_4_header = "tourist_show_passport_when_requested"
rule_4_scope = RuleScope([
    MatchCheckpoints(["employee_serve", "employee_ready"]),
    RenameArgs([ ["employee_serve", "e1", "person_name", "t"], ["employee_ready", "e2"] ]),
    CrossAndGroupByArgs([ ["employee_serve", "e1", "person_name", "t"], ["employee_ready", "e2"] ]),
    ImposeIteratorCondition("e2", "=", "e1"),
    ImposeIteratorCondition("t", "=", "tourist", True),
    ScopeBetween("employee_serve", "employee_ready")
])
rule_4_fact = RuleFact([
    MatchCheckpoints(["employee_request_passport", "tourist_show_passport"]),
    RenameArgs([ ["employee_request_passport", "employee_id"], ["tourist_show_passport", "pn", "passport", "traits"] ]),
    CrossAndGroupByArgs([ ["employee_request_passport", "employee_id"], ["tourist_show_passport", "pn"] ]),
    ImposeIteratorCondition("employee_id", "=", "#e1", True),
    ImposeIteratorCondition("pn", "=", "#person_name", True),
    CompareResultsPrecedence("employee_request_passport", "tourist_show_passport"),
    ReduceResult()
])
rule_4 = JARLRule(rule_4_statement, rule_4_header, rule_4_fact, rule_4_scope)
rule_4.set_dynamic_scope_arg("e1", True)
rule_4.set_dynamic_scope_arg("person_name", True)

rule_5_statement = (
    "# Every resident shows their document after being asked for it\n"
    "rule resident_show_document_when_requested\n"
    "for every e1, e2, person_name, t with e2=e1, t='resident':\n"
    "between employee_serve(e1, person_name, t) and next employee_ready(e2):\n"
    "  for every employee_id, pn and any document, gender with employee_id=e1, pn=person_name:\n"
    "  employee_request_document(employee_id) must precede resident_show_document(pn, document, gender)\n"
)
rule_5_header = "resident_show_document_when_requested"
rule_5_scope = RuleScope([
    MatchCheckpoints(["employee_serve", "employee_ready"]),
    RenameArgs([ ["employee_serve", "e1", "person_name", "t"], ["employee_ready", "e2"] ]),
    CrossAndGroupByArgs([ ["employee_serve", "e1", "person_name", "t"], ["employee_ready", "e2"] ]),
    ImposeIteratorCondition("e2", "=", "e1"),
    ImposeIteratorCondition("t", "=", "resident", True),
    ScopeBetween("employee_serve", "employee_ready")
])
rule_5_fact = RuleFact([
    MatchCheckpoints(["employee_request_document", "resident_show_document"]),
    RenameArgs([ ["employee_request_document", "employee_id"], ["resident_show_document", "pn", "document", "gender"] ]),
    CrossAndGroupByArgs([ ["employee_request_document", "employee_id"], ["resident_show_document", "pn"] ]),
    ImposeIteratorCondition("employee_id", "=", "#e1", True),
    ImposeIteratorCondition("pn", "=", "#person_name", True),
    CompareResultsPrecedence("employee_request_document", "resident_show_document"),
    ReduceResult()
])
rule_5 = JARLRule(rule_5_statement, rule_5_header, rule_5_fact, rule_5_scope)
rule_5.set_dynamic_scope_arg("e1", True)
rule_5.set_dynamic_scope_arg("person_name", True)

rule_6_statement = (
    "# Every tourist shows their passport once before dying\n"
    "rule tourist_show_passport_before_die\n"
    "for every pn1, p1, t1, pn2, p2, t2 with pn2=pn1, p2=p1, t2=t1:\n"
    "between tourist_spawn(pn1, p1, t1) and next tourist_die(pn2, p2, t2):\n"
    "  for any person_name, passport, traits with person_name=pn1, passport=p1, traits=t1:\n"
    "  tourist_show_passport(person_name, passport, traits) must happen 1 times\n"
)
rule_6_header = "tourist_show_passport_before_die"
rule_6_scope = RuleScope([
    MatchCheckpoints(["tourist_spawn", "tourist_die"]),
    RenameArgs([ ["tourist_spawn", "pn1", "p1", "t1"], ["tourist_die", "pn2", "p2", "t2"] ]),
    CrossAndGroupByArgs([ ["tourist_spawn", "pn1", "p1", "t1"], ["tourist_die", "pn2", "p2", "t2"] ]),
    ImposeIteratorCondition("pn2", "=", "pn1"),
    ImposeIteratorCondition("p2", "=", "p1"),
    ImposeIteratorCondition("t2", "=", "t1"),
    ScopeBetween("tourist_spawn", "tourist_die")
])
rule_6_fact = RuleFact([
    MatchCheckpoints(["tourist_show_passport"]),
    RenameArgs([ ["tourist_show_passport", "person_name", "passport", "traits"] ]),
    CrossAndGroupByArgs([ ["tourist_show_passport"] ]),
    ImposeWildcardCondition("person_name", "=", "#pn1", True),
    ImposeWildcardCondition("passport", "=", "#p1", True),
    ImposeWildcardCondition("traits", "=", "#t1", True),
    CompareResultsQuantity("=", 1),
    ReduceResult()
])
rule_6 = JARLRule(rule_6_statement, rule_6_header, rule_6_fact, rule_6_scope, passed_by_default=False)
rule_6.set_dynamic_scope_arg("pn1", True)
rule_6.set_dynamic_scope_arg("p1", True)
rule_6.set_dynamic_scope_arg("t1", True)

rule_7_statement = (
    "# Every resident shows their document once before dying\n"
    "rule resident_show_document_before_die\n"
    "for every pn1, d1, g1, pn2, d2, g2 with pn2=pn1, d2=d1, g2=g1:\n"
    "between resident_spawn(pn1, d1, g1) and next resident_die(pn2, d2, g2):\n"
    "  for any person_name, document, gender with person_name=pn1, document=d1, gender=g1:\n"
    "  resident_show_document(person_name, document, gender) must happen 1 times\n"
)
rule_7_header = "resident_show_document_before_die"
rule_7_scope = RuleScope([
    MatchCheckpoints(["resident_spawn", "resident_die"]),
    RenameArgs([ ["resident_spawn", "pn1", "d1", "g1"], ["resident_die", "pn2", "d2", "g2"] ]),
    CrossAndGroupByArgs([ ["resident_spawn", "pn1", "d1", "g1"], ["resident_die", "pn2", "d2", "g2"] ]),
    ImposeIteratorCondition("pn2", "=", "pn1"),
    ImposeIteratorCondition("d2", "=", "d1"),
    ImposeIteratorCondition("g2", "=", "g1"),
    ScopeBetween("resident_spawn", "resident_die")
])
rule_7_fact = RuleFact([
    MatchCheckpoints(["resident_show_document"]),
    RenameArgs([ ["resident_show_document", "person_name", "document", "gender"] ]),
    CrossAndGroupByArgs([ ["resident_show_document"] ]),
    ImposeWildcardCondition("person_name", "=", "#pn1", True),
    ImposeWildcardCondition("document", "=", "#d1", True),
    ImposeWildcardCondition("gender", "=", "#g1", True),
    CompareResultsQuantity("=", 1),
    ReduceResult()
])
rule_7 = JARLRule(rule_7_statement, rule_7_header, rule_7_fact, rule_7_scope, passed_by_default=False)
rule_7.set_dynamic_scope_arg("pn1", True)
rule_7.set_dynamic_scope_arg("d1", True)
rule_7.set_dynamic_scope_arg("g1", True)

rule_8_statement = (
    "# Tourists passports are sealed once before being allowed in\n"
    "rule tourist_passport_is_sealed\n"
    "for every employee_id, passport:\n"
    "before employee_allow_tourist(employee_id, passport):\n"
    "  for any e, p with e=employee_id, p=passport:\n"
    "  employee_seal_passport(e, p) must happen 1 times\n"
)
rule_8_header = "tourist_passport_is_sealed"
rule_8_scope = RuleScope([
    MatchCheckpoints(["employee_allow_tourist"]),
    RenameArgs([ ["employee_allow_tourist", "employee_id", "passport"] ]),
    CrossAndGroupByArgs([ ["employee_allow_tourist", "employee_id", "passport"] ]),
    ScopeBefore("employee_allow_tourist")
])
rule_8_fact = RuleFact([
    MatchCheckpoints(["employee_seal_passport"]),
    RenameArgs([ ["employee_seal_passport", "e", "p"] ]),
    CrossAndGroupByArgs([ ["employee_seal_passport"] ]),
    ImposeWildcardCondition("e", "=", "#employee_id", True),
    ImposeWildcardCondition("p", "=", "#passport", True),
    CompareResultsQuantity("=", 1),
    ReduceResult()
])
rule_8 = JARLRule(rule_8_statement, rule_8_header, rule_8_fact, rule_8_scope, passed_by_default=False)
rule_8.set_dynamic_scope_arg("employee_id", False)
rule_8.set_dynamic_scope_arg("passport", False)

rule_9_statement = (
    "# A seal must be taken before sealing a passport\n"
    "rule seal_needed_to_seal_passport\n"
    "for every e1, e2, person_name, t, passport with e2=e1, t='tourist':\n"
    "between employee_serve(e1, person_name, t) and next employee_allow_tourist(e2, passport):\n"
    "  for every eid1, eid2, p with eid1=e1, eid2=e1, p=passport:\n"
    "  employee_take_seal(eid1) must precede employee_seal_passport(eid2, p)\n"
)
rule_9_header = "seal_needed_to_seal_passport"
rule_9_scope = RuleScope([
    MatchCheckpoints(["employee_serve", "employee_allow_tourist"]),
    RenameArgs([ ["employee_serve", "e1", "person_name", "t"], ["employee_allow_tourist", "e2", "passport"] ]),
    CrossAndGroupByArgs([ ["employee_serve", "e1", "person_name", "t"], ["employee_allow_tourist", "e2", "passport"] ]),
    ImposeIteratorCondition("e2", "=", "e1"),
    ImposeIteratorCondition("t", "=", "tourist", True),
    ScopeBetween("employee_serve", "employee_allow_tourist")
])
rule_9_fact = RuleFact([
    MatchCheckpoints(["employee_take_seal", "employee_seal_passport"]),
    RenameArgs([ ["employee_take_seal", "eid1"], ["employee_seal_passport", "eid2", "p"] ]),
    CrossAndGroupByArgs([ ["employee_take_seal", "eid1"], ["employee_seal_passport", "eid2", "p"] ]),
    ImposeIteratorCondition("eid1", "=", "#e1", True),
    ImposeIteratorCondition("eid2", "=", "#e1", True),
    ImposeIteratorCondition("p", "=", "#passport", True),
    CompareResultsPrecedence("employee_take_seal", "employee_seal_passport"),
    ReduceResult()
])
rule_9 = JARLRule(rule_9_statement, rule_9_header, rule_9_fact, rule_9_scope)
rule_9.set_dynamic_scope_arg("e1", True)
rule_9.set_dynamic_scope_arg("passport", False)

rule_10_statement = (
    "# There are only 3 seals available\n"
    "rule seals_available_are_3\n"
    "for any e1, e2:\n"
    "between employee_take_seal(e1) and next employee_return_seal(e2):\n"
    "  for any e:\n"
    "  employee_take_seal(e) must happen at most 3 times\n"
)
rule_10_header = "seals_available_are_3"
rule_10_scope = RuleScope([
    MatchCheckpoints(["employee_take_seal", "employee_return_seal"]),
    RenameArgs([ ["employee_take_seal", "e1"], ["employee_return_seal", "e2"] ]),
    CrossAndGroupByArgs([ ["employee_take_seal"], ["employee_return_seal"] ]),
    ScopeBetween("employee_take_seal", "employee_return_seal")
])
rule_10_fact = RuleFact([
    MatchCheckpoints(["employee_take_seal"]),
    RenameArgs([ ["employee_take_seal", "e"] ]),
    CrossAndGroupByArgs([ ["employee_take_seal"] ]),
    CompareResultsQuantity("<=", 3),
    ReduceResult()
])
rule_10 = JARLRule(rule_10_statement, rule_10_header, rule_10_fact, rule_10_scope)

rule_11_statement = (
    "# 12 people are served\n"
    "rule twelve_people_served\n"
    "for any e, p, t:\n"
    "employee_serve(e, p, t) must happen 12 times\n"
)
rule_11_header = "twelve_people_served"
rule_11_fact = RuleFact([
    MatchCheckpoints(["employee_serve"]),
    RenameArgs([ ["employee_serve", "e", "p", "t"] ]),
    CrossAndGroupByArgs([ ["employee_serve"] ]),
    CompareResultsQuantity("=", 12),
    ReduceResult()
])
rule_11 = JARLRule(rule_11_statement, rule_11_header, rule_11_fact, passed_by_default=False)

rule_12_statement = (
    "# All taken seals are later returned\n"
    "rule serve_once_per_round\n"
    "for every employee_id:\n"
    "after employee_take_seal(employee_id):\n"
    "  for any e with e=employee_id:\n"
    "  employee_return_seal(e) must happen at least 1 times\n"
)
rule_12_header = "serve_once_per_round"
rule_12_scope = RuleScope([
    MatchCheckpoints(["employee_take_seal"]),
    RenameArgs([ ["employee_take_seal", "employee_id"] ]),
    CrossAndGroupByArgs([ ["employee_take_seal", "employee_id"] ]),
    ScopeAfter("employee_take_seal")
])
rule_12_fact = RuleFact([
    MatchCheckpoints(["employee_return_seal"]),
    RenameArgs([ ["employee_return_seal", "e"] ]),
    CrossAndGroupByArgs([ ["employee_return_seal"] ]),
    ImposeWildcardCondition("e", "=", "#employee_id", True),
    CompareResultsQuantity(">=", 1),
    ReduceResult()
])
rule_12 = JARLRule(rule_12_statement, rule_12_header, rule_12_fact, rule_12_scope, passed_by_default=False)
rule_12.set_dynamic_scope_arg("employee_id", True)



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