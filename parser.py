"""
Lexer and Parser for MiniML

This parser takes the token list from lexer and builds an AST
"""

from token import Token 
from ast_nodes import *

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    # look at current token, doesnt move position
    def current(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    # move forward and return the token that was just passed
    def go_next(self):
        token = self.current()
        # check that its not at end of list
        if token is not None:
            self.pos += 1
        return token

    # check if current token matches expected type
    def check(self, token_type):
        curr = self.current()
        if curr is None:
            return False
        return curr.type == token_type

    # checks if current token matches, take it else report a Syntax Error
    def expect(self, token_type):
        if self.check(token_type):
            return self.go_next()
        
        token = self.current()

        if token:
            print(f"Syntax Error at line {token.line}, column {token.column}: expected {token_type} but got {token.type}")
        else:
            print(f"Syntax Error: expected {token_type} but reached end of input")
        exit(1)
        
    # this handles the highest precedence items: 
    # Rule: primary_expr -> INT | BOOL | ID | ( expr ) 
    def parse_primary_expr(self):        
        # handle ints
        if self.check('INT'):
            token = self.go_next()
            return IntLiteral(int(token.value))
        
        # handle booleans
        elif self.check('BOOL'):
            token = self.go_next()
            return BoolLiteral(token.value == 'true')
        
        # handle variable names
        elif self.check('ID'):
            token = self.go_next()
            return Variable(token.value)
        
        # handle parentheses that come with expression
        elif self.check('LPAREN'):
            self.go_next()            
            expr = self.parse_expr() # jump back up to top level rule
            self.expect('RPAREN') # needs to have ending )
            return expr
        
        # if none of these match, its a syntax err
        else:
            token = self.current()
            if token:
                print(f"Syntax Error at line {token.line}, column {token.column}: unexpected token '{token.value}'")
            else:
                print("Syntax Error: unexpected end of input")
            exit(1)

    # this handles function applications. left-associative
    # Rule: app_expr -> primary_expr primary_expr*
    def parse_app_expr(self):
        # start with the first part (its either function or single literal)
        expr = self.parse_primary_expr()

        # as long as next token could be primary_expr, keep applying
        while self.check('INT') or self.check('BOOL') or self.check('ID') or self.check('LPAREN'):
            operand = self.parse_primary_expr()
            # put current expression in an app node with new operand
            expr = App(expr, operand)
            
        return expr
    
    # Rule: unary_expr -> (NOT | -) unary_expr | app_expr
    def parse_unary_expr(self):
        # handle not
        if self.check('NOT'):
            self.go_next()
            return UnaryOp('not', self.parse_unary_expr())
        
        # handle unary minus eg -x
        elif self.check('MINUS'):
            self.go_next()
            return UnaryOp('-', self.parse_unary_expr())
        # if nothing unary go to app
        else:
            return self.parse_app_expr()

    # Rule: mult_expr -> unary_expr ((* | /) unary_expr)*
    def parse_mult_expr(self):  
        # get first part of expression (unary has higher priority)
        expr = self.parse_unary_expr()

        # keep going while theres * or /
        while self.check('MULT') or self.check('DIV'):
            # get actual symbol, move to next token
            operator = self.go_next().value
            # get next part of the math (the right side of expression)
            right = self.parse_unary_expr()
            # put everything into a node to build the tree
            expr = BinaryOp(operator, expr, right)
        return expr

    # Rule: add_expr -> mult_expr ((+ | -) mult_expr)*
    # follows similar steps to the prev 
    def parse_add_expr(self):
        # get first part of expression (mult has higher priority)
        expr = self.parse_mult_expr()

        # keep going while theres + or -
        while self.check('PLUS') or self.check('MINUS'):
            operator = self.go_next().value
            right = self.parse_mult_expr()
            expr = BinaryOp(operator, expr, right)
        return expr

    # Rule: comp_expr -> add_expr [comp_op add_expr]
    # comp_op -> = | <> | < | > | <= | >=
    def parse_comp_expr(self):
        expr = self.parse_add_expr()
        # check for each comparison operator 
        if (self.check('EQ') or self.check('NEQ') or 
            self.check('LT') or self.check('GT') or 
            self.check('LEQ') or self.check('GEQ')):
            operator = self.go_next().value
            right = self.parse_add_expr()
            return BinaryOp(operator, expr, right)
        return expr
    
    # Rule: and_expr -> comp_expr ( && comp_expr )*
    def parse_and_expr(self):
        # start with the comparison
        expr = self.parse_comp_expr()

        # keep chaining while theres &&
        while self.check('AND'):
            op = self.go_next().value
            right = self.parse_comp_expr()
            expr = BinaryOp(op, expr, right)
            
        return expr
    
    # Rule: or_expr -> and_expr ( || and_expr )*
    def parse_or_expr(self):
        # start with the and
        expr = self.parse_and_expr()
        while self.check('OR'):
            operator = self.go_next().value
            right = self.parse_and_expr()
            expr = BinaryOp(operator, expr, right)
        return expr

    # Rule: expr -> let_expr | if_expr | fun_expr | or_expr
    # this has the lowest precedence, starts here
    def parse_expr(self):
        # look ahead to see if it starts with a keyword
        if self.check('LET'):
            return self.parse_let_expr()
            
        elif self.check('IF'):
            return self.parse_if_expr()
            
        elif self.check('FUN'):
            return self.parse_fun_expr()
            
        # if none go down following precedence
        return self.parse_or_expr()

    # if condition then a else b
    def parse_if_expr(self):
        # skip the if 
        self.go_next()  

        # parse the condition
        condition = self.parse_expr()

        # then part of conditional
        self.expect('THEN')
        then_branch = self.parse_expr()

        # else part of conditional
        self.expect('ELSE')
        else_branch = self.parse_expr()

        # return  If node from ast_nodes.py
        return If(condition, then_branch, else_branch)
    
    # fun x -> x + 1 or fun x y -> x + y
    def parse_fun_expr(self):
        # skip the fun
        self.go_next() 
        # this is to collect parameter names
        params = []
        
        while self.check('ID'):
            params.append(self.go_next().value)

        # there will be at least 1
        if len(params) == 0:
            token = self.current()
            print(f"Syntax Error at line {token.line}, column {token.column}: parameter needed after fun")
            exit(1)
        self.expect('ARROW')
        body = self.parse_expr()
        return Fun(params, body)
    
    # Rule: let_expr -> LET [REC] ID [ID]* = expr IN expr
    def parse_let_expr(self):
        # skip the let
        self.go_next()  
        # check if its recursive
        is_rec = False
        if self.check('REC'):
            self.go_next()
            is_rec = True

        # get the name (func/var name)
        name = self.expect('ID').value

        # get any extra params
        params = []
        while self.check('ID'):
            params.append(self.go_next().value)

        self.expect('EQ')
        value = self.parse_expr()

        self.expect('IN')
        body = self.parse_expr()
        
        return Let(name, params, value, body, is_rec)
    
    # this is the start point for the parser: program -> expr
    def parse(self):
        result = self.parse_expr()
        if not self.check('EOF'):
            token = self.current()
            print(f"Syntax Error at line {token.line}, column {token.column}: unexpected token '{token.value}' after expression")
            exit(1)
        return result
