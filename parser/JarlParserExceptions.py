
class JarlRuleValidationError(Exception):
    pass

class JarlIteratorAlreadyDefined(JarlRuleValidationError):
    pass

class JarlIteratorUndefined(JarlRuleValidationError):
    pass
