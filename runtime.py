"""Runtime data structures: nested variable scopes, functions, and returns."""
from errors import LangError


class Environment:
    def __init__(self, parent=None):
        self.values, self.parent = {}, parent

    def define(self, name, value):
        if name in self.values:
            raise LangError(f'Already defined in this scope: {name}')
        self.values[name] = value

    def get(self, name):
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        raise LangError(f'Undefined variable: {name}')

    def assign(self, name, value):
        if name in self.values:
            self.values[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            raise LangError(f'Undefined variable: {name}')
        return value

class ReturnValue(Exception):
    def __init__(self, value):
        self.value = value

class Function:
    def __init__(self, params, body, closure):
        self.params, self.body, self.closure = params, body, closure
