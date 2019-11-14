import unittest

from verifier.verifier_cli import *


class TestConcuspring(unittest.TestCase):
    log_file = "./resources/concuspring_1.log"
    checkpoint_file = "./resources/concuspring.chk"

    rule_1_statement = (
        "rule bouquets_made_before_boxed\n"
        "for every p1, b1, t1 and any box:\n"
        "before prod_box_bouquet(p1, b1, box, t1):\n"
        "  for every p2, b2 and any t with p2=p1, b2=b1:\n"
        "  prod_make_bouquet(p2, b2, t) must happen 1 times\n"
    )
    rule_1_header = "bouquets_made_before_boxed"
    rule_1_scope = RuleScope([
        MatchCheckpoints(['prod_box_bouquet']),
        RenameArgs([['prod_box_bouquet', 'p1', 'b1', 'box', 't1']]),
        CrossAndGroupByArgs([['prod_box_bouquet', 'p1', 'b1', 't1']]),
        ScopeBefore("prod_box_bouquet")
    ])
    rule_1_fact = RuleFact([
        MatchCheckpoints(['prod_make_bouquet']),
        RenameArgs([['prod_make_bouquet', 'p2', 'b2', 't']]),
        CrossAndGroupByArgs([['prod_make_bouquet', 'p2', 'b2']]),
        ImposeIteratorCondition("p2", "=", "#p1", using_literal=True),
        ImposeIteratorCondition("b2", "=", "#b1", using_literal=True),
        CompareResultsQuantity("=", 1),
        ReduceResult(and_results=True)
    ])
    rule_1 = JARLRule(rule_1_statement, rule_1_header, rule_1_fact, rule_1_scope, passed_by_default=False)
    rule_1.set_dynamic_scope_arg("b1", False)
    rule_1.set_dynamic_scope_arg("p1", False)

    rule_2_statement = (
        "rule ten_bouquets_per_box_when_sent\n"
        "for every p1, box1 and any dc:\n"
        "before prod_send_box(p1, box1, dc):\n"
        "  for every p2, box2 and any b, t with p2=p1, box2=box1:\n"
        "  prod_box_bouquet(p2, b, box2, t) must happen 10 times\n"
    )
    rule_2_header = "ten_bouquets_per_box_when_sent"
    rule_2_scope = RuleScope([
        MatchCheckpoints(['prod_send_box']),
        RenameArgs([['prod_send_box', 'p1', 'box1', 'dc']]),
        CrossAndGroupByArgs([['prod_send_box', 'p1', 'box1']]),
        ScopeBefore("prod_send_box")
    ])
    rule_2_fact = RuleFact([
        MatchCheckpoints(['prod_box_bouquet']),
        RenameArgs([['prod_box_bouquet', 'p2', 'b', 'box2', 't']]),
        CrossAndGroupByArgs([['prod_box_bouquet', 'p2', 'box2']]),
        ImposeIteratorCondition("p2", "=", "#p1", using_literal=True),
        ImposeIteratorCondition("box2", "=", "#box1", using_literal=True),
        CompareResultsQuantity("=", 10),
        ReduceResult(and_results=True)
    ])
    rule_2 = JARLRule(rule_2_statement, rule_2_header, rule_2_fact, rule_2_scope, passed_by_default=False)
    rule_2.set_dynamic_scope_arg("p1", False)
    rule_2.set_dynamic_scope_arg("box1", False)

    rule_3_statement = (
        "rule at_most_ten_bouquets_in_box\n"
        "for every box and any p, b, t:\n"
        "prod_box_bouquet(p, b, box, t) must happen at most 10 times\n"
    )
    rule_3_header = "at_most_ten_bouquets_in_box"
    rule_3_fact = RuleFact([
        MatchCheckpoints(['prod_box_bouquet']),
        RenameArgs([['prod_box_bouquet', 'p', 'b', 'box', 't']]),
        CrossAndGroupByArgs([['prod_box_bouquet', 'box']]),
        CompareResultsQuantity("<=", 10),
        ReduceResult(and_results=True)
    ])
    rule_3 = JARLRule(rule_3_statement, rule_3_header, rule_3_fact, passed_by_default=True)

    rule_4_statement = (
        "rule box_sent_before_received\n"
        "for every dc1, box1:\n"
        "before dc_receive_box(dc1, box1):\n"
        "  for every dc2, box2 and any p with dc2=dc1, box2=box1:\n"
        "  prod_send_box(p, box2, dc2) must happen 1 times\n"
    )
    rule_4_header = "box_sent_before_received"
    rule_4_scope = RuleScope([
        MatchCheckpoints(['dc_receive_box']),
        RenameArgs([['dc_receive_box', 'dc1', 'box1']]),
        CrossAndGroupByArgs([['dc_receive_box', 'dc1', 'box1']]),
        ScopeBefore("dc_receive_box")
    ])
    rule_4_fact = RuleFact([
        MatchCheckpoints(['prod_send_box']),
        RenameArgs([['prod_send_box', 'p', 'box2', 'dc2']]),
        CrossAndGroupByArgs([['prod_send_box', 'box2', 'dc2']]),
        ImposeIteratorCondition("dc2", "=", "#dc1", using_literal=True),
        ImposeIteratorCondition("box2", "=", "#box1", using_literal=True),
        CompareResultsQuantity("=", 1),
        ReduceResult(and_results=True)
    ])
    rule_4 = JARLRule(rule_4_statement, rule_4_header, rule_4_fact, rule_4_scope, passed_by_default=False)
    rule_4.set_dynamic_scope_arg("dc1", False)
    rule_4.set_dynamic_scope_arg("box1", False)

    rule_5_statement = (
        "rule bouquet_unboxed_only_after_received\n"
        "for every dc1, b, box1, t:\n"
        "before dc_unbox_bouquet(dc1, b, box1, t):\n"
        "  for every dc2, box2 with dc2=dc1, box2=box1:\n"
        "  dc_receive_box(dc2, box2) must happen 1 times\n"
    )
    rule_5_header = "bouquet_unboxed_only_after_received"
    rule_5_scope = RuleScope([
        MatchCheckpoints(['dc_unbox_bouquet']),
        RenameArgs([['dc_unbox_bouquet', 'dc1', 'b', 'box1', 't']]),
        CrossAndGroupByArgs([['dc_unbox_bouquet', 'dc1', 'b', 'box1', 't']]),
        ScopeBefore("dc_unbox_bouquet")
    ])
    rule_5_fact = RuleFact([
        MatchCheckpoints(['dc_receive_box']),
        RenameArgs([['dc_receive_box', 'dc2', 'box2']]),
        CrossAndGroupByArgs([['dc_receive_box', 'dc2', 'box2']]),
        ImposeIteratorCondition("dc2", "=", "#dc1", using_literal=True),
        ImposeIteratorCondition("box2", "=", "#box1", using_literal=True),
        CompareResultsQuantity("=", 1),
        ReduceResult(and_results=True)
    ])
    rule_5 = JARLRule(rule_5_statement, rule_5_header, rule_5_fact, rule_5_scope, passed_by_default=False)
    rule_5.set_dynamic_scope_arg("dc1", False)
    rule_5.set_dynamic_scope_arg("box1", False)

    rule_6_statement = (
        "rule at_most_ten_bouquets_unboxed_per_box\n"
        "for every b1 and any dc1, box1, t1, dc2, box2 with dc2=dc1, box2=box1:\n"
        "between dc_unbox_bouquet(dc1, b1, box1, t1) and previous dc_receive_box(dc2, box2):\n"
        "  for every dc3, box3 and any b2, t2 with box3=box1:\n"
        "  dc_unbox_bouquet(dc3, b2, box3, t2) must happen at most 10 times\n"
    )
    rule_6_header = "at_most_ten_bouquets_unboxed_per_box"
    rule_6_scope = RuleScope([
        MatchCheckpoints(['dc_unbox_bouquet', 'dc_receive_box']),
        RenameArgs([['dc_unbox_bouquet', 'dc1', 'b1', 'box1', 't1'], ['dc_receive_box', 'dc2', 'box2']]),
        CrossAndGroupByArgs([['dc_unbox_bouquet', 'b1'], ['dc_receive_box']]),
        ImposeWildcardCondition("dc2", "=", "dc1", using_literal=False),
        ImposeWildcardCondition("box2", "=", "box1", using_literal=False),
        ScopeBetween("dc_unbox_bouquet", "dc_receive_box", using_next=False, using_beyond=False)
    ])
    rule_6_fact = RuleFact([
        MatchCheckpoints(['dc_unbox_bouquet']),
        RenameArgs([['dc_unbox_bouquet', 'dc3', 'b2', 'box3', 't2']]),
        CrossAndGroupByArgs([['dc_unbox_bouquet', 'dc3', 'box3']]),
        ImposeIteratorCondition("box3", "=", "#box1", using_literal=True),
        CompareResultsQuantity("<=", 10),
        ReduceResult(and_results=True)
    ])
    rule_6 = JARLRule(rule_6_statement, rule_6_header, rule_6_fact, rule_6_scope, passed_by_default=True)
    rule_6.set_dynamic_scope_arg("box1", False)

    rule_7_statement = (
        "rule bouquets_only_boxed_once\n"
        "for every b, t and any p, box:\n"
        "prod_box_bouquet(p, b, box, t) must happen 1 times\n"
    )
    rule_7_header = "bouquets_only_boxed_once"
    rule_7_fact = RuleFact([
        MatchCheckpoints(['prod_box_bouquet']),
        RenameArgs([['prod_box_bouquet', 'p', 'b', 'box', 't']]),
        CrossAndGroupByArgs([['prod_box_bouquet', 'b', 't']]),
        CompareResultsQuantity("=", 1),
        ReduceResult(and_results=True)
    ])
    rule_7 = JARLRule(rule_7_statement, rule_7_header, rule_7_fact, passed_by_default=False)

    rule_8_statement = (
        "rule bouquets_only_unboxed_once\n"
        "for every b, t and any dc, box:\n"
        "dc_unbox_bouquet(dc, b, box, t) must happen 1 times\n"
    )
    rule_8_header = "bouquets_only_unboxed_once"
    rule_8_fact = RuleFact([
        MatchCheckpoints(['dc_unbox_bouquet']),
        RenameArgs([['dc_unbox_bouquet', 'dc', 'b', 'box', 't']]),
        CrossAndGroupByArgs([['dc_unbox_bouquet', 'b', 't']]),
        CompareResultsQuantity("=", 1),
        ReduceResult(and_results=True)
    ])
    rule_8 = JARLRule(rule_8_statement, rule_8_header, rule_8_fact, passed_by_default=False)

    rule_9_statement = (
        "rule hundred_bouquets_per_package_when_sent\n"
        "for every dc1, pack1 and any sp, t1:\n"
        "before dc_send_package(dc1, sp, pack1, t1):\n"
        "  for every dc2, pack2 and any b, t2 with dc2=dc1, pack2=pack1, t2=t1:\n"
        "  dc_package_bouquet(dc2, b, pack2, t2) must happen 3 times\n"
    )
    rule_9_header = "hundred_bouquets_per_package_when_sent"
    rule_9_scope = RuleScope([
        MatchCheckpoints(['dc_send_package']),
        RenameArgs([['dc_send_package', 'dc1', 'sp', 'pack1', 't1']]),
        CrossAndGroupByArgs([['dc_send_package', 'dc1', 'pack1']]),
        ScopeBefore("dc_send_package")
    ])
    rule_9_fact = RuleFact([
        MatchCheckpoints(['dc_package_bouquet']),
        RenameArgs([['dc_package_bouquet', 'dc2', 'b', 'pack2', 't2']]),
        CrossAndGroupByArgs([['dc_package_bouquet', 'dc2', 'pack2']]),
        ImposeIteratorCondition("dc2", "=", "#dc1", using_literal=True),
        ImposeIteratorCondition("pack2", "=", "#pack1", using_literal=True),
        ImposeWildcardCondition("t2", "=", "#t1", using_literal=True),
        CompareResultsQuantity("=", 3),
        ReduceResult(and_results=True)
    ])
    rule_9 = JARLRule(rule_9_statement, rule_9_header, rule_9_fact, rule_9_scope, passed_by_default=False)
    rule_9.set_dynamic_scope_arg("dc1", False)
    rule_9.set_dynamic_scope_arg("t1", False)
    rule_9.set_dynamic_scope_arg("pack1", False)

    rule_10_statement = (
        "rule bouquets_only_packaged_once\n"
        "for every b, t and any dc, pack:\n"
        "dc_package_bouquet(dc, b, pack, t) must happen 1 times\n"
    )
    rule_10_header = "bouquets_only_packaged_once"
    rule_10_fact = RuleFact([
        MatchCheckpoints(['dc_package_bouquet']),
        RenameArgs([['dc_package_bouquet', 'dc', 'b', 'pack', 't']]),
        CrossAndGroupByArgs([['dc_package_bouquet', 'b', 't']]),
        CompareResultsQuantity("=", 1),
        ReduceResult(and_results=True)
    ])
    rule_10 = JARLRule(rule_10_statement, rule_10_header, rule_10_fact, passed_by_default=False)

    rule_11_statement = (
        "rule packages_dont_have_bouquets_of_different_type\n"
        "for every dc1, pack1, t1 and any sp:\n"
        "before dc_send_package(dc1, sp, pack1, t1):\n"
        "  for every dc2, pack2, t2 and any b with dc2=dc1, pack2=pack1, t2!=t1:\n"
        "  dc_package_bouquet(dc2, b, pack2, t2) must not happen\n"
    )
    rule_11_header = "packages_dont_have_bouquets_of_different_type"
    rule_11_scope = RuleScope([
        MatchCheckpoints(['dc_send_package']),
        RenameArgs([['dc_send_package', 'dc1', 'sp', 'pack1', 't1']]),
        CrossAndGroupByArgs([['dc_send_package', 'dc1', 'pack1', 't1']]),
        ScopeBefore("dc_send_package")
    ])
    rule_11_fact = RuleFact([
        MatchCheckpoints(['dc_package_bouquet']),
        RenameArgs([['dc_package_bouquet', 'dc2', 'b', 'pack2', 't2']]),
        CrossAndGroupByArgs([['dc_package_bouquet', 'dc2', 'pack2', 't2']]),
        ImposeIteratorCondition("dc2", "=", "#dc1", using_literal=True),
        ImposeIteratorCondition("pack2", "=", "#pack1", using_literal=True),
        ImposeIteratorCondition("t2", "!=", "#t1", using_literal=True),
        CompareResultsQuantity("=", 0),
        ReduceResult(and_results=True)
    ])
    rule_11 = JARLRule(rule_11_statement, rule_11_header, rule_11_fact, rule_11_scope, passed_by_default=True)
    rule_11.set_dynamic_scope_arg("dc1", False)
    rule_11.set_dynamic_scope_arg("t1", False)
    rule_11.set_dynamic_scope_arg("pack1", False)

    rule_12_statement = (
        "rule at_most_hundred_bouquets_per_package\n"
        "for every pack and any dc, b, t:\n"
        "dc_package_bouquet(dc, b, pack, t) must happen at most 3 times\n"
    )
    rule_12_header = "at_most_hundred_bouquets_per_package"
    rule_12_fact = RuleFact([
        MatchCheckpoints(['dc_package_bouquet']),
        RenameArgs([['dc_package_bouquet', 'dc', 'b', 'pack', 't']]),
        CrossAndGroupByArgs([['dc_package_bouquet', 'pack']]),
        CompareResultsQuantity("<=", 3),
        ReduceResult(and_results=True)
    ])
    rule_12 = JARLRule(rule_12_statement, rule_12_header, rule_12_fact, passed_by_default=True)

    rule_13_statement = (
        "rule package_sent_before_received\n"
        "for every pack1, t1, sp1:\n"
        "before sp_receive_package(sp1, pack1, t1):\n"
        "  for every pack2, t2, sp2 and any dc with t2=t1, pack2=pack1, sp2=sp1:\n"
        "  dc_send_package(dc, sp2, pack2, t2) must happen 1 times\n"
    )
    rule_13_header = "package_sent_before_received"
    rule_13_scope = RuleScope([
        MatchCheckpoints(['sp_receive_package']),
        RenameArgs([['sp_receive_package', 'sp1', 'pack1', 't1']]),
        CrossAndGroupByArgs([['sp_receive_package', 'sp1', 'pack1', 't1']]),
        ScopeBefore("sp_receive_package")
    ])
    rule_13_fact = RuleFact([
        MatchCheckpoints(['dc_send_package']),
        RenameArgs([['dc_send_package', 'dc', 'sp2', 'pack2', 't2']]),
        CrossAndGroupByArgs([['dc_send_package', 'sp2', 'pack2', 't2']]),
        ImposeIteratorCondition("t2", "=", "#t1", using_literal=True),
        ImposeIteratorCondition("pack2", "=", "#pack1", using_literal=True),
        ImposeIteratorCondition("sp2", "=", "#sp1", using_literal=True),
        CompareResultsQuantity("=", 1),
        ReduceResult(and_results=True)
    ])
    rule_13 = JARLRule(rule_13_statement, rule_13_header, rule_13_fact, rule_13_scope, passed_by_default=False)
    rule_13.set_dynamic_scope_arg("sp1", False)
    rule_13.set_dynamic_scope_arg("t1", False)
    rule_13.set_dynamic_scope_arg("pack1", False)

    rule_14_statement = (
        "rule unpackaged_bouquet_was_previously_packaged\n"
        "for every b1, pack1, t1 and any sp:\n"
        "before sp_unpackage_bouquet(sp, b1, pack1, t1):\n"
        "  for every b2, t2, pack2 and any dc with b2=b1, pack2=pack1, t2=t1:\n"
        "  dc_package_bouquet(dc, b2, pack2, t2) must happen 1 times\n"
    )
    rule_14_header = "unpackaged_bouquet_was_previously_packaged"
    rule_14_scope = RuleScope([
        MatchCheckpoints(['sp_unpackage_bouquet']),
        RenameArgs([['sp_unpackage_bouquet', 'sp', 'b1', 'pack1', 't1']]),
        CrossAndGroupByArgs([['sp_unpackage_bouquet', 'b1', 'pack1', 't1']]),
        ScopeBefore("sp_unpackage_bouquet")
    ])
    rule_14_fact = RuleFact([
        MatchCheckpoints(['dc_package_bouquet']),
        RenameArgs([['dc_package_bouquet', 'dc', 'b2', 'pack2', 't2']]),
        CrossAndGroupByArgs([['dc_package_bouquet', 'b2', 'pack2', 't2']]),
        ImposeIteratorCondition("b2", "=", "#b1", using_literal=True),
        ImposeIteratorCondition("pack2", "=", "#pack1", using_literal=True),
        ImposeIteratorCondition("t2", "=", "#t1", using_literal=True),
        CompareResultsQuantity("=", 1),
        ReduceResult(and_results=True)
    ])
    rule_14 = JARLRule(rule_14_statement, rule_14_header, rule_14_fact, rule_14_scope, passed_by_default=False)
    rule_14.set_dynamic_scope_arg("b1", False)
    rule_14.set_dynamic_scope_arg("t1", False)
    rule_14.set_dynamic_scope_arg("pack1", False)

    rule_15_statement = (
        "rule at_most_hundred_bouquets_unpackaged_per_package\n"
        "for every sp1, sp2, pack1, pack2, b1 and any t1, t2 with sp2=sp1, pack2=pack1:\n"
        "between sp_unpackage_bouquet(sp1, b1, pack1, t1) and previous sp_receive_package(sp2, pack2, t2):\n"
        "  for every sp3, pack3 and any b2, t3 with pack3=pack1:\n"
        "  sp_unpackage_bouquet(sp3, b2, pack3, t3) must happen at most 3 times\n"
    )
    rule_15_header = "at_most_hundred_bouquets_unpackaged_per_package"
    rule_15_scope = RuleScope([
        MatchCheckpoints(['sp_unpackage_bouquet', 'sp_receive_package']),
        RenameArgs(
            [['sp_unpackage_bouquet', 'sp1', 'b1', 'pack1', 't1'], ['sp_receive_package', 'sp2', 'pack2', 't2']]),
        CrossAndGroupByArgs([['sp_unpackage_bouquet', 'sp1', 'b1', 'pack1'], ['sp_receive_package', 'sp2', 'pack2']]),
        ImposeIteratorCondition("sp2", "=", "sp1", using_literal=False),
        ImposeIteratorCondition("pack2", "=", "pack1", using_literal=False),
        ScopeBetween("sp_unpackage_bouquet", "sp_receive_package", using_next=False, using_beyond=False)
    ])
    rule_15_fact = RuleFact([
        MatchCheckpoints(['sp_unpackage_bouquet']),
        RenameArgs([['sp_unpackage_bouquet', 'sp3', 'b2', 'pack3', 't3']]),
        CrossAndGroupByArgs([['sp_unpackage_bouquet', 'sp3', 'pack3']]),
        ImposeIteratorCondition("pack3", "=", "#pack1", using_literal=True),
        CompareResultsQuantity("<=", 3),
        ReduceResult(and_results=True)
    ])
    rule_15 = JARLRule(rule_15_statement, rule_15_header, rule_15_fact, rule_15_scope, passed_by_default=True)
    rule_15.set_dynamic_scope_arg("pack1", False)

    rule_16_statement = (
        "rule internet_orders_requested_before_served\n"
        "for every o1, o2, sp1, sp2 and any ra, ta with o1=o2, sp1=sp2:\n"
        "internet_make_order(o1, ra, ta, sp1) must precede sp_serve_order(sp2, o2)\n"
    )
    rule_16_header = "internet_orders_requested_before_served"
    rule_16_fact = RuleFact([
        MatchCheckpoints(['internet_make_order', 'sp_serve_order']),
        RenameArgs([['internet_make_order', 'o1', 'ra', 'ta', 'sp1'], ['sp_serve_order', 'sp2', 'o2']]),
        CrossAndGroupByArgs([['internet_make_order', 'o1', 'sp1'], ['sp_serve_order', 'sp2', 'o2']]),
        ImposeIteratorCondition("o1", "=", "o2", using_literal=False),
        ImposeIteratorCondition("sp1", "=", "sp2", using_literal=False),
        CompareResultsPrecedence("internet_make_order", "sp_serve_order"),
        ReduceResult(and_results=True)
    ])
    rule_16 = JARLRule(rule_16_statement, rule_16_header, rule_16_fact, passed_by_default=True)

    rule_17_statement = (
        "rule customer_orders_requested_before_served\n"
        "for every o1, o2, sp1, sp2 and any ra, ta with o1=o2, sp1=sp2:\n"
        "customer_make_order(o1, ra, ta, sp1) must precede sp_serve_order(sp2, o2)\n"
    )
    rule_17_header = "customer_orders_requested_before_served"
    rule_17_fact = RuleFact([
        MatchCheckpoints(['customer_make_order', 'sp_serve_order']),
        RenameArgs([['customer_make_order', 'o1', 'ra', 'ta', 'sp1'], ['sp_serve_order', 'sp2', 'o2']]),
        CrossAndGroupByArgs([['customer_make_order', 'o1', 'sp1'], ['sp_serve_order', 'sp2', 'o2']]),
        ImposeIteratorCondition("o1", "=", "o2", using_literal=False),
        ImposeIteratorCondition("sp1", "=", "sp2", using_literal=False),
        CompareResultsPrecedence("customer_make_order", "sp_serve_order"),
        ReduceResult(and_results=True)
    ])
    rule_17 = JARLRule(rule_17_statement, rule_17_header, rule_17_fact, passed_by_default=True)

    rule_18_statement = (
        "rule bouquets_only_prepared_once\n"
        "for every b, t and any sp, o:\n"
        "sp_prepare_bouquet(sp, b, o, t) must happen 1 times\n"
    )
    rule_18_header = "bouquets_only_prepared_once"
    rule_18_fact = RuleFact([
        MatchCheckpoints(['sp_prepare_bouquet']),
        RenameArgs([['sp_prepare_bouquet', 'sp', 'b', 'o', 't']]),
        CrossAndGroupByArgs([['sp_prepare_bouquet', 'b', 't']]),
        CompareResultsQuantity("=", 1),
        ReduceResult(and_results=True)
    ])
    rule_18 = JARLRule(rule_18_statement, rule_18_header, rule_18_fact, passed_by_default=False)

    rule_19_statement = (
        "rule prepared_bouquets_were_unpackaged\n"
        "for every sp1, b1, t1 and any o:\n"
        "before sp_prepare_bouquet(sp1, b1, o, t1):\n"
        "  for every sp2, b2, t2 and any pack with sp2=sp1, b2=b1, t2=t1:\n"
        "  sp_unpackage_bouquet(sp2, b2, pack, t2) must happen 1 times\n"
    )
    rule_19_header = "prepared_bouquets_were_unpackaged"
    rule_19_scope = RuleScope([
        MatchCheckpoints(['sp_prepare_bouquet']),
        RenameArgs([['sp_prepare_bouquet', 'sp1', 'b1', 'o', 't1']]),
        CrossAndGroupByArgs([['sp_prepare_bouquet', 'sp1', 'b1', 't1']]),
        ScopeBefore("sp_prepare_bouquet")
    ])
    rule_19_fact = RuleFact([
        MatchCheckpoints(['sp_unpackage_bouquet']),
        RenameArgs([['sp_unpackage_bouquet', 'sp2', 'b2', 'pack', 't2']]),
        CrossAndGroupByArgs([['sp_unpackage_bouquet', 'sp2', 'b2', 't2']]),
        ImposeIteratorCondition("sp2", "=", "#sp1", using_literal=True),
        ImposeIteratorCondition("b2", "=", "#b1", using_literal=True),
        ImposeIteratorCondition("t2", "=", "#t1", using_literal=True),
        CompareResultsQuantity("=", 1),
        ReduceResult(and_results=True)
    ])
    rule_19 = JARLRule(rule_19_statement, rule_19_header, rule_19_fact, rule_19_scope, passed_by_default=False)
    rule_19.set_dynamic_scope_arg("b1", False)
    rule_19.set_dynamic_scope_arg("t1", False)
    rule_19.set_dynamic_scope_arg("sp1", False)

    rule_20_statement = (
        "rule orders_have_bouquets\n"
        "for every sp1, o1:\n"
        "before sp_serve_order(sp1, o1):\n"
        "  for every sp2, o2 and any b, t with sp2=sp1, o2=o1:\n"
        "  sp_prepare_bouquet(sp2, b, o2, t) must happen"
    )
    rule_20_header = "orders_have_bouquets"
    rule_20_scope = RuleScope([
        MatchCheckpoints(['sp_serve_order']),
        RenameArgs([['sp_serve_order', 'sp1', 'o1']]),
        CrossAndGroupByArgs([['sp_serve_order', 'sp1', 'o1']]),
        ScopeBefore("sp_serve_order")
    ])
    rule_20_fact = RuleFact([
        MatchCheckpoints(['sp_prepare_bouquet']),
        RenameArgs([['sp_prepare_bouquet', 'sp2', 'b', 'o2', 't']]),
        CrossAndGroupByArgs([['sp_prepare_bouquet', 'sp2', 'o2']]),
        ImposeIteratorCondition("sp2", "=", "#sp1", using_literal=True),
        ImposeIteratorCondition("o2", "=", "#o1", using_literal=True),
        CompareResultsQuantity(">=", 1),
        ReduceResult(and_results=True)
    ])
    rule_20 = JARLRule(rule_20_statement, rule_20_header, rule_20_fact, rule_20_scope, passed_by_default=False)
    rule_20.set_dynamic_scope_arg("o1", False)
    rule_20.set_dynamic_scope_arg("sp1", False)

    def check_one_rule(self, rule):
        rc = RuleChecker([ rule ], self.log_file, self.checkpoint_file)
        rule = rc.check_all_rules()[0]
        self.assertTrue(rule.has_passed())

    def test_bouqets_produced_before_boxed(self):
        self.check_one_rule(self.rule_1)

    def test_ten_bouquets_in_sent_box(self):
        self.check_one_rule(self.rule_2)

    def test_box_at_most_ten_bouqets(self):
        self.check_one_rule(self.rule_3)

    def test_box_sent_before_received(self):
        self.check_one_rule(self.rule_4)

    def test_receive_box_before_unbox_bouquet(self):
        self.check_one_rule(self.rule_5)

    def test_unbox_at_most_ten_bouquets_per_box(self):
        self.check_one_rule(self.rule_6)

    def test_box_bouquet_happens_once(self):
        self.check_one_rule(self.rule_7)

    def test_unbox_bouquet_happens_once(self):
        self.check_one_rule(self.rule_8)

    def test_hunded_bouquets_per_package_sent(self):
        self.check_one_rule(self.rule_9)

    def test_package_bouquet_happens_once(self):
        self.check_one_rule(self.rule_10)

    def test_only_one_type_per_package(self):
        self.check_one_rule(self.rule_11)

    def test_at_most_package_hundred_bouquets_in_package(self):
        self.check_one_rule(self.rule_12)

    def test_package_sent_before_received(self):
        self.check_one_rule(self.rule_13)

    def test_package_bouquet_before_unpackage(self):
        self.check_one_rule(self.rule_14)

    def test_at_most_hundred_buckets_unpackaged_per_package(self):
        self.check_one_rule(self.rule_15)

    def test_internet_order_requested_before_served(self):
        self.check_one_rule(self.rule_16)

    def test_customer_order_requested_before_served(self):
        self.check_one_rule(self.rule_17)

    def test_bouquet_prepared_only_once(self):
        self.check_one_rule(self.rule_18)

    def test_unpackage_bouquet_before_prepare(self):
        self.check_one_rule(self.rule_19)

    def test_orders_have_bouquets(self):
        self.check_one_rule(self.rule_20)

    def test_all_rules(self):
        all_rules = [
            self.rule_1,
            self.rule_2,
            self.rule_3,
            self.rule_4,
            self.rule_5,
            self.rule_6,
            self.rule_7,
            self.rule_8,
            self.rule_9,
            self.rule_10,
            self.rule_11,
            self.rule_12,
            self.rule_13,
            self.rule_14,
            self.rule_15,
            self.rule_16,
            self.rule_17,
            self.rule_18,
            self.rule_19,
            self.rule_20,
        ]
        rc = RuleChecker(all_rules, self.log_file, self.checkpoint_file)
        all_rules = rc.check_all_rules()

        all_passed = True
        for rule in all_rules:
            if rule.has_failed(): all_passed = False

        #VerifierPrinter(True).print_verifier_summary(all_rules)
        self.assertTrue(all_passed)


if __name__ == '__main__':
    unittest.main()
