"""Runtime data structures: nested variable scopes, functions, and returns."""
from errors import LangError

class Environment:
    # initialize attributes for variable
    def __init__(self, parent=None):
        self.values = {}    # use dictionary for O(1) lookup time
        self.parent = parent    #nested scoping (to access variable from outer scope)

    # define a variable
    def define(self, name, value):
        if name in self.values:
            raise LangError(f'Already defined in this scope: {name}')       # already in dictionary
        self.values[name] = value   # assign value to variable, put it in a dictionary

    # retrieve the variable value
    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.parent:     # retrieve it from outer scope
            return self.parent.get(name)
        raise LangError(f'Undefined variable: {name}')

    # assignment
    def assign(self, name, value):
        if name in self.values:     # assign new value
            self.values[name] = value
        elif self.parent:       # assign to variable in outer scope
            self.parent.assign(name, value)
        else:
            raise LangError(f'Undefined variable: {name}')
        return value

# return value itself
class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

# user-defined function
class Function:
    def __init__(self, params, body, closure):
        self.params = params        # parameter names
        self.body = body            # function body
        self.closure = closure      # function scope where defined
