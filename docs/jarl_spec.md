# JARL Language Specification Guide

![](jarl_logo2.png)

## Abstract

JARL aims to define a "common language" for writing business level user-defined rules for concurrent programs. This specification guide covers the main aspects of the language, providing different useful examples for each topic.

## Table of contents

- [Execution checkpoints](#execution-checkpoints)
- [Rule statement](#rule-statement)
- [Rule fact](#rule-fact)
  - [Checkpoint counting](#checkpoint-counting)
  - [Checkpoint precedence](#checkpoint-precedence)
  - [Argument matching with iterators](#argument-matching-with-iterators)
  - [Argument matching with wildcards](#argument-matching-with-wildcards)
  - [Combining argument matchers](#combining-argument-matchers)
  - [Imposing argument conditions (filtering)](#imposing-argument-conditions-filtering)
- [Rule scope](#rule-scope)
  - [After scope](#after-scope)
  - [Before scope](#before-scope)
  - [Between scope](#between-scope)
  - [Argument matching in rule scopes](#argument-matching-in-rule-scopes)


## Execution checkpoints

With the purpose of defining easily readable and writable concurrent rules, JARL syntax imposes the existence of _checkpoints_ inside the program. Checkpoints are precisely defined points of the code which the underlying testing runtime will be available to trace. Essentially, checkpoints might be seen as ordinary functions, except they are really not implemented by the developer of the program but by the testing framework itself.

These checkpoints are meant to represent concrete events of the concurrent problem that users would like to trace while their program is running. For instance, in the producer-consumer problem, consumer processes should have a "consume" checkpoint in their codes, while producer processes should have a "produce" one. The true purpose of these checkpoints is, then, to be used as "control points" during the concurrent execution. 

The underlying testing runtime must be able to detect _when_ did these checkpoints happened and with _which argument values_. These argument values are fetched from the program execution (i.e. they match code variables) and allow definition of JARL rules matching some criteria. Currently, JARL supported argument types are `int`, `float`, `char` and `string` (with no whitespaces).

A program set of checkpoints and their respective arguments should be defined a priori, on a separate file in a sort of checkpoints table. A possible checkpoints table for the producer-consumer example could be like the following (lines with `#` are considered comments):

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

In order to extend previous rule facts in a generic manner, JARL supports argument matching via _iterators_ using the `for every` reserved words. The syntax is the following:

```
for every [iterator ...]:
<rule_fact>
```

The list of iterators implies the enclosed rule fact should be valid for every value that the specified arguments acquire during the program execution. 

Examples:

```
# Every message is written before read
for every msg:
write(msg) must precede read(msg)
```

```
# Every shared resource must be released
for every shmid:
shm_destroy(shmid) must happen 1 time
```

```
# m is called for every i,j combination
for every i, j:
m(i, j) must happen at least 2 times
```

In very concrete words, iterators define a grouping behaviour when matching the checkpoint arguments values. For instance, suppose that during a program execution with a rule defined like the last example `m` was called with the following `(i, j)` argument values: `(1,1), (1,2), (3,7), (1,1), (2,1), (1,2), (2,1), (2,8), (3,7)`. The rule fact (`m` being called) should then be validated inside of the 5 groups `(1,1), (1,2), (3,7), (2,1), (2,8)`, resulting in a failure since `(2,8)` was only called once.

### Argument matching with wildcards

In addition to checkpoints' argument matching with iterators, JARL language provides a different matching system using _wildcards_ via the `for any` reserved words. The syntax for this is:

```
for any [wildcard ...]:
<rule_fact>
```

The list of wildcards implies the enclosed rule fact should be valid for any value, resulting in a "matching everything" scheme.

Examples:

```
# 10 items are produced among all producers
for any item_id:
produce(item_id) must happen 10 times
```

```
# At most 5 processes wait on the semaphore
for any pid:
sem_wait(pid) must happen at most 5 times
```

```
# m is called 5 times
for any i, j:
m(i, j) must happen 5 times
```

Note that the grouping argument scheme for wildcard matching is completely different that with iterators: since the arguments can match anything, all function calls will fall inside the same group. Let us suppose that, during a program execution with a rule defined like the last example, `m` was called with the following `(i, j)` argument values: `(1,1), (1,2), (2,1), (1,2), (3,7), (3,8)`. The rule fact validation will then fail, since the `any i, j` matched 6 values (the `(1,2)` is counted twice!)

### Combining argument matchers

As it would be expected, JARL supports combining matching via iterators and wildcards with the reserved word `and`. The resulting syntax becomes then:

```
for every [iterator ...] and any [wildcard ...]:
<rule_fact>
```

Examples:

```
# All items are must have been produced before consumed
for every item_id and any cid, pid:
produce(pid, item_id) must precede consume(cid, item_id)
```

```
# All acquired locks are released
for every lock_id and any pid:
lock_release(lock_id, pid) must follow lock_acquire(lock_id, pid)
```

```
# 10 messages must be queued on every message queue
for every msqid and any msg:
msq_send(msqid, msg) must happen 10 times
```

```
# m is called at most once for every i
for every i and any j:
m(i, j) must happen at most 1 times
```

Of course, the grouping argument behaviour when combining wildcards and iterators is a mixture of both cases. This way, assume that during a program execution with a rule defined like the last example, `m` was called with the following `(i, j)` argument values: `(1,1), (2,2), (5,1), (3,7), (6,8)`. Hence, the rule fact will be validated in five groups, matching any value of `j` in every case. If a sixth call with `(1,2)` were to happen, the rule fact validation would then fail, because `(1,1)` and `(1,2)` fall on the same group defined by the `i` value.

### Imposing argument conditions (filtering)

In JARL, it is also possible to _filter_ wildcards and iterators argument values according to binary conditions. This filtering will affect the argument matching by imposing extra restrictions on the checkpoints' argument values. The following is a list of all supported conditions:

- Equal to: `=`
- Not equal to: `!=`
- Greater than: `>`
- Less than: `<`
- Greater than or equal to: `>=`
- Less than or equal to: `<=`

Comparisons can be made between iterators or wildcards, or against literal values, However, JARL does not currently support comparing a wildcard against an iterator. The following are examples of each of the possible scenarios that can thus be made:

- Comparison between wildcards:

```
# Smokers never take elements they already have
for any smoker_id, element_id=smoker_id:
smoker_take_element(smoker_id, element_id) must happen 0 times
```

- Comparison between iterators:

```
# Items are produced in order
for every i, j>i and any p:
produce(p, i) must precede produce(p, j)
```

- Comparison against literal values:

```
# Semaphore cannot have negative value
for every semid, k<0:
sem_create(semid, k) must happen 0 times
```

## Rule scope

The _scope_ of a rule statement specifies a time range, during the program execution, in which the rule should be valid. Since checkpoints are the main control points for the testing runtime, scopes are defined relatively to them (i.e. the rule should be valid between two checkpoint calls).

**Note**: If no scope for a rule is provided, the implicit scope taken is the whole program execution.

The syntax for the three JARL explicitly-defined scopes is specified in the following sections.

### After scope:

In an `after` scope, the rule must be valid since a call to a certain checkpoint and until the end of the execution. This checkpoint _is included_ inside the scope considered for the rule validation. The syntax of a complete rule with an `after` scope is:

```
after <checkpoint>:
<rule-fact>
```

Examples:

```
# Released resource cannot be accessed
after shm_destroy:
for any pid:
shm_read(pid) must happen 0 times
```

```
# At most 5 processes are awaken via notify
after notify_all:
for any pid:
process_awake(pid) must happen at most 5 times
```

In the case that the checkpoint inside the `after` scope is called more than once, the rule should be valid _after every call_ and until the end of the execution.

### Before scope:

In a `before` scope, the rule must be valid since the beginning of the program execution and until a call to some checkpoint. This checkpoint _is included_ inside the scope considered for the rule validation. The syntax of a complete rule with a `before` scope is:

```
before <checkpoint>:
<rule-fact>
```

Examples:

```
# Lock cannot be acquired if it was not yet created
before lock_create:
for any pid:
lock_acquire(pid) must happen 0 times
```

```
# At most 5 processes can wait on the semaphore
before sem_signal:
for any pid:
sem_waig(pid) must happen at most 5 times
```

In the case that the checkpoint inside the `before` scope is called more than once, the rule should be valid _before every call_ since the beginning of the execution.

### Between scope:

In a `between` scope, the rule must be valid between the callings of two certain checkpoints (that may or may not be different). These two checkpoints _are included_ inside the scope considered for the rule validation. The syntax of a complete rule with a `before` scope is:

```
between <checkpoint_1> and [ next | previous ] <checkpoint_2>:
<rule-fact>
```  

Examples:

```
# Lock should not be destroyed twice
between lock_destroy and previous lock_create:
lock_destroy must happen 1 times
```

```
# The items buffer size is 5
between produce and next consume:
produce must happen at most 5 times
```

**Note:** A `between` scope is necessarily defined by two checkpoint calls. Hence, if in the last example `consume` is not called after some `produce`, then those `produce` checkpoints will fall into no validation range and would be as if they did not exist for such rule.

### Argument matching in rule scopes

JARL supports argument matching inside scopes in the same way that with rule facts. Thus, any JARL rule can be written as:  

```
for every [iterator ...] and any [wildcard ...]:
<rule-scope>:
<rule_fact>
```

Examples: 

```
# Elements cannot be taken after smoking if agent does not wake again
for any smoker_id:
between smoker_smoke(smoker_id) and next agent_wake:
for any sid, element_id:
smoker_take_element(sid, element_id) must happen 0 times
```

```
# If a reader reads something, a writer wrote it
for every reader_id, buffer, msg:
before read_buffer(reader_id, buffer, msg):
for any b=buffer, m=msg, writer_id:
write_buffer(writer_id, b, m) must happen at least 1 times
```

```
# Locks must not be acquired after their destruction
for every lock_id:
after lock_destroy(lock_id):
for every lid=lock_id:
lock_acquire(lid) must happen 0 times
```

```
# At most 10 elements can enter inside the buffer
for any producer_id, cconsumer_id, i1, i2:
between every produce(producer_id, i1) and next consume(cconsumer_id, i2):
for any p, i:
produce(producer_id, i) must happen at most 10 times
```

```
# On every queue, messages are sent before received
for every msqid:
between msq_create(msqid) and next msq_destroy(msqid):
for every m=msqid and any msg_id:
msq_send(m, msg_id) must precede msq_receive(m, msg_id)
```