/*
 * JARL grammar v0.1
 */

grammar Jarl;

/*
 * Parser Rules
 */

jarl                 : jarl_rule* EOF ;
jarl_rule            : NEWLINE* rule_header rule_scope rule_fact NEWLINE*;

/* Rule parts */
rule_header     : header_expr ;
rule_scope      : filter_expr? selector_expr ;
rule_fact       : filter_expr? fact_expr ;

/* Rule expresions */
header_expr          : RULE IDENTIFIER NEWLINE ? ;
selector_expr        : ( after_clause | before_clause | between_clause )  COLON NEWLINE ?;
filter_expr          : FOR quantifier_clause (AND quantifier_clause)* (with_clause)? COLON NEWLINE? ;
fact_expr            : fact_clause (NEWLINE? fact_clause)* ;

/* Clauses */
quantifier_clause    : quantifier identifier_list ;
with_clause          : WITH condition_list ;
after_clause         : AFTER checkpoint ;
before_clause        : BEFORE checkpoint ;
between_clause       : BETWEEN checkpoint AND (NEXT | PREVIOUS) checkpoint ;
fact_clause          : checkpoint requirement ;

/* Auxiliar parser rules */
requirement          : ( requirement_count | requirement_order ) ;
requirement_count    : MUST NOT? HAPPEN (how_many)? ;
requirement_order    : MUST NOT? (FOLLOW | PRECEDE) checkpoint ;
how_many             : ((AT MOST) | (AT LEAST))? NUMBER TIMES ;

condition_list       : condition (',' condition)* ;
condition            : (IDENTIFIER COMPARATOR (IDENTIFIER | LITERAL)) ;

quantifier           : (ANY | EVERY) ;
arguments            : '(' identifier_list ')' ;
identifier_list      : (IDENTIFIER (',' IDENTIFIER)*)? ;
checkpoint           : IDENTIFIER arguments ;


/*
 * Lexer Rules
 */

/* Comparators */
fragment  E : '=' ;
fragment NE : '!=' ;
fragment GT : '>' ;
fragment GE : '>=' ;
fragment LT : '<' ;
fragment LE : '<=' ;

COMPARATOR : E | NE | GT | GE | LT | LE ;

/* Keywords */
AFTER    : 'after' ;
AND      : 'and' ;
ANY      : 'any' ;
AT       : 'at' ;
BEFORE   : 'before' ;
BETWEEN  : 'between' ;
EVERY    : 'every' ;
FOLLOW   : 'follow' ;
FOR      : 'for' ;
HAPPEN   : 'happen' ;
LEAST    : 'least' ;
MOST     : 'most' ;
MUST     : 'must' ;
NEXT     : 'next' ;
NOT      : 'not' ;
PRECEDE  : 'precede' ;
PREVIOUS : 'previous' ;
RULE     : 'rule' ;
TIMES    : 'times' ;
WITH     : 'with' ;

/* Identifiers and special characters */
fragment DIGIT      : [0-9] ;
fragment LOWERCASE  : [a-z] ;
fragment UPPERCASE  : [A-Z] ;

NUMBER      : DIGIT+ ;
IDENTIFIER  : (LOWERCASE | UPPERCASE | '_') (DIGIT | LOWERCASE | UPPERCASE | '_')* ;
COLON       : ':' ;
LITERAL     : '\'' (~'\'')* '\'' ;
WHITESPACE  : (' ' | '\t')+ -> skip ;
NEWLINE     : ('\r'? '\n' | '\r')+ ;

