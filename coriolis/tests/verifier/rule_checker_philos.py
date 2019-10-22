import unittest

from verifier.rule_checker import *


class TestPhilos(unittest.TestCase):
    log_file = "./resources/philos_1.log"
    checkpoint_file = "./resources/philos.chk"

    rule_1_statement = (
        "rule every_philo_eats_four_times\n"
        "for every p and any r:\n"
        "eat(p, r) must happen 4 times\n"
    )
    rule_1_header = "every_philo_eats_four_times"
    rule_1_fact = RuleFact([
        MatchCheckpoints(['eat']),
        RenameArgs([['eat', 'p', 'r']]),
        CrossAndGroupByArgs([['eat', 'p']]),
        CompareResultsQuantity("=", 4),
        ReduceResult(and_results=True)
    ])
    rule_1 = JARLRule(rule_1_statement, rule_1_header, rule_1_fact, passed_by_default=False)

    rule_2_statement = (
        "rule every_philo_thinks_four_times\n"
        "for every p and any r:\n"
        "think(p, r) must happen 4 times\n"
    )
    rule_2_header = "every_philo_thinks_four_times"
    rule_2_fact = RuleFact([
        MatchCheckpoints(['think']),
        RenameArgs([['think', 'p', 'r']]),
        CrossAndGroupByArgs([['think', 'p']]),
        CompareResultsQuantity("=", 4),
        ReduceResult(and_results=True)
    ])
    rule_2 = JARLRule(rule_2_statement, rule_2_header, rule_2_fact, passed_by_default=False)

    rule_3_statement = (
        "rule philo_needs_two_forks_to_eat\n"
        "for every p1, r1:\n"
        "before eat(p1, r1):\n"
        "  for every p2, r2 and any f with p2=p1, r2=r1:\n"
        "  acquire_fork(p2, f, r2) must happen 2 times\n"
    )
    rule_3_header = "philo_needs_two_forks_to_eat"
    rule_3_fact = RuleFact([
        MatchCheckpoints(['acquire_fork']),
        RenameArgs([['acquire_fork', 'p2', 'f', 'r2']]),
        CrossAndGroupByArgs([['acquire_fork', 'p2', 'r2']]),
        ImposeIteratorCondition("p2", "=", "#p1", using_literal=True),
        ImposeIteratorCondition("r2", "=", "#r1", using_literal=True),
        CompareResultsQuantity("=", 2),
        ReduceResult(and_results=True)
    ])
    rule_3_scope = RuleScope([
        MatchCheckpoints(['eat']),
        RenameArgs([['eat', 'p1', 'r1']]),
        CrossAndGroupByArgs([['eat', 'p1', 'r1']]),
        ScopeBefore("eat")
    ])
    rule_3 = JARLRule(rule_3_statement, rule_3_header, rule_3_fact, rule_3_scope, passed_by_default=False)
    rule_3.set_dynamic_scope_arg("p1", False)
    rule_3.set_dynamic_scope_arg("r1", False)

    rule_4_statement = (
        "rule philo_releases_forks_before_thinking\n"
        "for every p1, p2 and any r1, r2 with p1=p2:\n"
        "between eat(p1, r1) and next think(p2, r2):\n"
        "  for every p3 and any f, r3 with p3=p1:\n"
        "  release_fork(p3, f, r3) must happen 2 times\n"
    )
    rule_4_header = "philo_releases_forks_before_thinking"
    rule_4_fact = RuleFact([
        MatchCheckpoints(['release_fork']),
        RenameArgs([['release_fork', 'p3', 'f', 'r3']]),
        CrossAndGroupByArgs([['release_fork', 'p3']]),
        ImposeIteratorCondition("p3", "=", "#p1", using_literal=True),
        CompareResultsQuantity("=", 2),
        ReduceResult(and_results=True)
    ])
    rule_4_scope = RuleScope([
        MatchCheckpoints(['eat', 'think']),
        RenameArgs([['eat', 'p1', 'r1'], ['think', 'p2', 'r2']]),
        CrossAndGroupByArgs([['eat', 'p1'], ['think', 'p2']]),
        ImposeIteratorCondition("p1", "=", "p2", using_literal=False),
        ScopeBetween("eat", "think", using_next=True, using_beyond=False)
    ])
    rule_4 = JARLRule(rule_4_statement, rule_4_header, rule_4_fact, rule_4_scope, passed_by_default=False)
    rule_4.set_dynamic_scope_arg("p1", True)

    rule_5_statement = (
        "rule all_acquired_forks_are_released_once\n"
        "for every p1, f1, r1:\n"
        "after acquire_fork(p1, f1, r1):\n"
        "  for every p2, f2, r2 with p2=p1, f2=f1, r2=r1:\n"
        "  release_fork(p2, f2, r2) must happen 1 times\n"
    )
    rule_5_header = "all_acquired_forks_are_released_once"
    rule_5_fact = RuleFact([
        MatchCheckpoints(['release_fork']),
        RenameArgs([['release_fork', 'p2', 'f2', 'r2']]),
        CrossAndGroupByArgs([['release_fork', 'p2', 'f2', 'r2']]),
        ImposeIteratorCondition("p2", "=", "#p1", using_literal=True),
        ImposeIteratorCondition("f2", "=", "#f1", using_literal=True),
        ImposeIteratorCondition("r2", "=", "#r1", using_literal=True),
        CompareResultsQuantity("=", 1),
        ReduceResult(and_results=True)
    ])
    rule_5_scope = RuleScope([
        MatchCheckpoints(['acquire_fork']),
        RenameArgs([['acquire_fork', 'p1', 'f1', 'r1']]),
        CrossAndGroupByArgs([['acquire_fork', 'p1', 'f1', 'r1']]),
        ScopeAfter("acquire_fork")
    ])
    rule_5 = JARLRule(rule_5_statement, rule_5_header, rule_5_fact, rule_5_scope, passed_by_default=False)
    rule_5.set_dynamic_scope_arg("p1", True)
    rule_5.set_dynamic_scope_arg("f1", True)
    rule_5.set_dynamic_scope_arg("r1", True)

    rule_6_statement = (
        "rule fork_held_by_one_philo_at_a_time\n"
        "for every p1, f1, r1, p2, f2, r2 with p2=p1, f2=f1, r2=r1:\n"
        "between acquire_fork(p1, f1, r1) and next release_fork(p2, f2, r2):\n"
        "  for any p3, f3, r3 with f3=f1, p3!=p1:\n"
        "  acquire_fork(p3, f3, r3) must not happen\n"
    )
    rule_6_header = "fork_held_by_one_philo_at_a_time"
    rule_6_fact = RuleFact([
        MatchCheckpoints(['acquire_fork']),
        RenameArgs([['acquire_fork', 'p3', 'f3', 'r3']]),
        CrossAndGroupByArgs([['acquire_fork']]),
        ImposeWildcardCondition("f3", "=", "#f1", using_literal=True),
        ImposeWildcardCondition("p3", "!=", "#p1", using_literal=True),
        CompareResultsQuantity("=", 0),
        ReduceResult(and_results=True)
    ])
    rule_6_scope = RuleScope([
        MatchCheckpoints(['acquire_fork', 'release_fork']),
        RenameArgs([['acquire_fork', 'p1', 'f1', 'r1'], ['release_fork', 'p2', 'f2', 'r2']]),
        CrossAndGroupByArgs([['acquire_fork', 'p1', 'f1', 'r1'], ['release_fork', 'p2', 'f2', 'r2']]),
        ImposeIteratorCondition("p2", "=", "p1", using_literal=False),
        ImposeIteratorCondition("f2", "=", "f1", using_literal=False),
        ImposeIteratorCondition("r2", "=", "r1", using_literal=False),
        ScopeBetween("acquire_fork", "release_fork", using_next=True, using_beyond=False)
    ])
    rule_6 = JARLRule(rule_6_statement, rule_6_header, rule_6_fact, rule_6_scope, passed_by_default=True)
    rule_6.set_dynamic_scope_arg("p1", True)
    rule_6.set_dynamic_scope_arg("f1", True)

    rule_7_statement = (
        "rule philo_acquires_no_forks_while_thinking\n"
        "for every p1, p2 and any r1, r2 with p1=p2:\n"
        "between eat(p1, r1) and next think(p2, r2):\n"
        "  for every p3 and any f, r3 with p3=p1:\n"
        "  acquire_fork(p3, f, r3) must not happen\n"
    )
    rule_7_header = "philo_acquires_no_forks_while_thinking"
    rule_7_fact = RuleFact([
        MatchCheckpoints(['acquire_fork']),
        RenameArgs([['acquire_fork', 'p3', 'f', 'r3']]),
        CrossAndGroupByArgs([['acquire_fork', 'p3']]),
        ImposeIteratorCondition("p3", "=", "#p1", using_literal=True),
        CompareResultsQuantity("=", 0),
        ReduceResult(and_results=True)
    ])
    rule_7_scope = RuleScope([
        MatchCheckpoints(['eat', 'think']),
        RenameArgs([['eat', 'p1', 'r1'], ['think', 'p2', 'r2']]),
        CrossAndGroupByArgs([['eat', 'p1'], ['think', 'p2']]),
        ImposeIteratorCondition("p1", "=", "p2", using_literal=False),
        ScopeBetween("eat", "think", using_next=True, using_beyond=False)
    ])
    rule_7 = JARLRule(rule_7_statement, rule_7_header, rule_7_fact, rule_7_scope, passed_by_default=True)
    rule_7.set_dynamic_scope_arg("p1", True)

    rule_8_statement = (
        "rule only_two_philos_use_same_fork\n"
        "for every f, r and any p:\n"
        "acquire_fork(p, f, r) must happen 2 times\n"
    )
    rule_8_header = "only_two_philos_use_same_fork"
    rule_8_fact = RuleFact([
        MatchCheckpoints(['acquire_fork']),
        RenameArgs([['acquire_fork', 'p', 'f', 'r']]),
        CrossAndGroupByArgs([['acquire_fork', 'f', 'r']]),
        CompareResultsQuantity("=", 2),
        ReduceResult(and_results=True)
    ])
    rule_8 = JARLRule(rule_8_statement, rule_8_header, rule_8_fact, passed_by_default=False)

    rule_9_statement = (
        "rule philo_dont_release_fork_without_eating\n"
        "for every p1, f1, r1, p2, f2, r2 with p2=p1, f2=f1, r2=r1:\n"
        "between acquire_fork(p1, f1, r1) and next release_fork(p2, f2, r2):\n"
        "  for every p3 and any r3 with p3=p1:\n"
        "  eat(p3, r3) must happen 1 times\n"
    )
    rule_9_header = "philo_dont_release_fork_without_eating"
    rule_9_fact = RuleFact([
        MatchCheckpoints(['eat']),
        RenameArgs([['eat', 'p3', 'r3']]),
        CrossAndGroupByArgs([['eat', 'p3']]),
        ImposeIteratorCondition("p3", "=", "#p1", using_literal=True),
        CompareResultsQuantity("=", 1),
        ReduceResult(and_results=True)
    ])
    rule_9_scope = RuleScope([
        MatchCheckpoints(['acquire_fork', 'release_fork']),
        RenameArgs([['acquire_fork', 'p1', 'f1', 'r1'], ['release_fork', 'p2', 'f2', 'r2']]),
        CrossAndGroupByArgs([['acquire_fork', 'p1', 'f1', 'r1'], ['release_fork', 'p2', 'f2', 'r2']]),
        ImposeIteratorCondition("p2", "=", "p1", using_literal=False),
        ImposeIteratorCondition("f2", "=", "f1", using_literal=False),
        ImposeIteratorCondition("r2", "=", "r1", using_literal=False),
        ScopeBetween("acquire_fork", "release_fork", using_next=True, using_beyond=False)
    ])
    rule_9 = JARLRule(rule_9_statement, rule_9_header, rule_9_fact, rule_9_scope, passed_by_default=False)
    rule_9.set_dynamic_scope_arg("p1", True)

    rule_10_statement = (
        "rule philo_dont_acquire_fork_without_thiking\n"
        "for every p1, f1, r1, p2, f2, r2 with p2=p1, f2=f1, r2=r1:\n"
        "between release_fork(p1, f1, r1) and next acquire_fork(p2, f2, r2):\n"
        "  for every p3 and any r3 with p3=p1:\n"
        "  think(p3, r3) must happen 1 times\n"
    )
    rule_10_header = "philo_dont_acquire_fork_without_thiking"
    rule_10_fact = RuleFact([
        MatchCheckpoints(['think']),
        RenameArgs([['think', 'p3', 'r3']]),
        CrossAndGroupByArgs([['think', 'p3']]),
        ImposeIteratorCondition("p3", "=", "#p1", using_literal=True),
        CompareResultsQuantity("=", 1),
        ReduceResult(and_results=True)
    ])
    rule_10_scope = RuleScope([
        MatchCheckpoints(['release_fork', 'acquire_fork']),
        RenameArgs([['release_fork', 'p1', 'f1', 'r1'], ['acquire_fork', 'p2', 'f2', 'r2']]),
        CrossAndGroupByArgs([['release_fork', 'p1', 'f1', 'r1'], ['acquire_fork', 'p2', 'f2', 'r2']]),
        ImposeIteratorCondition("p2", "=", "p1", using_literal=False),
        ImposeIteratorCondition("f2", "=", "f1", using_literal=False),
        ImposeIteratorCondition("r2", "=", "r1", using_literal=False),
        ScopeBetween("release_fork", "acquire_fork", using_next=True, using_beyond=False)
    ])
    rule_10 = JARLRule(rule_10_statement, rule_10_header, rule_10_fact, rule_10_scope, passed_by_default=False)
    rule_10.set_dynamic_scope_arg("p1", True)

    def check_one_rule(self, rule):
        rc = RuleChecker([ rule ], self.log_file, self.checkpoint_file)
        rule = rc.check_all_rules()[0]
        self.assertTrue(rule.has_passed())

    def test_philo_eats_four_times(self):
        self.check_one_rule(self.rule_1)

    def test_philo_thinks_four_times(self):
        self.check_one_rule(self.rule_2)

    def test_two_forks_to_eat(self):
        self.check_one_rule(self.rule_3)

    def test_forks_released_before_think(self):
        self.check_one_rule(self.rule_4)

    def test_acquired_forks_get_released(self):
        self.check_one_rule(self.rule_5)

    def test_fork_held_by_only_one_philo(self):
        self.check_one_rule(self.rule_6)

    def test_no_acquire_fork_if_thinking(self):
        self.check_one_rule(self.rule_7)

    def test_fork_shared_by_two_philos(self):
        self.check_one_rule(self.rule_8)

    def test_no_release_fork_without_eating(self):
        self.check_one_rule(self.rule_9)

    def test_no_acquire_fork_without_thinking(self):
        self.check_one_rule(self.rule_10)

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
