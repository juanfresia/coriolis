import sys
from antlr4 import *
from .JarlLexer import JarlLexer
from .JarlParser import JarlParser
from .JarlActualListener import JarlListener

def parse_stream(input):
    """ Uses JarlLexer and JarlParser to parse an input stream.
    Returns a list of JarlRues"""

    lexer = JarlLexer(input)
    stream = CommonTokenStream(lexer)
    parser = JarlParser(stream)
    tree = parser.jarl()
    
    Jarl = JarlListener()
    walker = ParseTreeWalker()
    walker.walk(Jarl, tree)

    return Jarl.rules

def parse_file(filepath):
    input = FileStream(filepath)
    return parse_stream(input)

def parse_str(s):
    input = InputStream(s)
    return parse_stream(input)


def main(argv):
    rules = parse_file(argv[1])
    for rule in Jarl.rules:
        lines = [line for line in rule.text.splitlines() if line]
        for line in lines:
            print(line)
        # print(rule)
        # print("Is last condition litaral? ->", rule.scope.filter.conditions[0].is_literal)
        print()
        rule.scope.toSteps()
        print()
        print()

        
if __name__ == '__main__':
    main(sys.argv)
