"""Step 3: walk the AST and execute the program according to SimpleLang semantics."""
from errors import LangError
from parser import parse
from runtime import Environment, Function, ReturnValue


class Interpreter:
    def __init__(self):
        self.output = []
        self.global_env = Environment()
        self.env = self.global_env
        self.steps = 0
        self.depth = 0

    def tick(self):
        self.steps += 1
        if self.steps > 100000:
            raise LangError('Execution stopped: step limit exceeded')

    def block(self, statements, env):
        previous = self.env
        self.env = env
        try:
            for statement in statements:
                self.execute(statement)
        finally:
            self.env = previous

    def execute(self, node):
        self.tick()
        kind = node[0]
        if kind == 'program':
            for item in node[1]:
                self.execute(item)
        elif kind == 'block':
            self.block(node[1], Environment(self.env))
        elif kind == 'let':
            self.env.define(node[1], self.eval(node[2]))
        elif kind == 'func':
            self.env.define(node[1], Function(node[2], node[3], self.env))
        elif kind == 'print':
            value = self.eval(node[1])
            self.output.append('true' if value is True else 'false' if value is False else 'null' if value is None else str(value))
        elif kind == 'expr':
            self.eval(node[1])
        elif kind == 'if':
            branch = node[2] if self.eval(node[1]) else node[3]
            if branch is not None:
                self.execute(branch)
        elif kind == 'while':
            while self.eval(node[1]):
                self.tick()
                self.execute(node[2])
        elif kind == 'return':
            if self.depth == 0:
                raise LangError('return outside function')
            raise ReturnValue(self.eval(node[1]) if node[1] is not None else None)
        else:
            raise LangError(f'Unknown statement: {kind}')

    def eval(self, node):
        self.tick()
        kind = node[0]
        if kind == 'literal':
            return node[1]
        if kind == 'variable':
            return self.env.get(node[1])
        if kind == 'assign':
            return self.env.assign(node[1], self.eval(node[2]))
        if kind == 'unary':
            value = self.eval(node[2])
            if node[1] == '!':
                return not bool(value)
            if type(value) not in (int, float):
                raise LangError('Unary minus requires a number')
            return -value
        if kind == 'binary':
            op = node[1]
            left = self.eval(node[2])
            if op == '&&':
                return left if not left else self.eval(node[3])
            if op == '||':
                return left if left else self.eval(node[3])
            right = self.eval(node[3])
            if op in ('==','!='):
                equal = type(left) == type(right) and left == right
                return equal if op == '==' else not equal
            if op == '+' and (isinstance(left, str) or isinstance(right, str)):
                return str(left) + str(right)
            if type(left) not in (int, float) or type(right) not in (int, float):
                raise LangError(f'Operator {op} requires numeric operands')
            if op == '+': return left + right
            if op == '-': return left - right
            if op == '*': return left * right
            if op in ('/','%') and right == 0:
                raise LangError('Division by zero')
            if op == '/': return left / right
            if op == '%': return left % right
            if op == '<': return left < right
            if op == '<=': return left <= right
            if op == '>': return left > right
            if op == '>=': return left >= right
            raise LangError(f'Unknown operator: {op}')
        if kind == 'call':
            function = self.eval(node[1])
            args = [self.eval(a) for a in node[2]]
            if not isinstance(function, Function):
                raise LangError('Only functions can be called')
            if len(args) != len(function.params):
                raise LangError('Incorrect number of function arguments')
            if self.depth >= 100:
                raise LangError('Recursion depth limit exceeded')
            local = Environment(function.closure)
            for name, value in zip(function.params, args):
                local.define(name, value)
            self.depth += 1
            try:
                try:
                    self.block(function.body[1], local)
                except ReturnValue as result:
                    return result.value
                return None
            finally:
                self.depth -= 1
        raise LangError(f'Unknown expression: {kind}')

def run(source):
    ast = parse(source)
    interpreter = Interpreter()
    interpreter.execute(ast)
    return {'ast': ast, 'output': '\n'.join(interpreter.output)}
