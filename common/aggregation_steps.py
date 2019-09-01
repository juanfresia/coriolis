#!/usr/bin/env python3

import json

#   This AggregationStep class provides a proper interface between CORIOLIS modules and Mongo
# aggregation pipeline, implementing pipeline transformations to execute the rule validation
# conforming the JARL syntax. Its evaluate method returns the "Mongo JSON" version of the
# step, ready to be inserted into Mongo pipeline (although you need to flatten such value
# returned if you concatenate many of these steps into a single array). The dynamic_args
# dict allows the Aggregation class to override values when calling evaluate, thus providing
# a way to set an AggregationStep value after the creation of the object instance.
class AggregationStep:
    def __init__(self):
        self.overridable_list = []

    def evaluate(self, dynamic_args={}):
        for k in self.overridable_list:
            if getattr(self, k) in dynamic_args:
                setattr(self, k, dynamic_args[getattr(self, k)])
        return self._mongofy()

    def _mongofy(self):
        raise NotImplementedError

    def _expr_to_cmp(self, expr):
        EXPR_TO_CMP = {
            "=": "$eq",
            "<": "$lt",
            ">": "$gt",
            "<=": "$lte",
            ">=": "$gte",
            "!=": "$ne",
        }
        return EXPR_TO_CMP[expr]

    def _int_to_str(self, x):
        return {"$substr": [x, 0, -1]}

#   Every rule is solved according to the following recipe:
#
#   First, the scope of the rule must be resolved via the aggregation pipeline with these steps:
#     1) Match all scope checkpoints by their names
#     2) Rename checkpoint arguments as in the scope expression
#     3) Perform a cross join and group according to the scope iterators
#     4) (If needed) Impose conditions on checkpoint arguments
#     5) Perform the scope operation according to the checkpoint(s) involved
#   Then, for every scope defined, the rule fact must be evaluated (recieving, if needed, any
#   dynamic args from the scope) according to the following:
#     1) Filter between the log lines of the current scope
#     2) Match all fact checkpoints by their names
#     3) Rename checkpoint arguments as in the fact expression
#     4) Perform a cross join and grouping according to the fact iterators
#     5) (If needed) Impose conditions on checkpoint arguments
#     6) Perform comparison of quantity or precedence on each group
#     7) Reduce the result
#
#   The following classes are designed to solve the above specified steps.


# USAGE EXAMPLE: MatchCheckpoints( ["f", "h"] )
# Input:
#   {'log_line': 1, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'f'}
#   {'log_line': 2, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'g'}
#   {'log_line': 3, 'arg_1': 2, 'arg_2': 2, 'checkpoint': 'f'}
#   {'log_line': 4, 'arg_1': 2, 'arg_2': 3, 'checkpoint': 'h'}
# Output:
#   {'log_line': 1, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'f'}
#   {'log_line': 3, 'arg_1': 2, 'arg_2': 2, 'checkpoint': 'f'}
#   {'log_line': 4, 'arg_1': 2, 'arg_2': 3, 'checkpoint': 'h'}
class MatchCheckpoints(AggregationStep):
    def __init__(self, checkpoint_names):
        super().__init__()
        self.checkpoint_names = checkpoint_names

    def _mongofy(self):
        checkpoint_names = [{"checkpoint": cn} for cn in self.checkpoint_names]
        return [ {"$match": {"$or": checkpoint_names }} ]

# USAGE EXAMPLE: RenameArgs( ["f", "g"], [ ["i", "j"], ["a1", "a2"] ] )
# Input:
#   {'log_line': 1, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'f'}
#   {'log_line': 2, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'g'}
#   {'log_line': 3, 'arg_1': 2, 'arg_2': 2, 'checkpoint': 'f'}
# Output:
#   {'log_line': 1, 'checkpoint': 'f', 'arg_i': 1, 'arg_j': 1}
#   {'log_line': 2, 'checkpoint': 'g', 'arg_a1': 1, 'arg_a2': 1}
#   {'log_line': 3, 'checkpoint': 'f', 'arg_i': 2, 'arg_j': 2}
class RenameArgs(AggregationStep):
    def  __init__(self, checkpoint_names, arg_names_list):
        super().__init__()
        self.checkpoint_names = checkpoint_names
        self.arg_names_list = arg_names_list

    def _mongofy(self):
        steps = []
        all_args = {"log_line": 1, "checkpoint": 1}
        for i in range(0, len(self.checkpoint_names)):
            new_args = {}
            for j in range(0, len(self.arg_names_list[i])):
                cond = {"$eq": ["$checkpoint", self.checkpoint_names[i]]}
                true_case = "$arg_{}".format(j + 1)
                false_case = "$arg_{}".format(self.arg_names_list[i][j])
                r = {"$cond": [cond, true_case, false_case]}
                new_args["arg_{}".format(self.arg_names_list[i][j])] = r
                all_args["arg_{}".format(self.arg_names_list[i][j])] = 1
            steps.append( {"$addFields": new_args } )

        steps.append( {"$project": all_args} )
        return steps

