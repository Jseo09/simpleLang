"""Step 1: turn SimpleLang source text into tokens."""
from dataclasses import dataclass
import re
from errors import LangError

# dataclass helps create object with accessed name attributes (token.kind, token.value) without indexing (token[0], token[1])
@dataclass
# 1 token has 4 properties
class Token:
    kind: str
    text: str
    value: object
    line: int

# take regex pattern, compile to object then store in PATTERN
# it has 7 named groups
PATTERN = re.compile(
    r'(?P<SPACE>\s+)|'
    r'(?P<COMMENT>//[^\n]*)|'
    r'(?P<NUMBER>\d+(?:\.\d+)?)|'
    r'(?P<STRING>"(?:\\.|[^"\\])*")|'
    r'(?P<IDENT>[A-Za-z_]\w*)|'
    r'(?P<OP>==|!=|<=|>=|&&|\|\||[+*/%<>=!;(),{}-])|'
    r'(?P<INVALID>.)'
)

# Need more keywords? (not, break, continue, etc.)
KEYWORDS = {'let','if','else','while','func','return','print','true','false'}

# find matching regex, extract value, process, append to token, line by line
def tokenize(source):
    tokens = []
    line = 1

    for match in PATTERN.finditer(source):
        # pull info from regex
        kind = match.lastgroup      # SPACE, COMMENT, NUMBER, etc.
        text = match.group()        # the matched text

        # process token
        if kind == 'INVALID':
            # text!r = repr(text), shows the tokenized value
            raise LangError(f"Unexpected character {text!r} on line {line}")
        if kind not in ('SPACE', 'COMMENT'):
            if kind == 'IDENT' and text in KEYWORDS:
                kind = text
            if kind == 'OP':
                kind = text
            if kind == 'NUMBER':
                value = float(text) if '.' in text else int(text)
            elif kind == 'STRING':
                # Json strips off quote marks, make escape characters usable (convert \n, \t, \ into real characters)
                try:
                    import json
                    value = json.loads(text)
                except ValueError:
                    # from None separate error from previous error
                    raise LangError(f'Invalid string on line {line}') from None
            elif text == 'true':
                value = True
            elif text == 'false':
                value = False
            else:
                value = text

            # append token after processing
            tokens.append(Token(kind, text, value, line))
        line += text.count('\n')

    tokens.append(Token('EOF', '', None, line))
    return tokens