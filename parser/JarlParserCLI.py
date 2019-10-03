import sys
from antlr4 import *
from .JarlLexer import JarlLexer
from .JarlParser import JarlParser
from .JarlActualListener import JarlListener
from .JarlRuleValidator import validate_rule

def parse_stream(input, show_errors=True):
    """ Uses JarlLexer and JarlParser to parse an input stream.
    Returns a list of JarlRues"""

    lexer = JarlLexer(input)
    stream = CommonTokenStream(lexer)
    parser = JarlParser(stream)
    if not show_errors: parser.removeErrorListeners()
    tree = parser.jarl()
    
    Jarl = JarlListener()
    walker = ParseTreeWalker()
    walker.walk(Jarl, tree)

    for rule in Jarl.rules:
        validate_rule(rule)
    return Jarl.rules

def parse_file(filepath, show_errors=True):
    input = FileStream(filepath)
    return parse_stream(input, show_errors)

def parse_str(s, show_errors=True):
    input = InputStream(s)
    return parse_stream(input, show_errors)

def main(argv):
    rules = parse_file(argv[1])
    for rule in rules:
        lines = [line for line in rule.text.splitlines() if line]
        for line in lines:
            print(line)
        # print(rule)
        # print("Is last condition litaral? ->", rule.scope.filter.conditions[0].is_literal)
        print()
        print(rule)
        print()
        print()
        
if __name__ == '__main__':
    main(sys.argv)
