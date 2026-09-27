"""
Lexer and Parser for MiniML

This is the main file, reads a .ml file and prints the AST
"""

import sys
from lexer import Lexer
from parser import Parser

# check that a valid file was passed in
if len(sys.argv) != 2:
    print("Error: please provide one ml file")
    sys.exit(1)

filename = sys.argv[1]

# try to open and read the file
try:
    with open(filename, 'r') as f:
        source = f.read()
except FileNotFoundError:
    print(f"Error: file '{filename}' not found")
    sys.exit(1)

# run the lexer and parser, print result or error
try:
    tokens = Lexer(source).tokenize()
    ast = Parser(tokens).parse()
    print(ast)
except SystemExit:
    sys.exit(1)