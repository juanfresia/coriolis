
class JarlRuleValidationError(Exception):
    pass

class JarlArgumentAlreadyDeclared(JarlRuleValidationError):
    def __init__(self, arg):
        self.arg = arg
        msg = "Argument \'{}\' is already declared".format(arg)
        super().__init__(msg)

class JarlArgumentAlreadyUsed(JarlRuleValidationError):
    def __init__(self, arg):
        self.arg = arg
        msg = "Argument \'{}\' is already used".format(arg)
        super().__init__(msg)

class JarlArgumentNotDeclared(JarlRuleValidationError):
    def __init__(self, arg):
        self.arg = arg
        msg = "Argument \'{}\' used but never declared".format(arg)
        super().__init__(msg)

class JarlConditionMixesArguments(JarlRuleValidationError):
    def __init__(self, arg1, arg2):
        self.arg1 = arg1
        self.arg2 = arg2
        msg = "Arguments \'{}\' and \'{}\' cannot be used in the same condition".format(arg1, arg2)
        super().__init__(msg)

