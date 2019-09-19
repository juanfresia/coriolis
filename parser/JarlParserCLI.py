import sys
from antlr4 import *
from JarlLexer import JarlLexer
from JarlParser import JarlParser
from JarlActualListener import JarlActualListener

def main(argv):
    input = FileStream(argv[1])
    lexer = JarlLexer(input)
    stream = CommonTokenStream(lexer)
    parser = JarlParser(stream)
    tree = parser.jarl()
    
    Jarl = JarlActualListener()
    walker = ParseTreeWalker()
    walker.walk(Jarl, tree)
        
if __name__ == '__main__':
    main(sys.argv)
