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
#   The following classes are designed to solve the above specified steps

class MatchCheckpoints(AggregationStep):
    def __init__(self, checkpoint_names):
        super().__init__()
        self.checkpoint_names = checkpoint_names

    def _mongofy(self):
        checkpoint_names = [{"checkpoint": cn} for cn in self.checkpoint_names]
        return [ {"$match": {"$or": checkpoint_names }} ]


class RenameArgs(AggregationStep):
    def  __init__(self, checkpoint_names, arg_names_list):
        super().__init__()
        self.checkpoint_names = checkpoint_names
        self.arg_names_list = arg_names_list

    def _mongofy(self):
        steps = []
        for i in range(0, len(self.checkpoint_names)):
            for j in range(0, len(self.arg_names_list[i])):
                cond = {"$eq": ["$checkpoint", self.checkpoint_names[i]]}
                true_case = "$arg_{}".format(j + 1)
                false_case = "$arg_{}".format(self.arg_names_list[i][j])
                r = {"$cond": [cond, true_case, false_case]}
                steps.append( {"$addFields": {"arg_{}".format(self.arg_names_list[i][j]): r} } )
        return steps


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
        for i in range(0, len(self.checkpoint_names)):
            checkpoint_name = self.checkpoint_names[i] + str(i + 1)
            steps.append({"$addFields": { "r{}.checkpoint".format(i + 1): checkpoint_name }})
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
        steps.append( {"$match": { "$expr": {"$ne": ["$results", []]} }} ) # Discard empty results arrays
        return steps


class CompareResultsQuantity(AggregationStep):
    def __init__(self, expr, n):
        super().__init__()
        self.expr = expr
        self.n = n

    def _mongofy(self):
        return [ {"$project": { "result": {self._expr_to_cmp(self.expr): [{"$size": "$results"}, self.n]} }} ]

class CompareResultsPrecedence(AggregationStep):
    def __init__(self, checkpoint_first, checkpoint_second, using_precede=True):
        super().__init__()
        self.checkpoint_first = checkpoint_first
        self.checkpoint_second = checkpoint_second
        self.using_precede = using_precede

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
        # Step 2.5: We purge all records with no "second" value
        if self.using_precede:
            steps.append( {"$match": { "$expr": {"$ne": ["$second" , None]} }} )
        # Step 3: We check every first value is less than the second value
        steps.append( {"$project": { "result": {"$lt": ["$first", "$second"]} }} )
        return steps


class ReduceResult(AggregationStep):
    def __init__(self):
        super().__init__()

    def _mongofy(self):
        return [ {"$group": { "_id" : "$result" }} ]


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


class ScopeAfter(AggregationStep):
    def __init__(self, checkpoint_name):
        super().__init__()
        self.checkpoint_name = checkpoint_name

    def _mongofy(self):
        steps = []
        steps.append( {"$unwind": "$results"} )
        steps.append( {"$project": {"c1": "$results", "c2": {"log_line": "MAX"}}} )
        return steps


class ScopeBefore(AggregationStep):
    def __init__(self, checkpoint_name):
        super().__init__()
        self.checkpoint_name = checkpoint_name

    def _mongofy(self):
        steps = []
        steps.append( {"$unwind": "$results"} )
        steps.append( {"$project": {"c2": "$results", "c1": {"log_line": "MIN"}}} )
        return steps


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
