import re
from pathlib import Path

import lark
from lark import Tree, Token
from lark.indenter import Indenter


class PythonIndenter(Indenter):
    NL_type = "_NEWLINE"
    OPEN_PAREN_types = ("LPAR", "LSQB", "LBRACE")
    CLOSE_PAREN_types = ("RPAR", "RSQB", "RBRACE")
    INDENT_type = "_INDENT"
    DEDENT_type = "_DEDENT"
    tab_len = 8

    def reset(self):
        self.indent_level = [0]
        self.paren_level = 0


class InsertEOF:
    token_type = "_END"

    def process(self, stream):
        token = None
        for token in stream:
            yield token
        if token is None:
            yield Token(self.token_type, "<EOF>")
        else:
            yield Token.new_borrow_pos(self.token_type, "<EOF>", token)

    @property
    def always_accept(self):
        return ()


class MultiPostLexer:
    def __init__(self, *postlexer):
        self.postlexer = postlexer

    def process(self, stream):
        for pl in self.postlexer:
            stream = pl.process(stream)
        yield from stream

    @property
    def always_accept(self):
        return tuple(t for pl in self.postlexer for t in pl.always_accept)


_indenter = PythonIndenter()
_parser = lark.Lark(open(Path(__file__).with_name('python.lark')).read(),
                    postlex=MultiPostLexer(InsertEOF(), _indenter), parser="lalr", start='file_input')


def decode_python_source(raw: bytes) -> str:
    if raw.startswith(b'\xEF\xBB\xBF'):
        print("BOM")
        coding = "utf-8"
        raw = raw[3:]
    else:
        coding = None
    for line in raw.split(b'\n', 2)[:2]:
        m = re.match(b'^[ \t\f]*#.*?coding[:=][ \t]*([-_.a-zA-Z0-9]+)', line)
        if m:
            assert coding is None or coding == m.group(1).decode('ascii')
            coding = m.group(1).decode('ascii')
            break
    if coding is None:
        coding = 'utf-8'
    return raw.decode(coding)


def parse(text: str) -> Tree:
    _indenter.reset()
    return _parser.parse(text)
