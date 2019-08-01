#!/usr/bin/env python3

import json

def match_checkpoint(checkpoint_name):
    return [ {"$match": {"checkpoint": checkpoint_name}} ]

def match_checkpoints(checkpoint_names):
    checkpoint_names = [{"checkpoint": cn} for cn in checkpoint_names]
    return [ {"$match": {"$or": checkpoint_names }} ]

def compare_results_equal(n):
    return [ {"$project": { "result": {"$eq": [{"$size": "$results"}, n]} }} ]

def compare_results_greater_than(n):
    return [ {"$project": { "result": {"$gt": [{"$size": "$results"}, n]} }} ]

def compare_results_lower_than(n):
    return [ {"$project": { "result": {"$lt": [{"$size": "$results"}, n]} }} ]

def having_greater_iterator(i_lower, i_bigger):
    steps = []
    steps.append({"$addFields": { "r": {"$cmp": ["$_id.{}".format(i_bigger), "$_id.{}".format(i_lower)]} }}),
    steps.append({"$match": { "r": 1 }})
    return steps

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

def _rename_args(checkpoint_names, arg_names_list):
    max_args = max( [len(a) for a in arg_names_list] )
    all_args_names = set()
    for args in arg_names_list:
        for a in args:
            all_args_names.add("arg_{}".format(a))

    steps = []
    for i in range(0, len(checkpoint_names)):
        projected_json = {"checkpoint": "$checkpoint", "log_line": "$log_line"}
        for a in all_args_names: projected_json[a] = "${}".format(a)
        for j in range(0, max_args):
            cond = {"$eq": ["$checkpoint", checkpoint_names[i]]}
            true_case = "$arg_{}".format(j + 1)
            false_case = "$arg_{}".format(arg_names_list[i][j])
            projected_json["arg_{}".format(arg_names_list[i][j])] = {"$cond": [cond, true_case, false_case]}
            projected_json["arg_{}".format(j + 1)] = "$arg_{}".format(j + 1)
        steps.append( {"$project": projected_json} )
    return steps

def group_by_arg_names(arg_names):
    group_id = {}
    for arg_name in arg_names:
        group_id[arg_name] = "$arg_{}".format(arg_name)
    return [ {"$group": { "_id" : group_id, "results": {"$push": "$$ROOT"} }} ]

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
    # Step 4: We unwind every subarray thus performing an all against all join
    for i in range(0, len(checkpoint_names)):
        steps.append({"$unwind": "$r{}".format(i + 1)})
    # Step 5: We perform the grouping by the arg_names
    step5 = {"$group": { "_id": {} }}
    for i in range(0, len(arg_names)):
        arg_name = "arg_{}".format(arg_names[i])
        step5["$group"]["_id"][arg_names[i]] = "$r{}.{}".format(i+1, arg_name)
    for i in range(0, len(checkpoint_names)):
        r = "r{}".format(i+1)
        step5["$group"][r] = {"$push": "$$ROOT.{}".format(r)}
    steps.append(step5)
    # Step 6: We do some array concat to be consistent with the group_by_arg_names format
    step6 = {"$project": {"_id": "$_id", "results": {"$concatArrays": []}}}
    for i in range(0, len(arg_names)):
        step6["$project"]["results"]["$concatArrays"].append("$r{}".format(i+1))
    steps.append(step6)

    return steps

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

def reduce_result():
    return [ {"$group": { "_id" : "$result" }} ]

if __name__ == "__main__":
    s = cross_by_arg_names(["produce", "produce"])
    print(json.dumps(s, indent=4))