# USAGE EXAMPLE: CrossJoinCheckpoints( ["f", "g"] )
# Input:
#   {'log_line': 1, 'checkpoint': 'f', 'arg_p': 1}
#   {'log_line': 2, 'checkpoint': 'g', 'arg_c': 1, 'arg_i': 1}
#   {'log_line': 3, 'checkpoint': 'f', 'arg_p': 2}
#   {'log_line': 4, 'checkpoint': 'f', 'arg_p': 2}
#   {'log_line': 5, 'checkpoint': 'g', 'arg_c': 1, 'arg_i': 2}
# Output:
#   {'r1': {'log_line': 1, 'checkpoint': 'f1', 'arg_p': 1}, 'r2': {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i': 1}}
#   {'r1': {'log_line': 1, 'checkpoint': 'f1', 'arg_p': 1}, 'r2': {'log_line': 5, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i': 2}}
#   {'r1': {'log_line': 3, 'checkpoint': 'f1', 'arg_p': 2}, 'r2': {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i': 1}}
#   {'r1': {'log_line': 3, 'checkpoint': 'f1', 'arg_p': 2}, 'r2': {'log_line': 5, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i': 2}}
#   {'r1': {'log_line': 4, 'checkpoint': 'f1', 'arg_p': 2}, 'r2': {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i': 1}}
#   {'r1': {'log_line': 4, 'checkpoint': 'f1', 'arg_p': 2}, 'r2': {'log_line': 5, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i': 2}}
#
# NOTE: The checkpoint names are modified by adding a number sufix (i.e. from "f","g" to "f1","g2")
class CrossJoinCheckpoints(AggregationStep):
    def __init__(self, checkpoint_names):
        super().__init__()
        self.checkpoint_names = checkpoint_names

    def _mongofy(self):
        steps = []
        # Step 1: We create a subarray for each checkpoint
        step1 = {"$group": { "_id" : "$checkpoint", "results": {"$push": "$$ROOT"} }}
        steps.append(step1)
        # Step 2: We filter every checkpoint given, creating a subarray for such checkpoint
        step2 = {"$project": {}}
        for i in range(0, len(self.checkpoint_names)):
            r = {"$filter": { "input": "$results", "as": "r", "cond": {"$eq": ["$$r.checkpoint", self.checkpoint_names[i]]} }}
            step2["$project"]["r{}".format(i + 1)] = r
        steps.append(step2)
        # Step 3: We rename all checkpoints adding a number to them
        all_checkpoints = {}
        for i in range(0, len(self.checkpoint_names)):
            checkpoint_name = self.checkpoint_names[i] + str(i + 1)
            all_checkpoints["r{}.checkpoint".format(i + 1)] = checkpoint_name
        steps.append({"$addFields": all_checkpoints})
        # Step 4: We combine all documents into a single one with an array field for each checkpoint
        step4_1 = {"$group": {"_id": "null"}}
        step4_2 = {"$project": {"_id": "$_id"}}
        for i in range(0, len(self.checkpoint_names)):
            r = "r{}".format(i + 1)
            step4_1["$group"][r] = {"$push":"${}".format(r)}
            step4_2["$project"][r] = {"$reduce": {"input":"${}".format(r), "initialValue": [], "in": {"$concatArrays": ["$$value", "$$this"]}}}
        steps.append(step4_1)
        steps.append(step4_2)
        # Step 5: We unwind every subarray thus performing an all against all join
        for i in range(0, len(self.checkpoint_names)):
            steps.append({"$unwind": "$r{}".format(i + 1)})

        return steps

