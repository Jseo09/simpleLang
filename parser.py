"""Step 2: convert a token stream into an abstract syntax tree (AST)."""
from errors import LangError
from lexer import tokenize


class Parser:

    # initialize token, cursor
    def __init__(self, tokens):
        self.tokens = tokens
        self.index = 0

    # look at token at current index without moving the cursor
    def peek(self):
        return self.tokens[self.index]

    # check if token is in kinds, else return None
    def take(self, *kinds):
        token = self.peek()
        if token.kind in kinds:
            self.index += 1
            return token
        return None

    # make sure token isn't None value
    def expect(self, kind):
        token = self.take(kind)
        if token is None:
            raise LangError(f"Expected {kind!r} on line {self.peek().line}, found {self.peek().text!r}")
        return token

    # keep parsing the statement till end of file and return the parsed value
    def parse(self):
        statements = []
        while self.peek().kind != 'EOF':
            statements.append(self.statement())
        return ('program', statements)

    # expect { then follows a statement, keep appending statement till end of file or } then output statement
    def block(self):
        self.expect('{')
        statements = []
        while self.peek().kind not in ('}', 'EOF'):
            statements.append(self.statement())
        self.expect('}')
        return ('block', statements)

    # check tokens against reserved words
    def statement(self):
        # let a = b;
        if self.take('let'):
            name = self.expect('IDENT').text
            self.expect('=')
            expr = self.expression()
            self.expect(';')
            return ('let', name, expr)

        # func name(param1, param2, ...)
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

        # no indentation/block for statement?
        """
        if (condition)
            statement   # run when true
        else
            statement   # run when false
        """
        if self.take('if'):
            self.expect('(')
            condition = self.expression()
            self.expect(')')
            yes = self.statement()
            no = self.statement() if self.take('else') else None
            return ('if', condition, yes, no)

        # no indentation/block for statement?
        """
        while (condition)
            statement
        """
        if self.take('while'):
            self.expect('(')
            condition = self.expression()
            self.expect(')')
            return ('while', condition, self.statement())

        # return; -> parsed value is None, else returns expression
        if self.take('return'):
            value = None if self.peek().kind == ';' else self.expression()
            self.expect(';')
            return ('return', value)

        # why does only print requires ';' at the end?
        # print(value/expression);
        if self.take('print'):
            self.expect('(')
            value = self.expression()
            self.expect(')')
            self.expect(';')
            return ('print', value)

        #  {statement};
        if self.peek().kind == '{':
            return self.block()
        expr = self.expression()
        self.expect(';')
        return ('expr', expr)

    # return the assignment
    def expression(self):
        return self.assignment()

    # assignment a=b=c, left side must be a variable
    def assignment(self):
        expr = self.logic_or()
        if self.take('='):
            if expr[0] != 'variable':
                raise LangError('Invalid assignment target')
            return ('assign', expr[1], self.assignment())
        return expr

    # build AST
    def binary(self, next_level, operators):
        expr = next_level()
        while self.peek().kind in operators:
            op = self.take(*operators).kind
            # build AST node for new found binary operation
            expr = ('binary', op, expr, next_level())
        return expr

    # logic, comparison, arithmetic operators
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

    # retrieve expression after ! or -
    def unary(self):
        token = self.take('!', '-')
        if token:
            return ('unary', token.kind, self.unary())      # recursion
        return self.call()

    # parse call function
    def call(self):
        expr = self.primary()   # return AST node
        while self.take('('):
            args = []
            if self.peek().kind != ')':
                args.append(self.expression())
                while self.take(','):
                    args.append(self.expression())
            self.expect(')')
            expr = ('call', expr, args)     # build AST node
        return expr

    # return parsed value type, raise error if no match
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

# tokenize the source, build ast
def parse(source):
    return Parser(tokenize(source)).parse()