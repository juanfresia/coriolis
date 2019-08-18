# JARL Language Specification Guide

## Rule statements

A rule _statement_ is the complete declaration of the rule, the whole text. It consists of the following two well-defined parts:

```
(1)  for every w
     between every writer_enter(w) and next writer_exit(w)
(2)    for any r 
       reader_enter(r) must not happen 
```

- **(1) Scope:** Defines which section(s) of the log should be considered to test the rule.
- **(2) Fact:** The concrete action the rule states, and which should be asserted.

## Rule scope

The _scope_ of a rule statement specifies time ranges, during the program execution, in which the rule should be valid. For CORIOLIS logging-based implementation, this is translated as ranges inside the log file (i.e. the rule should be valid between certain log lines).

A rule form can take any of the following forms:

1. ```between [ every | any ] f and [ next | previous ] g```:  

The rule must be validated between a call of `f` and the next or previous call of `g`. if the `every` word was used, the rule must be valid in every checked range. If the `any` word was used, the rule must be valid in at least one range.

Examples:

```
between every lock_acquire and previous lock_release
```

```
between any open_door and next close_door
```

```
between every produce and next consume
```

**Note:** In the last case, if `consume` is not called after some `produce`, then those checkpoints will fall into no validation range and hence it would be as if they did not exist for such rule.

2. ```after [ every | any ] f```

The rule must be valid since a call to `f` and until the end of the execution. The usage of `every` or `any` is like in the `between` scope.

Examples:
```
after any sem_destroy
```
```
after every consume
```

3. ```before [ every | any ] f```

The rule must be valid from the beginning of the execution and until a call to `f`. The usage of `every` or `any` is like in the `between` scope.

Examples:
```
before every sem_create
```
```
before any produce
```

**Note:** In all scopes, the range definition is _inclusive_. For instance, in a `between every f and next g` scope, `f` and `g` are included in every validation range as the left and right extremes of such range.

## Rule filters

Rule _filters_ define how should the checkpoint arguments be matched in order to validate the rule statement. In other words, they specify a concrete grouping strategy for rule validation.

In their most basic form, filters have the following general structure:

```for every [ iterators... ] and any [ wildcards... ]```

Examples:


```
for every i, j and any w
```
```
for every i, j
```
```
for any p, q
```

The `iterators` list of arguments specifies a grouping behaviour when matching the checkpoint arguments values. For instance, suppose that during a program execution the argument `i` took the values `1, 2, 3` and the argument `j` took the values `1, 2, 7, 8`. This way, the `for every i, j` block will group the checkpoint calls in 12 possible categories according to the pair `(i, j)` values: `(1,1), (1,2), (1,7), (1,8), (2,1), (2,2), (2,7), (2,8), (3,1), (3,2), (3,7), (3,8)`. The rule must then be validated inside all of this 12 groups. On the other hand, the `wildcards` list of arguments allows those certain arguments to match any value.

Additionally, conditions can be imposed for making filtering more customizable. 

Examples:

```
for every i, j=i
```

```
for every i, j>i
```

In the above examples, if `i` took the values `1, 2, 3` and `j` took the values `1, 2, 7, 8` then the `(i, j)` pairs to consider would be `(1,1), (2,2)` for the first example and `(1,2), (1,7), (1,8), (2,7), (2,8), (3,7), (3,8)` for the second.

## Rule fact

The _fact_ of a rule statement indicates what should be asserted during the rule validation. These facts can represent two different kind of checkings: 

1. ```f(...) must happen [ <N> | at least <N> | at most <N> ] times ```

The amount of matching calls to `f(...)` must meet a certain criteria. 

2. ```f(...) must [ precede | follow ] g(...)```

All matching calls to `f(...)` must come before or after all matching calls of `g(...)`.