# USAGE EXAMPLE: CrossAndGroupByArgs( ["f", "g"], [ ["i1"], ["i2"] ] )
# Input:
#   {'log_line': 1, 'checkpoint': 'f', 'arg_i1': 1}
#   {'log_line': 2, 'checkpoint': 'g', 'arg_c': 1, 'arg_i2': 1}
#   {'log_line': 3, 'checkpoint': 'f', 'arg_i1': 2}
#   {'log_line': 4, 'checkpoint': 'f', 'arg_i1': 3}
#   {'log_line': 6, 'checkpoint': 'g', 'arg_c': 1, 'arg_i2': 2}
# Output:
#   {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 1}], '_id': {'i2': 1, 'i1': 1}}
#   {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 6, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 2}], '_id': {'i2': 2, 'i1': 1}}
#   {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}, {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 1}], '_id': {'i2': 1, 'i1': 2}}
#   {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}, {'log_line': 6, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 2}], '_id': {'i2': 2, 'i1': 2}}
#   {'results': [{'log_line': 4, 'checkpoint': 'f1', 'arg_i1': 3}, {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 1}], '_id': {'i2': 1, 'i1': 3}}
#   {'results': [{'log_line': 4, 'checkpoint': 'f1', 'arg_i1': 3}, {'log_line': 6, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 2}], '_id': {'i2': 2, 'i1': 3}}
#
# NOTE: The checkpoint names are modified by adding a number sufix (i.e. from "f","g" to "f1","g2")
class CrossAndGroupByArgs(AggregationStep):
    def __init__(self, checkpoint_names, arg_names):
        super().__init__()
        self.checkpoint_names = checkpoint_names
        self.arg_names = arg_names

    def _mongofy(self):
        # Step 1: We cross join all checkpoints according their names
        steps = CrossJoinCheckpoints(self.checkpoint_names).evaluate()
        # Step 2: We perform the grouping by the arg_names
        step2 = {"$group": { "_id": {} }}
        for i in range(0, len(self.arg_names)):
            for arg in self.arg_names[i]:
                arg_name = "arg_{}".format(arg)
                step2["$group"]["_id"][arg] = "$r{}.{}".format(i+1, arg_name)
        for i in range(0, len(self.checkpoint_names)):
            r = "r{}".format(i+1)
            step2["$group"][r] = {"$push": "$$ROOT.{}".format(r)}
        steps.append(step2)
        # Step 3: We do some array concat to be consistent with the output formats
        step3 = {"$project": {"_id": "$_id", "results": {"$setUnion": []}}}
        for i in range(0, len(self.checkpoint_names)):
            step3["$project"]["results"]["$setUnion"].append("$r{}".format(i+1))
        steps.append(step3)

        return steps

# USAGE EXAMPLE: ImposeIteratorCondition("i1", "<=", "i2")
# Input:
#   {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 1}], '_id': {'i2': 1, 'i1': 1}}
#   {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 6, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 2}], '_id': {'i2': 2, 'i1': 1}}
#   {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}, {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 1}], '_id': {'i2': 1, 'i1': 2}}
#   {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}, {'log_line': 6, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 2}], '_id': {'i2': 2, 'i1': 2}}
#   {'results': [{'log_line': 4, 'checkpoint': 'f1', 'arg_i1': 3}, {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 1}], '_id': {'i2': 1, 'i1': 3}}
#   {'results': [{'log_line': 4, 'checkpoint': 'f1', 'arg_i1': 3}, {'log_line': 6, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 2}], '_id': {'i2': 2, 'i1': 3}}
# Output:
#   {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 2, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 1}], '_id': {'i2': 1, 'i1': 1}}
#   {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 6, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 2}], '_id': {'i2': 2, 'i1': 1}}
#   {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}, {'log_line': 6, 'checkpoint': 'g2', 'arg_c': 1, 'arg_i2': 2}], '_id': {'i2': 2, 'i1': 2}}
class ImposeIteratorCondition(AggregationStep):
    def __init__(self, i1, expr, i2, using_literal=False):
        super().__init__()
        self.i1 = i1
        self.expr = expr
        self.i2 = i2
        self.using_literal = using_literal
        self.overridable_list += ["i1", "i2"]

    def _mongofy(self):
        i2 = self.i2 if self.using_literal else "$_id.{}".format(self.i2)
        return [ {"$match": { "$expr": {self._expr_to_cmp(self.expr): ["$_id.{}".format(self.i1), i2]} }} ]

