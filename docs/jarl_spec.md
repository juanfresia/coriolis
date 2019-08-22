# JARL Language Specification Guide

![](jarl_logo2.png)

## Abstract

JARL aims to define a "common language"" for writing business level user-defined rules for concurrent programs. This specification guide covers the main aspects of the language, providing different useful examples for each topic.

## Table of contents

TODO: Fill when finished


## Execution checkpoints

In order to define easily readable and writable concurrent rules, JARL depends on the concept of _checkpoints_ during the program execution. Checkpoints are precisely defined points of the code which the underlying testing runtime will be available to trace. Essentially, checkpoints might be seen as ordinary functions, except they are really not implemented by the developer of the program but by the testing framework itself.

These checkpoints are meant to represent concrete events of the concurrent problem that users would like to trace while their program is running. For instance, in the producer-consumer problem, consumer processes should have a "consume" checkpoint in their codes, while producer processes should have a "produce" one. The true purpose of these checkpoints is, then, to be used as "control points" during the concurrent execution. 

The underlying testing runtime must be able to detect _when_ did these checkpoints happened and with _which argument values_. These argument values are fetched from the program execution (i.e. they match code variables) and allow definition of JARL rules matching some criteria. Currently, JARL supported argument types are `int`, `float`, `char` and `string` (with no whitespaces).

A program set of checkpoints and their respective arguments should be defined a priori, on a separate file in a sort of checkpoints table. A possible checkpoints table for the producer-consumer example could be like the following:

```
# Format is:
#   <breakpoint-name> [<arg-name>:<arg-type> ...]

produce   producer_id:int   item:int
consume   consumer_id:int   item:int
``` 

## Rule statement

A rule _statement_ is the complete declaration of a JARL rule, addressing certain checkpoints of the code with their arguments. It consists of the following two well-defined parts:

- **Scope definition:** Defines which time intervals during the execution of the concurrent program should be considered to test the rule.
- **Fact definition:** The concrete action the rule states, and which should be asserted inside every declared scope.

Checkpoints can be referenced inside both sections together with their arguments. For instance, `produce(p, i)` may refer to the `produce` checkpoint defined on the previous section. As it will be shown in the following sections, JARL syntax allows the writer of the concurrent rules to address these arguments by their values generically, thus providing a flexible and clean way for explaining business-layered concurrent concerns.

## Rule fact

The _fact_ of a rule statement indicates what should be asserted during the rule validation. Hence rule facts represent checkings to verify for the concurrent testing runtime. JARL specifies two different kinds of possible assertions: checkpoint counting and checkpoint precedence.

### Checkpoint counting

Checkpoint counting facts state that some checkpoint must happen a certain number of times during the program execution. The full syntax for a checkpoint `f(x)` would be: 

```f(x) must happen [ <N> | at least <N> | at most <N> ] times ```

Examples:

```semaphore_acquire(sem_id) must happen at most 5 times```

```consume_item() must happen 10 times```

```message_recieve(msg) must happen at least 1 times```

Additionally, it is suggested (although not totally needed) that the following two extra options for `must happen` be present on any JARL parser:

- `must happen` as an alias of `must happen at least 1 times`
- `must not happen` as an alias of `must happen 0 times`

### Checkpoint precedence

Checkpoint precedence facts expose an order relationship between two checkpoints, in the sense they express that a checkpoint must happen before or after another one. The full syntax for two checkpoints `f(x)` and `g(y)` would be:

```f(x) must [ precede | follow ] g(y)```

Examples:

```produce(item) must precede consume(item)```

```lock_release(lock_id) must follow lock_acquire(lock_id)```

Although it is clear which checkpoint comes before or after the other on both cases, it truly is important to note the logic difference between the `precede` and the `follow` words.

Let `T(X)` be the time when checkpoint `X` happens during the execution of a concurrent program. Then:

- `X must precede Y` is _true_ iff `T(X)` < `T(Y)` or `Y` does not happen when `X` does.
- `X must follow Y` is _false_ iff `T(X)` < `T(Y)` or `X` does not happen when `Y` does.

### Argument matching with iterators



### Argument matching with wildcards

### Imposing argument conditions (filtering)

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

