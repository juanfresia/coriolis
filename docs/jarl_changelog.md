# JARL Language Changelog

![](jarl_logo.png)



## 0.4.1

- `rule` header for simpler rule declarations.
- Definition of `with` keyword for argument filtering declarations.

## 0.4.0

- Argument matching and filtering (wildcards and iterators) at scope declarations.
- Removal of `must follow` and redefinition of `must precede` in favour of `after` and `before` scopes.
- Argument filtering in rule facts based on scope argument values.

## 0.3.0

- Definition of rule scope against rule fact.
- Definition of `after`, `before` and `previous` scopes.
- Definition of `next` and `previous` keywords for `between` scope.

## 0.2.0

- Removal of process type and ID in favour of checkpoints arguments.
- Definition of precedence with `must follow` keywords as a complement of `must precede`.
- Definition of suggested abbreviations: `must happen` as `must happen at least 1 times` and `must not happen` as `must happen 0 times`.

## 0.1.0

- Checkpoint functions definition based on process types.
- Iteration over processes via their process ID.
- Checkpoints precedence based on the `must precede` keywords. 
- Checkpoints counting based on the `must happen` keywords. 
- Iteration and wildcard matching of checkpoint functions arguments using `for every` and `for any`.
- Checkpoint arguments filtering with boolean conditions.