# USAGE EXAMPLE: ImposeWildcardCondition("w1", ">=", "w2")
# Input:
#   {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_w1': 1, 'arg_w2': 0}]}
#   {'results': [{'log_line': 2, 'checkpoint': 'f1', 'arg_w1': 1, 'arg_w2': 2}]}
#   {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_w1': 2, 'arg_w2': 4}]}
#   {'results': [{'log_line': 4, 'checkpoint': 'f1', 'arg_w1': 2, 'arg_w2': 4}]}
#   {'results': [{'log_line': 5, 'checkpoint': 'f1', 'arg_w1': 3, 'arg_w2': 2}]}
#   {'results': [{'log_line': 6, 'checkpoint': 'f1', 'arg_w1': 3, 'arg_w2': 0}]}
# Output:
#   {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_w1': 1, 'arg_w2': 0}]}
#   {'results': []}
#   {'results': []}
#   {'results': []}
#   {'results': [{'log_line': 5, 'checkpoint': 'f1', 'arg_w1': 3, 'arg_w2': 2}]}
#   {'results': [{'log_line': 6, 'checkpoint': 'f1', 'arg_w1': 3, 'arg_w2': 0}]}
class ImposeWildcardCondition(AggregationStep):
    def __init__(self, w1, expr, w2, using_literal=False):
        super().__init__()
        self.w1 = w1
        self.expr = expr
        self.w2 = w2
        self.using_literal = using_literal
        self.overridable_list += ["w1", "w2"]

    def _mongofy(self):
        w2 = self.w2 if self.using_literal else "$$r.arg_{}".format(self.w2)
        cond = {"input": "$results", "as": "r", "cond": { self._expr_to_cmp(self.expr): ["$$r.arg_{}".format(self.w1), w2] }}
        steps = [ {"$project": {"_id": "$_id", "results": { "$filter": cond }}} ]
        #steps.append( {"$match": { "$expr": {"$ne": ["$results", []]} }} ) # Discard empty results arrays
        return steps

# USAGE EXAMPLE: CompareResultsQuantity("=", 1)
# Input:
#   {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_x': 1}], '_id': {'i': 1}}
#   {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_x': 2}], '_id': {'i': 2}}
#   {'results': [{'log_line': 7, 'checkpoint': 'f1', 'arg_x': 3}, {'log_line': 11, 'checkpoint': 'f1', 'arg_x': 4}], '_id': {'i': 3}}
# Output:
#   {'result': True, 'info': 'Some info message', '_id': {'i': 1}}
#   {'result': True, 'info': 'Some info message', '_id': {'i': 2}}
#   {'result': False, 'info': 'Some info message', '_id': {'i': 3}}
class CompareResultsQuantity(AggregationStep):
    def __init__(self, expr, n):
        super().__init__()
        self.expr = expr
        self.n = n

    def _make_info_message(self):
        log_lines = {"$map": { "input": "$results", "as": "r", "in": {"$concat": [ " ", self._int_to_str("$$r.log_line") ]} }}
        log_lines = {"$reduce": {"input": log_lines, "initialValue": "", "in": {"$concat": ["$$value", "$$this"]}}}
        return {"$concat": [ "Checkpoint happened ", self._int_to_str({"$size": "$results"}), " times (involved lines on log:", log_lines, ").\n" ]}

    def _mongofy(self):
        info = self._make_info_message()
        return [ {"$project": { "result": {self._expr_to_cmp(self.expr): [{"$size": "$results"}, self.n]}, "info": info }} ]

