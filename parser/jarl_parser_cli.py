import sys
from antlr4 import *
from .JarlLexer import JarlLexer
from .JarlParser import JarlParser
from .jarl_actual_listener import JarlListener
from .jarl_rule_validator import JarlRuleValidator
from .jarl_rule_adapter import JarlRuleAdapter

def parse_stream(input, show_errors=True):
    """ Uses JarlLexer and JarlParser to parse an input stream.
    Returns a list of JarlRules"""

    lexer = JarlLexer(input)
    stream = CommonTokenStream(lexer)
    stream_parser = JarlParser(stream)
    if not show_errors: stream_parser.removeErrorListeners()
    tree = stream_parser.jarl()
    
    Jarl = JarlListener()
    walker = ParseTreeWalker()
    walker.walk(Jarl, tree)

    for rule in Jarl.rules:
        JarlRuleValidator().validate_rule(rule)
    return Jarl.rules

def parse_file(filepath, show_errors=True):
    input = FileStream(filepath)
    return parse_stream(input, show_errors)

def parse_str(string, show_errors=True):
    input = InputStream(string)
    return parse_stream(input, show_errors)

def rules_to_steps(rules):
    adapted_rules = []
    for rule in rules:
        adapted_rule = JarlRuleAdapter().rule_to_steps(rule)
        adapted_rules.append(adapted_rule)
        
    return adapted_rules

def adapt_file(filepath, show_errors=True):
    rules = parse_file(filepath)
    return rules_to_steps(rules)
    
def adapt_str(string, show_errors=True):
    rules = parse_str(string)
    return rules_to_steps(rules)

def main(argv):
    rules = adapt_file(argv[1])
    print("all_rules = [")
    for rule in rules:
        print("\t{},\n".format(str(rule).replace("\n", "\n\t")))
    print("]")
        
if __name__ == '__main__':
    main(sys.argv)
