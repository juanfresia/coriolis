from antlr4 import *
from .JarlLexer import JarlLexer
from .JarlParser import JarlParser
from .jarl_actual_listener import JarlListener
from .jarl_rule_validator import JarlRuleValidator
from .jarl_rule_adapter import JarlRuleAdapter
from .parser_printer import ParserPrinter
import io
from contextlib import redirect_stderr


def parse_stream(input, verbose=False):
    """ Uses JarlLexer and JarlParser to parse an input stream.
    Returns a list of JarlRules"""

    lexer = JarlLexer(input)
    stream = CommonTokenStream(lexer)
    stream_parser = JarlParser(stream)
    parser_printer = ParserPrinter(verbose)

    f = io.StringIO()
    with redirect_stderr(f):
        tree = stream_parser.jarl()
        Jarl = JarlListener()
        walker = ParseTreeWalker()
        try:
            walker.walk(Jarl, tree)
        except Exception as e:
            pass

    error_lines = f.getvalue().split("\n")
    error_lines.remove("")
    parser_printer.print_checking_syntax(error_lines)
    if len(error_lines) > 0:
        return []

    all_valid = True
    for rule in Jarl.rules:
        try:
            JarlRuleValidator().validate_rule(rule)
            parser_printer.print_parsing_rule(rule)
        except Exception as e:
            parser_printer.print_parsing_rule(rule, e)
            all_valid = False

    return Jarl.rules if all_valid else []


def parse_file(filepath, verbose=False):
    input = FileStream(filepath)
    return parse_stream(input, verbose)


def parse_str(string, verbose=False):
    input = InputStream(string)
    return parse_stream(input, verbose)


def rules_to_steps(rules):
    adapted_rules = []
    for rule in rules:
        adapted_rule = JarlRuleAdapter().rule_to_steps(rule)
        adapted_rules.append(adapted_rule)

    return adapted_rules


def adapt_file(filepath, verbose=False):
    parser_printer = ParserPrinter(verbose)
    try:
        parser_printer.print_parser_summary(filepath)
        rules = parse_file(filepath, verbose)
    except Exception as e:
        parser_printer.print_error("{}".format(e))
        return []
    return rules_to_steps(rules)


def adapt_str(string, verbose=False):
    rules = parse_str(string, verbose)
    return rules_to_steps(rules)


def run_parser(args):
    rules = adapt_file(args.rules, args.verbose)
    #print("all_rules = [")
    # for rule in rules:
    #    print("\t{},\n".format(str(rule).replace("\n", "\n\t")))
    # print("]")