# USAGE EXAMPLE: CompareResultsPrecedence("f1", "g2")
# Input:
#   {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}, {'log_line': 7, 'checkpoint': 'g2', 'arg_i2': 2}], '_id': {'i2': 2, 'i1': 2}}
#   {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 2, 'checkpoint': 'g2', 'arg_i2': 1}], '_id': {'i2': 1, 'i1': 1}}
#   {'results': [{'log_line': 5, 'checkpoint': 'f1', 'arg_i1': 3}, {'log_line': 4, 'checkpoint': 'g2', 'arg_i2': 3}], '_id': {'i2': 3, 'i1': 3}}
# Output:
#   {'result': True, 'info': 'Some info message', '_id': {'i1': 2, 'i2': 2}}
#   {'result': True, 'info': 'Some info message', '_id': {'i1': 1, 'i2': 1}}
#   {'result': False, 'info': 'Some info message', '_id': {'i1': 3, 'i2': 3}}
class CompareResultsPrecedence(AggregationStep):
    def __init__(self, checkpoint_first, checkpoint_second):
        super().__init__()
        self.checkpoint_first = checkpoint_first
        self.checkpoint_second = checkpoint_second

    def _make_info_message(self):
        msg = "Checkpoint {} did not precede {} (involved lines on log: ".format(self.checkpoint_first[:-1], self.checkpoint_second[:-1])
        return {"$concat": [ msg, self._int_to_str("$first"), " ", self._int_to_str("$second"), ").\n" ]}

    def _mongofy(self):
        steps = []
        # Step 1: We create two subarrays for each checkpoint
        m1 = {"$filter": { "input": "$results", "as": "r", "cond": {"$eq": ["$$r.checkpoint", self.checkpoint_first]} }}
        m2 = {"$filter": { "input": "$results", "as": "r", "cond": {"$eq": ["$$r.checkpoint", self.checkpoint_second]} }}
        steps.append( {"$project": { "first": m1, "second": m2 }} )
        # Step 2: We get the max log_line for the first checkpoint, and the min for the second
        m1 = {"$max": "$first.log_line"}
        m2 = {"$min": "$second.log_line"}
        steps.append( {"$project": { "first": m1, "second": m2 }} )
        # Step 3: We check every first value is less than the second value
        steps.append( {"$project": { "result": {"$lt": ["$first", "$second"]}, "info": self._make_info_message() }} )
        return steps

# USAGE EXAMPLE: ReduceResult()
# Input:
#   {'result': False, 'info': 'Info message 1\n'}
#   {'result': True, 'info': 'Info message 2\n'}
#   {'result': False, 'info': 'Info message 3\n'}
#   {'result': True, 'info': 'Info message 4\n'}
# Output:
#   {'_id': False, 'info': 'Info message 1\nInfo message 3\n'}
class ReduceResult(AggregationStep):
    def __init__(self, and_results=True):
        super().__init__()
        self.and_results = and_results

    def _mongofy(self):
        steps = [ {"$addFields": {"info": {"$cond": ["$result", "", "$info"]}}} ]
        op = "$and" if self.and_results else "$or"
        initial_value = self.and_results
        steps.append( {"$group": { "_id" : "null", "r": {"$push": "$$ROOT"} }} )
        _id = {"$reduce": {"input": "$r", "initialValue": initial_value, "in": {op: ["$$value", "$$this.result"]}}}
        info = {"$reduce": {"input": "$r", "initialValue": "", "in": {"$concat": ["$$value", "$$this.info"]}}}
        steps.append( {"$project": {"_id": _id, "info": info}} )
        return steps

# USAGE EXAMPLE: FilterByLogLines(2, 4)
# Input:
#   {'log_line': 1, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'f'}
#   {'log_line': 2, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'g'}
#   {'log_line': 3, 'arg_1': 2, 'arg_2': 2, 'checkpoint': 'f'}
#   {'log_line': 4, 'arg_1': 2, 'arg_2': 3, 'checkpoint': 'h'}
#   {'log_line': 5, 'arg_1': 3, 'arg_2': 9, 'checkpoint': 'g'}
# Output:
#   {'log_line': 2, 'arg_1': 1, 'arg_2': 1, 'checkpoint': 'g'}
#   {'log_line': 3, 'arg_1': 2, 'arg_2': 2, 'checkpoint': 'f'}
#   {'log_line': 4, 'arg_1': 2, 'arg_2': 3, 'checkpoint': 'h'}
class FilterByLogLines(AggregationStep):
    def __init__(self, l_first, l_second):
        super().__init__()
        self.l_first = l_first
        self.l_second = l_second

    def _mongofy(self):
        if (self.l_second == "MAX") and (self.l_first == "MIN"): return []
        if self.l_second == "MAX": return [ {"$match": { "log_line": {"$gte": self.l_first} }} ]
        if self.l_first == "MIN": return [ {"$match": { "log_line": {"$lte": self.l_second} }} ]
        return [ {"$match": { "log_line": {"$gte": self.l_first, "$lte": self.l_second} }} ]

