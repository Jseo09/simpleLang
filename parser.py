"""Step 2: convert a token stream into an abstract syntax tree (AST)."""
from errors import LangError
from lexer import tokenize


class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    def peek(self):
        return self.tokens[self.index]

    def take(self, *kinds):
        token = self.peek()
        if token.kind in kinds:
            self.index += 1
            return token
        return None

    def expect(self, kind):
        token = self.take(kind)
        if token is None:
            raise LangError(f"Expected {kind!r} on line {self.peek().line}, found {self.peek().text!r}")
        return token

    def parse(self):
        statements = []
        while self.peek().kind != 'EOF':
            statements.append(self.statement())
        return ('program', statements)

    def block(self):
        self.expect('{')
        statements = []
        while self.peek().kind not in ('}', 'EOF'):
            statements.append(self.statement())
        self.expect('}')
        return ('block', statements)

    def statement(self):
        if self.take('let'):
            name = self.expect('IDENT').text
            self.expect('=')
            expr = self.expression()
            self.expect(';')
            return ('let', name, expr)
        if self.take('func'):
            name = self.expect('IDENT').text
            self.expect('(')
            params = []
            if self.peek().kind != ')':
                params.append(self.expect('IDENT').text)
                while self.take(','):
                    params.append(self.expect('IDENT').text)
            self.expect(')')
            return ('func', name, params, self.block())
        if self.take('if'):
            self.expect('(')
            condition = self.expression()
            self.expect(')')
            yes = self.statement()
            no = self.statement() if self.take('else') else None
            return ('if', condition, yes, no)
        if self.take('while'):
            self.expect('(')
            condition = self.expression()
            self.expect(')')
            return ('while', condition, self.statement())
        if self.take('return'):
            value = None if self.peek().kind == ';' else self.expression()
            self.expect(';')
            return ('return', value)
        if self.take('print'):
            self.expect('(')
            value = self.expression()
            self.expect(')')
            self.expect(';')
            return ('print', value)
        if self.peek().kind == '{':
            return self.block()
        expr = self.expression()
        self.expect(';')
        return ('expr', expr)

    def expression(self):
        return self.assignment()

    def assignment(self):
        expr = self.logic_or()
        if self.take('='):
            if expr[0] != 'variable':
                raise LangError('Invalid assignment target')
            return ('assign', expr[1], self.assignment())
        return expr

    def binary(self, next_level, operators):
        expr = next_level()
        while self.peek().kind in operators:
            op = self.take(*operators).kind
            expr = ('binary', op, expr, next_level())
        return expr

    def logic_or(self):
        return self.binary(self.logic_and, ('||',))
    def logic_and(self):
        return self.binary(self.equality, ('&&',))
    def equality(self):
        return self.binary(self.comparison, ('==', '!='))
    def comparison(self):
        return self.binary(self.term, ('<', '<=', '>', '>='))
    def term(self):
        return self.binary(self.factor, ('+', '-'))
    def factor(self):
        return self.binary(self.unary, ('*', '/', '%'))

    def unary(self):
        token = self.take('!', '-')
        if token:
            return ('unary', token.kind, self.unary())
        return self.call()

    def call(self):
        expr = self.primary()
        while self.take('('):
            args = []
            if self.peek().kind != ')':
                args.append(self.expression())
                while self.take(','):
                    args.append(self.expression())
            self.expect(')')
            expr = ('call', expr, args)
        return expr

    def primary(self):
        token = self.take('NUMBER', 'STRING', 'true', 'false')
        if token:
            return ('literal', token.value)
        token = self.take('IDENT')
        if token:
            return ('variable', token.text)
        if self.take('('):
            expr = self.expression()
            self.expect(')')
            return expr
        raise LangError(f'Expected expression on line {self.peek().line}')

def parse(source):
    return Parser(tokenize(source)).parse()