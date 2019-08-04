#!/usr/bin/env python3

import json

#   This transformation generator module provides a proper interface between CORIOLIS parser
# and rule validator, allowing the later one to execute the rule validation conforming the
# rule syntax. Every rule is solved according the following recipe:
#
#   1) Match all checkpoints by their names
#   2) Rename checkpoint arguments as in the rule expression
#   3) Perform a cross join and grouping according to the rule iterators
#   4) (If needed) Impose conditions on iterators
#   5) Perform comparison of quantity or precedence on each group
#   6) Reduce the result

# 1) Match checkpoints methods

def match_checkpoints(checkpoint_names):
    checkpoint_names = [{"checkpoint": cn} for cn in checkpoint_names]
    return [ {"$match": {"$or": checkpoint_names }} ]

# 2) Rename args methods

def rename_args(checkpoint_names, arg_names_list):
    steps = []
    for i in range(0, len(checkpoint_names)):
        for j in range(0, len(arg_names_list[i])):
            cond = {"$eq": ["$checkpoint", checkpoint_names[i]]}
            true_case = "$arg_{}".format(j + 1)
            false_case = "$arg_{}".format(arg_names_list[i][j])
            r = {"$cond": [cond, true_case, false_case]}
            steps.append( {"$addFields": {"arg_{}".format(arg_names_list[i][j]): r} } )
    return steps

# 3) Cross join and group methods

def cross_group_arg_names(checkpoint_names, arg_names):
    steps = []
    # Step 1: We create a subarray for each checkpoint
    step1 = {"$group": { "_id" : "$checkpoint", "results": {"$push": "$$ROOT"} }}
    steps.append(step1)
    # Step 2: We filter every checkpoint given, creating a subarray for such checkpoint
    step2 = {"$project": {}}
    for i in range(0, len(checkpoint_names)):
        r = {"$filter": { "input": "$results", "as": "r", "cond": {"$eq": ["$$r.checkpoint", checkpoint_names[i]]} }}
        step2["$project"]["r{}".format(i + 1)] = r
    steps.append(step2)
    # Step 3: We rename all checkpoints adding a number to them
    for i in range(0, len(checkpoint_names)):
        checkpoint_name = checkpoint_names[i] + str(i + 1)
        steps.append({"$addFields": { "r{}.checkpoint".format(i + 1): checkpoint_name }})
    # Step 4: We combine all documents into a single one with an array field for each checkpoint
    step4_1 = {"$group": {"_id": "null"}}
    step4_2 = {"$project": {"_id": "$_id"}}
    for i in range(0, len(checkpoint_names)):
        r = "r{}".format(i + 1)
        step4_1["$group"][r] = {"$push":"${}".format(r)}
        step4_2["$project"][r] = {"$reduce": {"input":"${}".format(r), "initialValue": [], "in": {"$concatArrays": ["$$value", "$$this"]}}}
    steps.append(step4_1)
    steps.append(step4_2)
    # Step 5: We unwind every subarray thus performing an all against all join
    for i in range(0, len(checkpoint_names)):
        steps.append({"$unwind": "$r{}".format(i + 1)})
    # Step 6: We perform the grouping by the arg_names
    step6 = {"$group": { "_id": {} }}
    for i in range(0, len(arg_names)):
        arg_name = "arg_{}".format(arg_names[i])
        step6["$group"]["_id"][arg_names[i]] = "$r{}.{}".format(i+1, arg_name)
    for i in range(0, len(checkpoint_names)):
        r = "r{}".format(i+1)
        step6["$group"][r] = {"$push": "$$ROOT.{}".format(r)}
    steps.append(step6)
    # Step 7: We do some array concat to be consistent with the group_by_arg_names formats
    step7 = {"$project": {"_id": "$_id", "results": {"$concatArrays": []}}}
    for i in range(0, len(arg_names)):
        step7["$project"]["results"]["$concatArrays"].append("$r{}".format(i+1))
    steps.append(step7)

    return steps

# 4) Having conditions on iterators methods

def having_iterators(i1, expr, i2):
    EXPR_TO_MATCH = {
        "=": {"$match": { "r": 0 }},
        "<": {"$match": { "r": -1 }},
        ">": {"$match": { "r": 1 }},
        "<=": {"$match": { "$or": [{"r": 0}, {"r": -1}] }},
        ">=": {"$match": { "$or": [{"r": 0}, {"r": 1}] }}
    }
    steps = [ {"$addFields": { "r": {"$cmp": ["$_id.{}".format(i1), "$_id.{}".format(i2)]} }} ]
    steps.append(EXPR_TO_MATCH[expr])

    return steps

# 5) Comparison of quantity or precedence methods

def compare_results_quantity(expr, n):
    EXPR_TO_CMP = {
        "=": "$eq",
        "<": "$lt",
        ">": "$gt",
        "<=": "$lte",
        ">=": "$gte",
    }
    return [ {"$project": { "result": {EXPR_TO_CMP[expr]: [{"$size": "$results"}, n]} }} ]

def compare_results_precedence(checkpoint_first, checkpoint_second, using_precede=True):
    steps = []
    # Step 1: We create two subarrays for each checkpoint
    m1 = {"$filter": { "input": "$results", "as": "r", "cond": {"$eq": ["$$r.checkpoint", checkpoint_first]} }}
    m2 = {"$filter": { "input": "$results", "as": "r", "cond": {"$eq": ["$$r.checkpoint", checkpoint_second]} }}
    steps.append( {"$project": { "first": m1, "second": m2 }} )
    # Step 2: We get the max log_line for the first checkpoint, and the min for the second
    m1 = {"$max": "$first.log_line"}
    m2 = {"$min": "$second.log_line"}
    steps.append( {"$project": { "first": m1, "second": m2 }} )
    # Step 2.5: We purge all records with no "second" value
    if using_precede:
        steps.append( {"$match": { "$expr": {"$ne": ["$second" , None]} }} )
    # Step 3: We check every first value is less than the second value
    steps.append( {"$project": { "result": {"$lt": ["$first", "$second"]} }} )
    return steps

# 6) Reduce result methods:

def reduce_result():
    return [ {"$group": { "_id" : "$result" }} ]

if __name__ == "__main__":
    s = cross_group_arg_names(["produce", "produce"], ["i", "j"])
    print(json.dumps(s, indent=4))
    s = cross_group_arg_names(["produce", "consume"], ["i", "i"])
    print(json.dumps(s, indent=4))
