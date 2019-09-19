# Generated from Jarl.g4 by ANTLR 4.7.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .JarlParser import JarlParser
else:
    from JarlParser import JarlParser

# This class defines a complete listener for a parse tree produced by JarlParser.
class JarlActualListener(ParseTreeListener):

    # Enter a parse tree produced by JarlParser#jarl.
    def enterJarl(self, ctx:JarlParser.JarlContext):
        pass

    # Exit a parse tree produced by JarlParser#jarl.
    def exitJarl(self, ctx:JarlParser.JarlContext):
        pass


    # Enter a parse tree produced by JarlParser#line.
    def enterLine(self, ctx:JarlParser.LineContext):
        pass

    # Exit a parse tree produced by JarlParser#line.
    def exitLine(self, ctx:JarlParser.LineContext):
        pass


    # Enter a parse tree produced by JarlParser#condition.
    def enterCondition(self, ctx:JarlParser.ConditionContext):
        pass

    # Exit a parse tree produced by JarlParser#condition.
    def exitCondition(self, ctx:JarlParser.ConditionContext):
        pass


    # Enter a parse tree produced by JarlParser#filter_argument.
    def enterFilter_argument(self, ctx:JarlParser.Filter_argumentContext):
        pass

    # Exit a parse tree produced by JarlParser#filter_argument.
    def exitFilter_argument(self, ctx:JarlParser.Filter_argumentContext):
        pass


    # Enter a parse tree produced by JarlParser#filter_argument_list.
    def enterFilter_argument_list(self, ctx:JarlParser.Filter_argument_listContext):
        pass

    # Exit a parse tree produced by JarlParser#filter_argument_list.
    def exitFilter_argument_list(self, ctx:JarlParser.Filter_argument_listContext):
        pass


    # Enter a parse tree produced by JarlParser#identifier_list.
    def enterIdentifier_list(self, ctx:JarlParser.Identifier_listContext):
        pass

    # Exit a parse tree produced by JarlParser#identifier_list.
    def exitIdentifier_list(self, ctx:JarlParser.Identifier_listContext):
        pass


    # Enter a parse tree produced by JarlParser#filter1.
    def enterFilter1(self, ctx:JarlParser.Filter1Context):
        pass

    # Exit a parse tree produced by JarlParser#filter1.
    def exitFilter1(self, ctx:JarlParser.Filter1Context):
        pass


    # Enter a parse tree produced by JarlParser#selector.
    def enterSelector(self, ctx:JarlParser.SelectorContext):
        print("Found a selector rule!")
        print("Quantifier is: {}".format(ctx.QUANTIFIER()[0].getText()))
        print("Arguments are: {}".format([arg.getText() for arg in ctx.identifier_list(0).IDENTIFIER()]))
        pass

    # Exit a parse tree produced by JarlParser#selector.
    def exitSelector(self, ctx:JarlParser.SelectorContext):
        pass


    # Enter a parse tree produced by JarlParser#arguments.
    def enterArguments(self, ctx:JarlParser.ArgumentsContext):
        pass

    # Exit a parse tree produced by JarlParser#arguments.
    def exitArguments(self, ctx:JarlParser.ArgumentsContext):
        pass


    # Enter a parse tree produced by JarlParser#checkpoint.
    def enterCheckpoint(self, ctx:JarlParser.CheckpointContext):
        pass

    # Exit a parse tree produced by JarlParser#checkpoint.
    def exitCheckpoint(self, ctx:JarlParser.CheckpointContext):
        pass


    # Enter a parse tree produced by JarlParser#after_clause.
    def enterAfter_clause(self, ctx:JarlParser.After_clauseContext):
        pass

    # Exit a parse tree produced by JarlParser#after_clause.
    def exitAfter_clause(self, ctx:JarlParser.After_clauseContext):
        pass


