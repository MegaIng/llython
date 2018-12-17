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
_parser = lark.Lark(open(Path(__file__).with_name('level0.lark')).read(),
                    parser="lalr", start='file_input')

print(_parser.parse(''))


def parse(text: str) -> Tree:
    _indenter.reset()
    return _parser.parse(text)
