# Generated from Jarl.g4 by ANTLR 4.7.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .JarlParser import JarlParser
else:
    from JarlParser import JarlParser

# This class defines a complete listener for a parse tree produced by JarlParser.


class JarlListener(ParseTreeListener):

    # Enter a parse tree produced by JarlParser#jarl.
    def enterJarl(self, ctx: JarlParser.JarlContext):
        pass

    # Exit a parse tree produced by JarlParser#jarl.
    def exitJarl(self, ctx: JarlParser.JarlContext):
        pass

    # Enter a parse tree produced by JarlParser#jarl_rule.
    def enterJarl_rule(self, ctx: JarlParser.Jarl_ruleContext):
        pass

    # Exit a parse tree produced by JarlParser#jarl_rule.
    def exitJarl_rule(self, ctx: JarlParser.Jarl_ruleContext):
        pass

    # Enter a parse tree produced by JarlParser#rule_header.
    def enterRule_header(self, ctx: JarlParser.Rule_headerContext):
        pass

    # Exit a parse tree produced by JarlParser#rule_header.
    def exitRule_header(self, ctx: JarlParser.Rule_headerContext):
        pass

    # Enter a parse tree produced by JarlParser#rule_scope.
    def enterRule_scope(self, ctx: JarlParser.Rule_scopeContext):
        pass

    # Exit a parse tree produced by JarlParser#rule_scope.
    def exitRule_scope(self, ctx: JarlParser.Rule_scopeContext):
        pass

    # Enter a parse tree produced by JarlParser#rule_fact.
    def enterRule_fact(self, ctx: JarlParser.Rule_factContext):
        pass

    # Exit a parse tree produced by JarlParser#rule_fact.
    def exitRule_fact(self, ctx: JarlParser.Rule_factContext):
        pass

    # Enter a parse tree produced by JarlParser#header_expr.
    def enterHeader_expr(self, ctx: JarlParser.Header_exprContext):
        pass

    # Exit a parse tree produced by JarlParser#header_expr.
    def exitHeader_expr(self, ctx: JarlParser.Header_exprContext):
        pass

    # Enter a parse tree produced by JarlParser#selector_expr.
    def enterSelector_expr(self, ctx: JarlParser.Selector_exprContext):
        pass

    # Exit a parse tree produced by JarlParser#selector_expr.
    def exitSelector_expr(self, ctx: JarlParser.Selector_exprContext):
        pass

    # Enter a parse tree produced by JarlParser#filter_expr.
    def enterFilter_expr(self, ctx: JarlParser.Filter_exprContext):
        pass

    # Exit a parse tree produced by JarlParser#filter_expr.
    def exitFilter_expr(self, ctx: JarlParser.Filter_exprContext):
        pass

    # Enter a parse tree produced by JarlParser#fact_expr.
    def enterFact_expr(self, ctx: JarlParser.Fact_exprContext):
        pass

    # Exit a parse tree produced by JarlParser#fact_expr.
    def exitFact_expr(self, ctx: JarlParser.Fact_exprContext):
        pass

    # Enter a parse tree produced by JarlParser#quantifier_clause.
    def enterQuantifier_clause(self, ctx: JarlParser.Quantifier_clauseContext):
        pass

    # Exit a parse tree produced by JarlParser#quantifier_clause.
    def exitQuantifier_clause(self, ctx: JarlParser.Quantifier_clauseContext):
        pass

    # Enter a parse tree produced by JarlParser#with_clause.
    def enterWith_clause(self, ctx: JarlParser.With_clauseContext):
        pass

    # Exit a parse tree produced by JarlParser#with_clause.
    def exitWith_clause(self, ctx: JarlParser.With_clauseContext):
        pass

    # Enter a parse tree produced by JarlParser#after_clause.
    def enterAfter_clause(self, ctx: JarlParser.After_clauseContext):
        pass

    # Exit a parse tree produced by JarlParser#after_clause.
    def exitAfter_clause(self, ctx: JarlParser.After_clauseContext):
        pass

    # Enter a parse tree produced by JarlParser#before_clause.
    def enterBefore_clause(self, ctx: JarlParser.Before_clauseContext):
        pass

    # Exit a parse tree produced by JarlParser#before_clause.
    def exitBefore_clause(self, ctx: JarlParser.Before_clauseContext):
        pass

    # Enter a parse tree produced by JarlParser#between_clause.
    def enterBetween_clause(self, ctx: JarlParser.Between_clauseContext):
        pass

    # Exit a parse tree produced by JarlParser#between_clause.
    def exitBetween_clause(self, ctx: JarlParser.Between_clauseContext):
        pass

    # Enter a parse tree produced by JarlParser#fact_clause.
    def enterFact_clause(self, ctx: JarlParser.Fact_clauseContext):
        pass

    # Exit a parse tree produced by JarlParser#fact_clause.
    def exitFact_clause(self, ctx: JarlParser.Fact_clauseContext):
        pass

    # Enter a parse tree produced by JarlParser#requirement.
    def enterRequirement(self, ctx: JarlParser.RequirementContext):
        pass

    # Exit a parse tree produced by JarlParser#requirement.
    def exitRequirement(self, ctx: JarlParser.RequirementContext):
        pass

    # Enter a parse tree produced by JarlParser#requirement_count.
    def enterRequirement_count(self, ctx: JarlParser.Requirement_countContext):
        pass

    # Exit a parse tree produced by JarlParser#requirement_count.
    def exitRequirement_count(self, ctx: JarlParser.Requirement_countContext):
        pass

    # Enter a parse tree produced by JarlParser#requirement_order.
    def enterRequirement_order(self, ctx: JarlParser.Requirement_orderContext):
        pass

    # Exit a parse tree produced by JarlParser#requirement_order.
    def exitRequirement_order(self, ctx: JarlParser.Requirement_orderContext):
        pass

    # Enter a parse tree produced by JarlParser#how_many.
    def enterHow_many(self, ctx: JarlParser.How_manyContext):
        pass

    # Exit a parse tree produced by JarlParser#how_many.
    def exitHow_many(self, ctx: JarlParser.How_manyContext):
        pass

    # Enter a parse tree produced by JarlParser#condition_list.
    def enterCondition_list(self, ctx: JarlParser.Condition_listContext):
        pass

    # Exit a parse tree produced by JarlParser#condition_list.
    def exitCondition_list(self, ctx: JarlParser.Condition_listContext):
        pass

    # Enter a parse tree produced by JarlParser#condition.
    def enterCondition(self, ctx: JarlParser.ConditionContext):
        pass

    # Exit a parse tree produced by JarlParser#condition.
    def exitCondition(self, ctx: JarlParser.ConditionContext):
        pass

    # Enter a parse tree produced by JarlParser#quantifier.
    def enterQuantifier(self, ctx: JarlParser.QuantifierContext):
        pass

    # Exit a parse tree produced by JarlParser#quantifier.
    def exitQuantifier(self, ctx: JarlParser.QuantifierContext):
        pass

    # Enter a parse tree produced by JarlParser#arguments.
    def enterArguments(self, ctx: JarlParser.ArgumentsContext):
        pass

    # Exit a parse tree produced by JarlParser#arguments.
    def exitArguments(self, ctx: JarlParser.ArgumentsContext):
        pass

    # Enter a parse tree produced by JarlParser#identifier_list.
    def enterIdentifier_list(self, ctx: JarlParser.Identifier_listContext):
        pass

    # Exit a parse tree produced by JarlParser#identifier_list.
    def exitIdentifier_list(self, ctx: JarlParser.Identifier_listContext):
        pass

    # Enter a parse tree produced by JarlParser#checkpoint.
    def enterCheckpoint(self, ctx: JarlParser.CheckpointContext):
        pass

    # Exit a parse tree produced by JarlParser#checkpoint.
    def exitCheckpoint(self, ctx: JarlParser.CheckpointContext):
        pass

    # Enter a parse tree produced by JarlParser#literal.
    def enterLiteral(self, ctx: JarlParser.LiteralContext):
        pass

    # Exit a parse tree produced by JarlParser#literal.
    def exitLiteral(self, ctx: JarlParser.LiteralContext):
        pass
