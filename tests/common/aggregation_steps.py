import unittest

from common.aggregation_steps import *
from verifier.mongo_client import MongoClient


class TestAggregationSteps(unittest.TestCase):
    mongo_client = MongoClient()

    def insert_documents(self, documents):
        for d in documents:
            self.mongo_client.insert_one(d)

    def pop_id_fields(self, document):
        document.pop("_id", None)
        if "r1" in document: document["r1"].pop("_id", None)
        if "r2" in document: document["r2"].pop("_id", None)
        if "results" in document:
            for x in document["results"]:
                x.pop("_id", None)

    def check_aggregation_step(self, step, input, expected_output, remove_id=True, remove_info=False):
        self.maxDiff = None
        self.insert_documents(input)
        output = self.mongo_client.aggregate(step.evaluate())
        output = [x for x in output]
        for x in output:
            if remove_id: self.pop_id_fields(x)
            if remove_info: x.pop("info", None)
        self.mongo_client.drop()
        self.assertCountEqual(output, expected_output)

    def test_match_two_checkpoints(self):
        step = MatchCheckpoints( ["f", "h"] )
        input = [
            {'log_line': 1, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'f'},
            {'log_line': 2, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'g'},
            {'log_line': 3, 'arg_1': 2, 'arg_2': 2, 'checkpoint': 'f'},
            {'log_line': 4, 'arg_1': 2, 'arg_2': 3, 'checkpoint': 'h'}
        ]
        expected_output = [
            {'log_line': 1, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'f'},
            {'log_line': 3, 'arg_1': 2, 'arg_2': 2, 'checkpoint': 'f'},
            {'log_line': 4, 'arg_1': 2, 'arg_2': 3, 'checkpoint': 'h'}
        ]
        self.check_aggregation_step(step, input, expected_output)

    def test_match_one_checkpoint(self):
        step = MatchCheckpoints( ["h"] )
        input = [
            {'log_line': 1, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'f'},
            {'log_line': 2, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'g'},
            {'log_line': 3, 'arg_1': 2, 'arg_2': 2, 'checkpoint': 'f'},
            {'log_line': 4, 'arg_1': 2, 'arg_2': 3, 'checkpoint': 'h'}
        ]
        expected_output = [
            {'log_line': 4, 'arg_1': 2, 'arg_2': 3, 'checkpoint': 'h'}
        ]
        self.check_aggregation_step(step, input, expected_output)

    def test_rename_one_arg(self):
        step = RenameArgs([ ["f", "x"] ])
        input = [
            {'log_line': 1, 'arg_1': 8, 'checkpoint': 'f'}
        ]
        expected_output = [
            {'log_line': 1, 'checkpoint': 'f', 'arg_x': 8}
        ]
        self.check_aggregation_step(step, input, expected_output)

    def test_rename_same_arg_twice(self):
        step = RenameArgs([ ["f", "x"], ["f", "y"] ])
        input = [
            {'log_line': 1, 'arg_1': 8, 'checkpoint': 'f'},
            {'log_line': 2, 'arg_1': 6, 'checkpoint': 'f'}
        ]
        expected_output = [
            {'log_line': 1, 'checkpoint': 'f', 'arg_x': 8, 'arg_y': 8},
            {'log_line': 2, 'checkpoint': 'f', 'arg_x': 6, 'arg_y': 6}
        ]
        self.check_aggregation_step(step, input, expected_output)

    def test_rename_args(self):
        step = RenameArgs([ ["f", "i", "j"], ["g", "a1", "a2"] ])
        input = [
            {'log_line': 1, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'f'},
            {'log_line': 2, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'g'},
            {'log_line': 3, 'arg_1': 2, 'arg_2': 2, 'checkpoint': 'f'}
        ]
        expected_output = [
            {'log_line': 1, 'checkpoint': 'f', 'arg_i': 1, 'arg_j': 1},
            {'log_line': 2, 'checkpoint': 'g', 'arg_a1': 1, 'arg_a2': 1},
            {'log_line': 3, 'checkpoint': 'f', 'arg_i': 2, 'arg_j': 2}
        ]
        self.check_aggregation_step(step, input, expected_output)

    def test_cross_join_checkpoints(self):
        step = CrossJoinCheckpoints(["f", "g"])
        input = [
            {'log_line': 1, 'checkpoint': 'f', 'arg_p': 1},
            {'log_line': 2, 'checkpoint': 'g', 'arg_c': 1, 'arg_i': 1},
            {'log_line': 3, 'checkpoint': 'f', 'arg_p': 2},
            {'log_line': 4, 'checkpoint': 'f', 'arg_p': 2},
            {'log_line': 5, 'checkpoint': 'g', 'arg_c': 1, 'arg_i': 2}
        ]
        expected_output = [
            {'r1': {'log_line': 1, 'checkpoint': 'f1', 'arg_p': 1}, 'r2': {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i': 1}},
            {'r1': {'log_line': 1, 'checkpoint': 'f1', 'arg_p': 1}, 'r2': {'log_line': 5, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i': 2}},
            {'r1': {'log_line': 3, 'checkpoint': 'f1', 'arg_p': 2}, 'r2': {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i': 1}},
            {'r1': {'log_line': 3, 'checkpoint': 'f1', 'arg_p': 2}, 'r2': {'log_line': 5, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i': 2}},
            {'r1': {'log_line': 4, 'checkpoint': 'f1', 'arg_p': 2}, 'r2': {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i': 1}},
            {'r1': {'log_line': 4, 'checkpoint': 'f1', 'arg_p': 2}, 'r2': {'log_line': 5, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i': 2}}
        ]
        self.check_aggregation_step(step, input, expected_output)

    def test_cross_group_by_args(self):
        step = CrossAndGroupByArgs([ ["f", "i1"], ["g", "i2"] ])
        input= [
            {'log_line': 1, 'checkpoint': 'f', 'arg_i1': 1},
            {'log_line': 2, 'checkpoint': 'g', 'arg_c': 1, 'arg_i2': 1},
            {'log_line': 3, 'checkpoint': 'f', 'arg_i1': 2},
            {'log_line': 4, 'checkpoint': 'f', 'arg_i1': 3},
            {'log_line': 6, 'checkpoint': 'g', 'arg_c': 1, 'arg_i2': 2}
        ]
        expected_output = [
            {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 1}]},
            {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 6, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 2}]},
            {'results': [{'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 1}, {'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}]},
            {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}, {'log_line': 6, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 2}]},
            {'results': [{'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 1}, {'log_line': 4, 'checkpoint': 'f1', 'arg_i1': 3}]},
            {'results': [{'log_line': 4, 'checkpoint': 'f1', 'arg_i1': 3}, {'log_line': 6, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 2}]}
        ]
        self.check_aggregation_step(step, input, expected_output)

    def test_cross_group_by_null(self):
        step = CrossAndGroupByArgs([ ["f", "null"] ])
        input= [
            {'log_line': 1, 'checkpoint': 'f', 'arg_x': 1},
            {'log_line': 2, 'checkpoint': 'f', 'arg_x': 3},
            {'log_line': 3, 'checkpoint': 'f', 'arg_x': 5}
        ]
        expected_output = [
            {'results': [
                {'log_line': 1, 'checkpoint': 'f1', 'arg_x': 1},
                {'log_line': 2, 'checkpoint': 'f1', 'arg_x': 3},
                {'log_line': 3, 'checkpoint': 'f1', 'arg_x': 5}
            ]}
        ]
        self.check_aggregation_step(step, input, expected_output)

    def test_iterators_lte_condition(self):
        step = ImposeIteratorCondition("i1", "<=", "i2")
        input = [
            {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 1}], '_id': {'i2': 1, 'i1': 1}},
            {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 6, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 2}], '_id': {'i2': 2, 'i1': 1}},
            {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}, {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 1}], '_id': {'i2': 1, 'i1': 2}},
            {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}, {'log_line': 6, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 2}], '_id': {'i2': 2, 'i1': 2}},
            {'results': [{'log_line': 4, 'checkpoint': 'f1', 'arg_i1': 3}, {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 1}], '_id': {'i2': 1, 'i1': 3}},
            {'results': [{'log_line': 4, 'checkpoint': 'f1', 'arg_i1': 3}, {'log_line': 6, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 2}], '_id': {'i2': 2, 'i1': 3}}
        ]
        expected_output = [
          {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 1}]},
          {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 6, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 2}]},
          {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}, {'log_line': 6, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 2}]}
        ]
        self.check_aggregation_step(step, input, expected_output)

    def test_iterators_eq_condition(self):
        step = ImposeIteratorCondition("i1", "=", "i2")
        input = [
            {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 1}], '_id': {'i2': 1, 'i1': 1}},
            {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 6, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 2}], '_id': {'i2': 2, 'i1': 1}},
            {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}, {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 1}], '_id': {'i2': 1, 'i1': 2}},
            {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}, {'log_line': 6, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 2}], '_id': {'i2': 2, 'i1': 2}},
            {'results': [{'log_line': 4, 'checkpoint': 'f1', 'arg_i1': 3}, {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 1}], '_id': {'i2': 1, 'i1': 3}},
            {'results': [{'log_line': 4, 'checkpoint': 'f1', 'arg_i1': 3}, {'log_line': 6, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 2}], '_id': {'i2': 2, 'i1': 3}}
        ]
        expected_output = [
          {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 1}]},
          {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}, {'log_line': 6, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 2}]}
        ]
        self.check_aggregation_step(step, input, expected_output)

    def test_wildcard_gte_condition(self):
        step = ImposeWildcardCondition("w1", ">=", "w2")
        input = [
            {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_w1': 1, 'arg_w2': 0}]},
            {'results': [{'log_line': 2, 'checkpoint': 'f1', 'arg_w1': 1, 'arg_w2': 2}]},
            {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_w1': 2, 'arg_w2': 4}]},
            {'results': [{'log_line': 4, 'checkpoint': 'f1', 'arg_w1': 2, 'arg_w2': 4}]},
            {'results': [{'log_line': 5, 'checkpoint': 'f1', 'arg_w1': 3, 'arg_w2': 2}]},
            {'results': [{'log_line': 6, 'checkpoint': 'f1', 'arg_w1': 3, 'arg_w2': 0}]}
        ]
        expected_output = [
            {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_w1': 1, 'arg_w2': 0}]},
            {'results': []},
            {'results': []},
            {'results': []},
            {'results': [{'log_line': 5, 'checkpoint': 'f1', 'arg_w1': 3, 'arg_w2': 2}]},
            {'results': [{'log_line': 6, 'checkpoint': 'f1', 'arg_w1': 3, 'arg_w2': 0}]}
        ]
        self.check_aggregation_step(step, input, expected_output)

    def test_wildcard_ne_condition(self):
        step = ImposeWildcardCondition("w1", "!=", "w2")
        input = [
            {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_w1': 1, 'arg_w2': 1}]},
            {'results': [{'log_line': 2, 'checkpoint': 'f1', 'arg_w1': 1, 'arg_w2': 2}]},
            {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_w1': 2, 'arg_w2': 4}]},
            {'results': [{'log_line': 4, 'checkpoint': 'f1', 'arg_w1': 4, 'arg_w2': 4}]},
            {'results': [{'log_line': 5, 'checkpoint': 'f1', 'arg_w1': 3, 'arg_w2': 2}]},
            {'results': [{'log_line': 6, 'checkpoint': 'f1', 'arg_w1': 3, 'arg_w2': 0}]}
        ]
        expected_output = [
            {'results': []},
            {'results': [{'log_line': 2, 'checkpoint': 'f1', 'arg_w1': 1, 'arg_w2': 2}]},
            {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_w1': 2, 'arg_w2': 4}]},
            {'results': []},
            {'results': [{'log_line': 5, 'checkpoint': 'f1', 'arg_w1': 3, 'arg_w2': 2}]},
            {'results': [{'log_line': 6, 'checkpoint': 'f1', 'arg_w1': 3, 'arg_w2': 0}]}
        ]
        self.check_aggregation_step(step, input, expected_output)

    def test_compare_results_precedence(self):
        step = CompareResultsPrecedence("f1", "g2")
        input = [
            {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}, {'log_line': 7, 'checkpoint': 'g2', 'arg_i2': 2}], '_id': {'i2': 2, 'i1': 2}},
            {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 2, 'checkpoint': 'g2', 'arg_i2': 1}], '_id': {'i2': 1, 'i1': 1}},
            {'results': [{'log_line': 5, 'checkpoint': 'f1', 'arg_i1': 3}, {'log_line': 4, 'checkpoint': 'g2', 'arg_i2': 3}], '_id': {'i2': 3, 'i1': 3}}
        ]
        expected_output = [
            {'result': True, '_id': {'i2': 2, 'i1': 2}},
            {'result': True, '_id': {'i2': 1, 'i1': 1}},
            {'result': False, '_id': {'i2': 3, 'i1': 3}}
        ]
        self.check_aggregation_step(step, input, expected_output, remove_id=False, remove_info=True)

    def test_compare_results_quantity(self):
        step = CompareResultsQuantity("=", 1)
        input = [
            {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_x': 1}], '_id': {'i': 1}},
            {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_x': 2}], '_id': {'i': 2}},
            {'results': [{'log_line': 7, 'checkpoint': 'f1', 'arg_x': 3}, {'log_line': 11, 'checkpoint': 'f1', 'arg_x': 4}], '_id': {'i': 3}}
        ]
        expected_output = [
            {'result': True, '_id': {'i': 1}},
            {'result': True, '_id': {'i': 2}},
            {'result': False, '_id': {'i': 3}}
        ]
        self.check_aggregation_step(step, input, expected_output, remove_id=False, remove_info=True)

    def test_reduce_failing_result(self):
        step = ReduceResult()
        input = [
            {'result': False, 'info': 'Info message 1\n'},
            {'result': True, 'info': 'Info message 2\n'},
            {'result': False, 'info': 'Info message 3\n'},
            {'result': True, 'info': 'Info message 4\n'}
        ]
        expected_output = [ {'_id': False, 'info': 'Info message 1\nInfo message 3\n'} ]
        self.check_aggregation_step(step, input, expected_output, remove_id=False)

    def test_reduce_passing_result(self):
        step = ReduceResult()
        input = [
            {'result': True, 'info': 'Info message 1\n'},
            {'result': True, 'info': 'Info message 2\n'},
            {'result': True, 'info': 'Info message 3\n'},
            {'result': True, 'info': 'Info message 4\n'}
        ]
        expected_output = [ {'_id': True, 'info': ''} ]
        self.check_aggregation_step(step, input, expected_output, remove_id=False)

    def test_filter_log_lines(self):
        step = FilterByLogLines(2, 4)
        input = [
            {'log_line': 1, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'f'},
            {'log_line': 2, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'g'},
            {'log_line': 3, 'arg_1': 2, 'arg_2': 2, 'checkpoint': 'f'},
            {'log_line': 4, 'arg_1': 2, 'arg_2': 3, 'checkpoint': 'h'},
            {'log_line': 5, 'arg_1': 3, 'arg_2': 9, 'checkpoint': 'g'}
        ]
        expected_output = [
            {'log_line': 2, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'g'},
            {'log_line': 3, 'arg_1': 2, 'arg_2': 2, 'checkpoint': 'f'},
            {'log_line': 4, 'arg_1': 2, 'arg_2': 3, 'checkpoint': 'h'}
        ]
        self.check_aggregation_step(step, input, expected_output)

    def test_filter_log_lines_with_min(self):
        step = FilterByLogLines("MIN", 4)
        input = [
            {'log_line': 1, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'f'},
            {'log_line': 2, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'g'},
            {'log_line': 3, 'arg_1': 2, 'arg_2': 2, 'checkpoint': 'f'},
            {'log_line': 4, 'arg_1': 2, 'arg_2': 3, 'checkpoint': 'h'},
            {'log_line': 5, 'arg_1': 3, 'arg_2': 9, 'checkpoint': 'g'}
        ]
        expected_output = [
            {'log_line': 1, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'f'},
            {'log_line': 2, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'g'},
            {'log_line': 3, 'arg_1': 2, 'arg_2': 2, 'checkpoint': 'f'},
            {'log_line': 4, 'arg_1': 2, 'arg_2': 3, 'checkpoint': 'h'}
        ]
        self.check_aggregation_step(step, input, expected_output)

    def test_filter_log_lines_with_max(self):
        step = FilterByLogLines(2, "MAX")
        input = [
            {'log_line': 1, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'f'},
            {'log_line': 2, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'g'},
            {'log_line': 3, 'arg_1': 2, 'arg_2': 2, 'checkpoint': 'f'},
            {'log_line': 4, 'arg_1': 2, 'arg_2': 3, 'checkpoint': 'h'},
            {'log_line': 5, 'arg_1': 3, 'arg_2': 9, 'checkpoint': 'g'}
        ]
        expected_output = [
            {'log_line': 2, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'g'},
            {'log_line': 3, 'arg_1': 2, 'arg_2': 2, 'checkpoint': 'f'},
            {'log_line': 4, 'arg_1': 2, 'arg_2': 3, 'checkpoint': 'h'},
            {'log_line': 5, 'arg_1': 3, 'arg_2': 9, 'checkpoint': 'g'}
        ]
        self.check_aggregation_step(step, input, expected_output)

    def test_scope_between(self):
        step = ScopeBetween("f1", "g2")
        input = [
            {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 2, 'checkpoint': 'g2', 'arg_i2': 1}], '_id': {'i2': 1, 'i1': 1}},
            {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 6, 'checkpoint': 'g2', 'arg_i2': 2}], '_id': {'i2': 2, 'i1': 1}},
            {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}, {'log_line': 2, 'checkpoint': 'g2', 'arg_i2': 1}], '_id': {'i2': 1, 'i1': 2}},
            {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}, {'log_line': 6, 'checkpoint': 'g2', 'arg_i2': 2}], '_id': {'i2': 2, 'i1': 2}},
            {'results': [{'log_line': 4, 'checkpoint': 'f1', 'arg_i1': 3}, {'log_line': 2, 'checkpoint': 'g2', 'arg_i2': 1}], '_id': {'i2': 1, 'i1': 3}},
            {'results': [{'log_line': 4, 'checkpoint': 'f1', 'arg_i1': 3}, {'log_line': 6, 'checkpoint': 'g2', 'arg_i2': 2}], '_id': {'i2': 2, 'i1': 3}}
        ]
        expected_output = [
            {'c2': {'log_line': 2, 'checkpoint': 'g2', 'arg_i2': 1}, 'c1': {'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, '_id': {'i1': 1, 'i2': 1}},
            {'c2': {'log_line': 6, 'checkpoint': 'g2', 'arg_i2': 2}, 'c1': {'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, '_id': {'i1': 1, 'i2': 2}},
            {'c2': {'log_line': 6, 'checkpoint': 'g2', 'arg_i2': 2}, 'c1': {'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}, '_id': {'i1': 2, 'i2': 2}},
            {'c2': {'log_line': 6, 'checkpoint': 'g2', 'arg_i2': 2}, 'c1': {'log_line': 4, 'checkpoint': 'f1', 'arg_i1': 3}, '_id': {'i1': 3, 'i2': 2}}
        ]
        self.check_aggregation_step(step, input, expected_output, remove_id=False)

    def test_scope_after(self):
        step = ScopeAfter("f1")
        input = [
            {'_id': {'null': None}, 'results': [
                {'log_line': 2, 'checkpoint': 'f1', 'arg_x': 1},
                {'log_line': 6, 'checkpoint': 'f1', 'arg_x': 1},
                {'log_line': 8, 'checkpoint': 'f1', 'arg_x': 2},
                {'log_line': 9, 'checkpoint': 'f1', 'arg_x': 3},
                {'log_line': 10, 'checkpoint': 'f1', 'arg_x': 3}
            ]}
        ]
        expected_output = [
            {'_id': {'null': None}, 'c1': {'log_line': 2, 'checkpoint': 'f1', 'arg_x': 1}, 'c2': {'log_line': 'MAX'}},
            {'_id': {'null': None}, 'c1': {'log_line': 6, 'checkpoint': 'f1', 'arg_x': 1}, 'c2': {'log_line': 'MAX'}},
            {'_id': {'null': None}, 'c1': {'log_line': 8, 'checkpoint': 'f1', 'arg_x': 2}, 'c2': {'log_line': 'MAX'}},
            {'_id': {'null': None}, 'c1': {'log_line': 9, 'checkpoint': 'f1', 'arg_x': 3}, 'c2': {'log_line': 'MAX'}},
            {'_id': {'null': None}, 'c1': {'log_line': 10, 'checkpoint': 'f1', 'arg_x': 3}, 'c2': {'log_line': 'MAX'}}
        ]
        self.check_aggregation_step(step, input, expected_output, remove_id=False)

    def test_scope_before(self):
        step = ScopeBefore("f1")
        input = [
            {'_id': {'null': None}, 'results': [
                {'log_line': 2, 'checkpoint': 'f1', 'arg_x': 1},
                {'log_line': 6, 'checkpoint': 'f1', 'arg_x': 1},
                {'log_line': 8, 'checkpoint': 'f1', 'arg_x': 2},
                {'log_line': 9, 'checkpoint': 'f1', 'arg_x': 3},
                {'log_line': 10, 'checkpoint': 'f1', 'arg_x': 3}
            ]}
        ]
        expected_output = [
            {'_id': {'null': None}, 'c1': {'log_line': 'MIN'}, 'c2': {'log_line': 2, 'checkpoint': 'f1', 'arg_x': 1}},
            {'_id': {'null': None}, 'c1': {'log_line': 'MIN'}, 'c2': {'log_line': 6, 'checkpoint': 'f1', 'arg_x': 1}},
            {'_id': {'null': None}, 'c1': {'log_line': 'MIN'}, 'c2': {'log_line': 8, 'checkpoint': 'f1', 'arg_x': 2}},
            {'_id': {'null': None}, 'c1': {'log_line': 'MIN'}, 'c2': {'log_line': 9, 'checkpoint': 'f1', 'arg_x': 3}},
            {'_id': {'null': None}, 'c1': {'log_line': 'MIN'}, 'c2': {'log_line': 10, 'checkpoint': 'f1', 'arg_x': 3}}
        ]
        self.check_aggregation_step(step, input, expected_output, remove_id=False)


if __name__ == '__main__':
    unittest.main()
