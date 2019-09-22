import sys
from antlr4 import *
from JarlLexer import JarlLexer
from JarlParser import JarlParser
from JarlActualListener import JarlListener

def main(argv):
    input = FileStream(argv[1])
    lexer = JarlLexer(input)
    stream = CommonTokenStream(lexer)
    parser = JarlParser(stream)
    tree = parser.jarl()
    
    Jarl = JarlListener()
    walker = ParseTreeWalker()
    walker.walk(Jarl, tree)

    for rule in Jarl.rules:
        print(rule.text)
        print(rule)
        print("Is last condition litaral? ->", rule.scope.filter.conditions[-1].is_literal)
        print()
        print()

        
if __name__ == '__main__':
    main(sys.argv)
