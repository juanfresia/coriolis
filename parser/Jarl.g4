grammar Jarl;

/*
 * Parser Rules
 */

jarl                : line EOF ;

line                : selector | filter ;

condition           : (IDENTIFIER COMPARATOR IDENTIFIER) ;
filter_argument     : (IDENTIFIER | condition) ;
filter_argument_list : (filter_argument (',' filter_argument)*)? ;

identifier_list     : (IDENTIFIER (',' IDENTIFIER)*)? ;

filter              : after_clause ;

selector            : FOR QUANTIFIER identifier_list (AND QUANTIFIER identifier_list)* COLON NEWLINE ;

arguments           : '(' identifier_list ')' ;
checkpoint          : IDENTIFIER arguments ;

after_clause        : AFTER checkpoint COLON NEWLINE ;


/*
 * Lexer Rules
 */

/* Comparators */
 E : '=' ;
NE : '!=' ;
GT : '>' ;
GE : '>=' ;
LT : '<' ;
LE : '<=' ;

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
AFTER : 'after' ;

QUANTIFIER : (ANY | EVERY) ;

IDENTIFIER          : (LOWERCASE | UPPERCASE | '_') (DIGIT | LOWERCASE | UPPERCASE | '_')+ ;

COLON               : ':' ;

WHITESPACE            : (' ' | '\t')+ -> skip ;

NEWLINE                : ('\r'? '\n' | '\r')+ ;

