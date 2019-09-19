grammar Jarl;

/*
 * Parser Rules
 */

jarl                 : jarl_rule* EOF ;
jarl_rule            : NEWLINE* header_expr filter_expr? selector_expr filter_expr? fact_expr NEWLINE*;

header_expr          : RULE IDENTIFIER NEWLINE ? ;
selector_expr        : ( after_clause | before_clause | between_clause )  COLON NEWLINE ?;
filter_expr          : FOR quantifier_clause (AND quantifier_clause)* (with_clause)? COLON NEWLINE? ;
fact_expr            : fact_clause (NEWLINE fact_clause)* ;

// Clauses
quantifier_clause    : QUANTIFIER identifier_list ;
with_clause          : WITH condition_list ;
after_clause         : AFTER checkpoint ;
before_clause        : BEFORE checkpoint ;
between_clause       : BETWEEN checkpoint AND (NEXT | PREVIOUS) checkpoint ;
fact_clause          : checkpoint requirement ;

// Auxiliar rules

requirement          : ( requirement_count | requirement_order ) ;
requirement_count    : MUST NOT? HAPPEN (NUMBER TIMES)? ;
requirement_order    : MUST NOT? (FOLLOW | PRECEDE) checkpoint ;

condition_list       : condition (',' condition)* ;
condition            : (IDENTIFIER COMPARATOR (IDENTIFIER | LITERAL)) ;

identifier_list      : (IDENTIFIER (',' IDENTIFIER)*)? ;
arguments           : '(' identifier_list ')' ;
checkpoint          : IDENTIFIER arguments ;



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

fragment DIGIT      : [0-9] ;
fragment LOWERCASE  : [a-z] ;
fragment UPPERCASE  : [A-Z] ;

/*
 * Keywords, only in lowercase
 */
AND : 'and' ;
FOR : 'for' ;
fragment ANY : 'any' ;
fragment EVERY : 'every' ;
WITH : 'with' ;
AFTER : 'after' ;
BEFORE : 'before' ;
BETWEEN : 'between' ;
NEXT : 'next' ;
PREVIOUS : 'previous' ;
MUST : 'must' ;
HAPPEN : 'happen' ;
NOT : 'not' ;
TIMES : 'times' ;
FOLLOW : 'follow' ;
PRECEDE : 'precede' ;
RULE : 'rule' ;

QUANTIFIER : (ANY | EVERY) ;

NUMBER              : DIGIT+ ;
IDENTIFIER          : (LOWERCASE | UPPERCASE | '_') (DIGIT | LOWERCASE | UPPERCASE | '_')* ;

COLON               : ':' ;

LITERAL             : '\'' (~'\'')* '\'' ;

WHITESPACE            : (' ' | '\t')+ -> skip ;

NEWLINE                : ('\r'? '\n' | '\r')+ ;