# TODO: Throw away since it is not used?
class SortByLogLine(AggregationStep):
    def __init__(self, ascending=True):
        super().__init__()
        self.ascending = ascending

    def _mongofy(self):
        return [ {"$sort": {"log_line": 1 if self.ascending else -1}} ]

# USAGE EXAMPLE: ScopeAfter("f1")
# Input:
#   {'_id': {'null': None}, 'results': [
#     {'log_line': 2, 'checkpoint': 'f1', 'arg_x': 1},
#     {'log_line': 6, 'checkpoint': 'f1', 'arg_x': 1},
#     {'log_line': 8, 'checkpoint': 'f1', 'arg_x': 2},
#     {'log_line': 9, 'checkpoint': 'f1', 'arg_x': 3},
#     {'log_line': 10, 'checkpoint': 'f1', 'arg_x': 3}
#   ]}
# Output:
#   {'_id': {'null': None}, 'c1': {'log_line': 2, 'checkpoint': 'f1', 'arg_x': 1}, 'c2': {'log_line': 'MAX'}}
#   {'_id': {'null': None}, 'c1': {'log_line': 6, 'checkpoint': 'f1', 'arg_x': 1}, 'c2': {'log_line': 'MAX'}}
#   {'_id': {'null': None}, 'c1': {'log_line': 8, 'checkpoint': 'f1', 'arg_x': 2}, 'c2': {'log_line': 'MAX'}}
#   {'_id': {'null': None}, 'c1': {'log_line': 9, 'checkpoint': 'f1', 'arg_x': 3}, 'c2': {'log_line': 'MAX'}}
#   {'_id': {'null': None}, 'c1': {'log_line': 10, 'checkpoint': 'f1', 'arg_x': 3}, 'c2': {'log_line': 'MAX'}}
class ScopeAfter(AggregationStep):
    def __init__(self, checkpoint_name):
        super().__init__()
        self.checkpoint_name = checkpoint_name

    def _mongofy(self):
        steps = []
        steps.append( {"$unwind": "$results"} )
        steps.append( {"$project": {"c1": "$results", "c2": {"log_line": "MAX"}}} )
        return steps

# USAGE EXAMPLE: ScopeBefore("f1")
# Input:
#   {'_id': {'null': None}, 'results': [
#     {'log_line': 2, 'checkpoint': 'f1', 'arg_x': 1},
#     {'log_line': 6, 'checkpoint': 'f1', 'arg_x': 1},
#     {'log_line': 8, 'checkpoint': 'f1', 'arg_x': 2},
#     {'log_line': 9, 'checkpoint': 'f1', 'arg_x': 3},
#     {'log_line': 10, 'checkpoint': 'f1', 'arg_x': 3}
#   ]}
# Output:
#   {'_id': {'null': None}, 'c1': {'log_line': 'MIN'}, 'c2': {'log_line': 2, 'checkpoint': 'f1', 'arg_x': 1}},
#   {'_id': {'null': None}, 'c1': {'log_line': 'MIN'}, 'c2': {'log_line': 6, 'checkpoint': 'f1', 'arg_x': 1}},
#   {'_id': {'null': None}, 'c1': {'log_line': 'MIN'}, 'c2': {'log_line': 8, 'checkpoint': 'f1', 'arg_x': 2}},
#   {'_id': {'null': None}, 'c1': {'log_line': 'MIN'}, 'c2': {'log_line': 9, 'checkpoint': 'f1', 'arg_x': 3}},
#   {'_id': {'null': None}, 'c1': {'log_line': 'MIN'}, 'c2': {'log_line': 10, 'checkpoint': 'f1', 'arg_x': 3}}
class ScopeBefore(AggregationStep):
    def __init__(self, checkpoint_name):
        super().__init__()
        self.checkpoint_name = checkpoint_name

    def _mongofy(self):
        steps = []
        steps.append( {"$unwind": "$results"} )
        steps.append( {"$project": {"c2": "$results", "c1": {"log_line": "MIN"}}} )
        return steps

