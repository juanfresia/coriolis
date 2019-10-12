# Generated from Jarl.g4 by ANTLR 4.7.1
from antlr4 import *
if __name__ is not None and "." in __name__:
    from .JarlParser import JarlParser
else:
    from JarlParser import JarlParser

from .jarl_rule import *
from .jarl_parser_exceptions import *

# This class defines a complete listener for a parse tree produced by JarlParser.
class JarlListener(ParseTreeListener):
    def __init__(self):
        # This will contains all the rules found.
        # At any point in the parsing, rules[-1] refers to the rule being parsed
        self.rules = []

        # This variable will contain the current scope and fact being parsed
        # TODO(juanfresia): using lists may be an overkill. Maybe use simple variables?
        self.scopes = []
        self.facts = []

        self.filters = []

        # This stack will contain any unprocessed items, which are waiting for a
        # parent expression to grab them when it exits.
        # Example: during the processing of 'for any e and every b' (FilterExpr)
        #          it may contain the Identifier a, but not yet the Identifier b
        #          when all the identifiers and conditions are parsed, the exit
        #          filter will grab them all.
        self.stack = []


    # Enter a parse tree produced by JarlParser#jarl_rule.
    def enterJarl_rule(self, ctx:JarlParser.Jarl_ruleContext):
        start = ctx.start.start
        stop = ctx.stop.stop
        text = ctx.start.getInputStream().getText(start, stop)
        self.rules.append(JarlRule(text=text))

    # Exit a parse tree produced by JarlParser#jarl_rule.
    def exitJarl_rule(self, ctx:JarlParser.Jarl_ruleContext):
        if self.scopes:
            self.rules[-1].scope = self.scopes.pop()
        self.rules[-1].fact = self.facts.pop()

    # Enter a parse tree produced by JarlParser#rule_header.
    def enterRule_header(self, ctx:JarlParser.Rule_headerContext):
        ruleName = ctx.header_expr().IDENTIFIER().getText()
        self.rules[-1].name = ruleName


    # Enter a parse tree produced by JarlParser#rule_scope.
    def enterRule_scope(self, ctx:JarlParser.Rule_scopeContext):
        self.scopes.append(JarlRuleScope())

    # Exit a parse tree produced by JarlParser#rule_scope.
    def exitRule_scope(self, ctx:JarlParser.Rule_scopeContext):
        if len(self.filters) > 1:
            raise Exception("Scope should only have one filter")

        if self.filters:
            self.scopes[-1].filter = self.filters.pop()


    # Enter a parse tree produced by JarlParser#rule_fact.
    def enterRule_fact(self, ctx:JarlParser.Rule_factContext):
        self.facts.append(JarlRuleFact())

    # Exit a parse tree produced by JarlParser#rule_fact.
    def exitRule_fact(self, ctx:JarlParser.Rule_factContext):
        if len(self.filters) > 1:
            raise Exception("Scope should only have one filter")
        if self.filters:
            self.facts[-1].filter = self.filters.pop()

    # Exit a parse tree produced by JarlParser#selector_expr.
    def exitSelector_expr(self, ctx:JarlParser.Selector_exprContext):
        self.scopes[-1].selector = self.stack.pop()

    # Enter a parse tree produced by JarlParser#filter_expr.
    def enterFilter_expr(self, ctx:JarlParser.Filter_exprContext):
        self.filters.append(JarlFilterExpr())

    # Exit a parse tree produced by JarlParser#filter_expr.
    def exitFilter_expr(self, ctx:JarlParser.Filter_exprContext):
        while self.stack:
            self.filters[-1].add(self.stack.pop())

    # Enter a parse tree produced by JarlParser#quantifier_clause.
    def enterQuantifier_clause(self, ctx:JarlParser.Quantifier_clauseContext):
        if ctx.quantifier().ANY():
            type = JarlFilterClauseType.ANY
        else:
            type = JarlFilterClauseType.EVERY
        identifiers = [i.getText() for i in ctx.identifier_list().IDENTIFIER()]
        self.stack.append(JarlQuantifierClause(type, identifiers))

    # Enter a parse tree produced by JarlParser#with_clause.
    def enterWith_clause(self, ctx:JarlParser.With_clauseContext):
        conditions = []
        for i in ctx.condition_list().condition():
            l = i.IDENTIFIER()[0].getText()
            c = JarlComparator(i.COMPARATOR().getText())
            if i.literal():
                literal = True
                # If literal is a string, remove single quotes
                if i.literal().LITERAL_STR():
                    r = i.literal().LITERAL_STR().getText().strip("'")
                else:
                    # Literal is a number
                    # TODO: support other type of numbers
                    r = int(i.literal().NUMBER().getText())
            else:
                r = i.IDENTIFIER()[1].getText()
                literal = False
            conditions.append(JarlWithCondition(l, c, r, literal))

        self.stack.append(JarlWithClause(conditions))

    # Enter a parse tree produced by JarlParser#after_clause.
    def enterAfter_clause(self, ctx:JarlParser.After_clauseContext):
        chk_name = ctx.checkpoint().IDENTIFIER().getText()
        chk_args_list = ctx.checkpoint().arguments().identifier_list().IDENTIFIER()
        chk_args = [arg.getText() for arg in chk_args_list]
        start = JarlCheckpoint(chk_name, chk_args)

        sel_expr = JarlSelectorExpr(JarlSelectorClauseType.AFTER, start=start)
        self.stack.append(sel_expr)

    # Enter a parse tree produced by JarlParser#before_clause.
    def enterBefore_clause(self, ctx:JarlParser.Before_clauseContext):
        chk_name = ctx.checkpoint().IDENTIFIER().getText()
        chk_args_list = ctx.checkpoint().arguments().identifier_list().IDENTIFIER()
        chk_args = [arg.getText() for arg in chk_args_list]
        end = JarlCheckpoint(chk_name, chk_args)

        sel_expr = JarlSelectorExpr(JarlSelectorClauseType.BEFORE, end=end)
        self.stack.append(sel_expr)

    # Enter a parse tree produced by JarlParser#between_clause.
    def enterBetween_clause(self, ctx:JarlParser.Between_clauseContext):
        chk1_name = ctx.checkpoint()[0].IDENTIFIER().getText()
        chk1_args_list = ctx.checkpoint()[0].arguments().identifier_list().IDENTIFIER()
        chk1_args = [arg.getText() for arg in chk1_args_list]
        chk1 = JarlCheckpoint(chk1_name, chk1_args)

        chk2_name = ctx.checkpoint()[1].IDENTIFIER().getText()
        chk2_args_list = ctx.checkpoint()[1].arguments().identifier_list().IDENTIFIER()
        chk2_args = [arg.getText() for arg in chk2_args_list]
        chk2 = JarlCheckpoint(chk2_name, chk2_args)

        start = chk1
        end = chk2
        type = JarlSelectorClauseType.BETWEEN_NEXT
        # If between has a previous, we need to reverse the order
        if ctx.PREVIOUS():
            type = JarlSelectorClauseType.BETWEEN_PREV

        sel_expr = JarlSelectorExpr(type, start, end)
        self.stack.append(sel_expr)

    # Exit a parse tree produced by JarlParser#fact_clause.
    def exitFact_clause(self, ctx:JarlParser.Fact_clauseContext):
        chk_name = ctx.checkpoint().IDENTIFIER().getText()
        chk_args_list = ctx.checkpoint().arguments().identifier_list().IDENTIFIER()
        chk_args = [arg.getText() for arg in chk_args_list]
        chk = JarlCheckpoint(chk_name, chk_args)

        # It is guaranteed that the stack only contains a single requirement
        req = self.stack.pop()

        fact_clause = JarlRuleFactClause(chk, req)
        self.facts[-1].facts.append(fact_clause)
        pass

    # Enter a parse tree produced by JarlParser#requirement_count.
    def enterRequirement_count(self, ctx:JarlParser.Requirement_countContext):
        req = JarlRuleFactRequirementCount()

        negated = ctx.NOT()

        ## If hoy_many is not specified, we leave default values '=' and 1
        if ctx.how_many():
            if ctx.how_many().MOST():
                # AT MOST means less or equal than
                req.type = JarlComparator.GT if negated else JarlComparator.LE
            elif ctx.how_many().LEAST():
                # AT LEAST means greater or equal than
                req.type = JarlComparator.LT if negated else JarlComparator.GE
            else:
                req.type = JarlComparator.NE if negated else JarlComparator.EQ
            req.count = int(ctx.how_many().NUMBER().getText())
        else:
            ## There is not a count, then the comparator should be JarlComparator.GE
            ## If a must happen is negated, then it means JarlComparator.EQ 0
            if negated:
                req.type = JarlComparator.EQ
                req.count = 0
            else:
                req.type = JarlComparator.GE
                req.count = 1

        self.stack.append(req)

    # Enter a parse tree produced by JarlParser#requirement_order.
    def enterRequirement_order(self, ctx:JarlParser.Requirement_orderContext):

        chk_name = ctx.checkpoint().IDENTIFIER().getText()
        chk_args_list = ctx.checkpoint().arguments().identifier_list().IDENTIFIER()
        chk_args = [arg.getText() for arg in chk_args_list]

        req = JarlRuleFactRequirementOrder(JarlCheckpoint(chk_name, chk_args))

        if ctx.NOT():
            raise JarlNegatedOrderRequirement()

        self.stack.append(req)

