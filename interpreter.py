"""Step 3: walk the AST and execute the program according to SimpleLang semantics."""
from errors import LangError
from parser import parse
from runtime import Environment, Function, ReturnValue

class Interpreter:
    # initialize the interpreter
    def __init__(self):
        self.output = []
        self.global_env = Environment() # top level, parent = None
        self.env = self.global_env      # current scope (as in line 22)
        self.steps = 0                  # count how many operations
        self.depth = 0                  # check how deep the nested chain of function is

    # guardrail against infinite loop, stops when there are more than 1,000 operations
    def tick(self):
        self.steps += 1
        if self.steps > 1000:           # reduce to 1,000 from original 100,000
            raise LangError('Execution stopped: step limit exceeded')

    # run statements, make sure current scope is switched correctly
    def block(self, statements, env):
        previous = self.env
        self.env = env
        try:
            for statement in statements:    # run nested statements 
                self.execute(statement)
        finally:                        # the following code block always runs even when crash
            self.env = previous         # restore scope active before previous block

    # execute statement
    def execute(self, node):
        self.tick()         # start counting operations
        kind = node[0]      # ast node tag, decides which branch below runs, reference from parser.py
        if kind == 'program':
            for item in node[1]:
                self.execute(item)
        elif kind == 'block':
            self.block(node[1], Environment(self.env))      # run block's statement inside nested scope
        elif kind == 'let':
            self.env.define(node[1], self.eval(node[2]))        # assignment
        elif kind == 'func':
            self.env.define(node[1], Function(node[2], node[3], self.env))      # take params at node[2], body at node[3], self.env as scope, store under node[1] name
        elif kind == 'print':
            value = self.eval(node[1])
            self.output.append('true' if value is True else 'false' if value is False else 'null' if value is None else str(value))     # print the output, T/F/None/actual value
        elif kind == 'expr':
            self.eval(node[1])  # compute the expression and ignore the result
        elif kind == 'if':
            branch = node[2] if self.eval(node[1]) else node[3]
            if branch is not None:      # run following statement if truthy
                self.execute(branch)
        elif kind == 'while':
            while self.eval(node[1]):       # node[1]: condition
                self.tick()
                self.execute(node[2])       # node[2]: statement
        elif kind == 'return':
            if self.depth == 0:             # depth=0 : not inside any function call
                raise LangError('return outside function')
            raise ReturnValue(self.eval(node[1]) if node[1] is not None else None)
        else:
            raise LangError(f'Unknown statement: {kind}')

    def eval(self, node):
        self.tick()
        kind = node[0]      # first tag in ast node, reference from parser.py

        if kind == 'literal':
            return node[1]          # return literal value
        if kind == 'variable':
            return self.env.get(node[1])        # retrieve variable value from dictionary
        if kind == 'assign':                                        # reassginment doesn't use 'let'
            return self.env.assign(node[1], self.eval(node[2]))     # assign node[2] value to node[1]
        if kind == 'unary':
            value = self.eval(node[2])          # node[2] is a variable/literal/expression
            if node[1] == '!':      # check for ! or -
                return not bool(value)      # return logical NOT, convert to bool then flip
            if type(value) not in (int, float):
                raise LangError('Unary minus requires a number')
            return -value           # return negated value
        # conduct all binary operations
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
        if kind == 'call':                              # reference call function in parser.py
            function = self.eval(node[1])               # retrieve expression
            args = [self.eval(a) for a in node[2]]      # retrieve all arguments
            if not isinstance(function, Function):      # check if function object belongs to Function class
                raise LangError('Only functions can be called')
            if len(args) != len(function.params):       # compare number of params vs args
                raise LangError('Incorrect number of function arguments')
            if self.depth >= 100:           # more than 100 nested functions specifically, not loop
                raise LangError('Recursion depth limit exceeded')
            local = Environment(function.closure)       # create new, empty scope
            for name, value in zip(function.params, args):      # pair parameters with arguments
                local.define(name, value)               # define variable, reference runtime.py
            self.depth += 1                             # increase call function depth by 1, depth != number of operations
            try:
                try:
                    self.block(function.body[1], local)     # run the function body locally
                except ReturnValue as result:
                    return result.value             
                return None
            finally:
                self.depth -= 1                         # decrement after function is ended

        raise LangError(f'Unknown expression: {kind}')  # raise error for unknown tag

def run(source):
    ast = parse(source)             # parse source to ast
    interpreter = Interpreter()     # create an interpreter
    interpreter.execute(ast)        # execute ast
    return {'ast': ast, 'output': '\n'.join(interpreter.output)}       # return ast, output of interpreter