# USAGE EXAMPLE: ScopeBetween("f1", "g2")
# Input:
#   {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 2, 'checkpoint': 'g2', 'arg_i2': 1}], '_id': {'i1': 1, 'i2': 1}}
#   {'results': [{'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, {'log_line': 6, 'checkpoint': 'g2', 'arg_i2': 2}], '_id': {'i1': 1, 'i2': 2}}
#   {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}, {'log_line': 2, 'checkpoint': 'g2', 'arg_i2': 1}], '_id': {'i1': 2, 'i2': 1}}
#   {'results': [{'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}, {'log_line': 6, 'checkpoint': 'g2', 'arg_i2': 2}], '_id': {'i1': 2, 'i2': 2}}
#   {'results': [{'log_line': 4, 'checkpoint': 'f1', 'arg_i1': 3}, {'log_line': 2, 'checkpoint': 'g2', 'arg_i2': 1}], '_id': {'i1': 3, 'i2': 1}}
#   {'results': [{'log_line': 4, 'checkpoint': 'f1', 'arg_i1': 3}, {'log_line': 6, 'checkpoint': 'g2', 'arg_i2': 2}], '_id': {'i1': 3, 'i2': 2}}
# Output:
#   {'c2': {'log_line': 2, 'checkpoint': 'g2', 'arg_i2': 1}, 'c1': {'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, '_id': {'i1': 1, 'i2': 1}}
#   {'c2': {'log_line': 6, 'checkpoint': 'g2', 'arg_i2': 2}, 'c1': {'log_line': 1, 'checkpoint': 'f1', 'arg_i1': 1}, '_id': {'i1': 1, 'i2': 2}}
#   {'c2': {'log_line': 6, 'checkpoint': 'g2', 'arg_i2': 2}, 'c1': {'log_line': 3, 'checkpoint': 'f1', 'arg_i1': 2}, '_id': {'i1': 2, 'i2': 2}}
#   {'c2': {'log_line': 6, 'checkpoint': 'g2', 'arg_i2': 2}, 'c1': {'log_line': 4, 'checkpoint': 'f1', 'arg_i1': 3}, '_id': {'i1': 3, 'i2': 2}}
class ScopeBetween(AggregationStep):
    def __init__(self, checkpoint_first, checkpoint_second, using_next=True, using_beyond=False):
        super().__init__()
        self.checkpoint_first = checkpoint_first
        self.checkpoint_second = checkpoint_second
        self.using_next = using_next
        self.using_beyond = using_beyond

    def _mongofy(self):
        steps = []
        # Step 1: We create two subarrays for each checkpoint
        c1 = "{}".format(self.checkpoint_first)
        c2 = "{}_{}".format("next" if self.using_next else "prev", self.checkpoint_second)
        m1 = {"$filter": { "input": "$results", "as": "r", "cond": {"$eq": ["$$r.checkpoint", self.checkpoint_first]} }}
        m2 = {"$filter": { "input": "$results", "as": "r", "cond": {"$eq": ["$$r.checkpoint", self.checkpoint_second]} }}
        steps.append( {"$project": { c1: m1, c2: m2 }} )
        # Step 2: We unwind the first one, thus having every checkpoint_first against all checkpoint_second
        steps.append({"$unwind": "${}".format(c1)})
        # Step 3: We find the next or previous checkpoint_second occurrence to form the pair
        m2 = {"$filter": { "input": "${}".format(c2), "as": "r" }}
        if self.using_next:
            m2["$filter"]["cond"] = {"$gt": ["$$r.log_line", "${}.log_line".format(c1)]}
            m2 = {"$min": m2}
            steps.append( {"$project": { "c1": "${}".format(c1), "c2": m2 }} )
        else:
            m2["$filter"]["cond"] = {"$lt": ["$$r.log_line", "${}.log_line".format(c1)]}
            m2 = {"$max": m2}
            steps.append({"$project": { "c2": "${}".format(c1), "c1": m2 }})
        # Step 4: If using beyond, we add a MIN or MAX pair
        c = "c2" if self.using_next else "c1"
        if self.using_beyond: # We replace all None with MIN or MAX values
            m = {"log_line": "MAX" if self.using_next else "MIN"}
            # TODO: Add fields in m?
            steps.append( {"$addFields": {c: {"$ifNull": ["${}".format(c), m]}}} )
        else: # We filter all None elements
            steps.append( {"$match": {"$expr": {"$ne": ["${}".format(c), None]}}} )

        return steps

if __name__ == "__main__":
    s = ReduceResult()
    print(json.dumps(s.evaluate(), indent=4))
