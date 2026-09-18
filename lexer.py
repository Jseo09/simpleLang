"""Step 1: turn SimpleLang source text into tokens."""
from dataclasses import dataclass
import re

from errors import LangError


@dataclass
class Token:
    kind: str
    text: str
    value: object
    line: int

PATTERN = re.compile(r'(?P<SPACE>\s+)|(?P<COMMENT>//[^\n]*)|(?P<NUMBER>\d+(?:\.\d+)?)|(?P<STRING>"(?:\\.|[^"\\])*")|(?P<IDENT>[A-Za-z_]\w*)|(?P<OP>==|!=|<=|>=|&&|\|\||[+*/%<>=!;(),{}-])|(?P<INVALID>.)')
KEYWORDS = {'let','if','else','while','func','return','print','true','false'}

def tokenize(source):
    tokens = []
    line = 1
    for match in PATTERN.finditer(source):
        kind, text = match.lastgroup, match.group()
        if kind == 'INVALID':
            raise LangError(f"Unexpected character {text!r} on line {line}")
        if kind not in ('SPACE', 'COMMENT'):
            if kind == 'IDENT' and text in KEYWORDS:
                kind = text
            if kind == 'OP':
                kind = text
            if kind == 'NUMBER':
                value = float(text) if '.' in text else int(text)
            elif kind == 'STRING':
                try:
                    import json
                    value = json.loads(text)
                except ValueError:
                    raise LangError(f'Invalid string on line {line}') from None
            elif text == 'true':
                value = True
            elif text == 'false':
                value = False
            else:
                value = text
            tokens.append(Token(kind, text, value, line))
        line += text.count('\n')
    tokens.append(Token('EOF', '', None, line))
    return tokens
