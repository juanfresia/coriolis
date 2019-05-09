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

def rename_args(checkpoint_names, arg_names_list):
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
            if i != (len(checkpoint_names) - 1): projected_json["arg_{}".format(j + 1)] = "$arg_{}".format(j + 1)
        steps.append( {"$project": projected_json} )
    return steps

def group_by_arg_name(arg_name):
    return [ {"$group": { "_id" : "$arg_{}".format(arg_name), "results": {"$push": "$$ROOT"} }} ]

def compare_results_precedence(checkpoint_first, checkpoint_second):
    steps = []
    # Step 1: We create two subarrays for each checkpoint
    m1 = {"$filter": { "input": "$results", "as": "r", "cond": {"$eq": ["$$r.checkpoint", checkpoint_first]} }}
    m2 = {"$filter": { "input": "$results", "as": "r", "cond": {"$eq": ["$$r.checkpoint", checkpoint_second]} }}
    steps.append( {"$project": { "first": m1, "second": m2 }} )
    # Step 2: We get the max log_line for the first checkpoint, and the min for the second
    m1 = {"$max": "$first.log_line"}
    m2 = {"$min": "$second.log_line"}
    steps.append( {"$project": { "first": m1, "second": m2 }} )
    # Step 3: We check every first value is less than the second value
    steps.append( {"$project": { "result": {"$lt": ["$first", "$second"]} }} )
    return steps

def reduce_result():
    return [ {"$group": { "_id" : "$result" }} ]

if __name__ == "__main__":
    s = compare_results_equal(10)
    print(json.dumps(s, indent=4))
