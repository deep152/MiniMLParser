"""
Lexer and Parser for MiniML

This is the token class used by the parser and lexer
"""

class Token:
    # this initializes the token with its type, value, and pos in the source code
    def __init__(self, type, value, line, column):
        self.type = type # what kind of token (INT/LET/PLUS/ETC)
        self.value = value # the actual text (42/let/-)
        self.line = line # which line it appeared on
        self.column = column # which column it started at

    # this returns a readable string with the tokens details
    def __repr__(self):
        return f"Token({self.type}, {self.value!r}, line={self.line}, col={self.column})"
