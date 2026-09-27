"""
Lexer and Parser for MiniML

This is the lexer class which reads raw source code and produces a list of tokens
"""
from token import Token

# this dictionary is used to check if an ID is actually a keyword
KEYWORDS = {
    'let': 'LET', 'in': 'IN', 'if': 'IF', 'then': 'THEN', 'else': 'ELSE', 
    'fun': 'FUN', 'rec': 'REC', 'not': 'NOT',
    'true': 'BOOL', 'false': 'BOOL'
}

class Lexer:
    # initialize lexer with the input code and start values
    def __init__(self, source):
        self.source = source # full source code string
        self.pos = 0 # current character position
        self.line = 1 # current line number
        self.column = 1 # current column number
        self.tokens = [] # list that will be filled with token objects

    # returns the character at current position, or none if at end
    def current_char(self):
        # check if pos is valid length
        if self.pos < len(self.source):
            # return the single character at current index
            return self.source[self.pos]
        # passed end of the string so return nothing
        return None
    
    # look at next char without moving the position
    def peek(self):
        # check if next position is still valid (inside the string)
        if self.pos + 1 < len(self.source):
            # return the char at the next position
            return self.source[self.pos + 1]
        # return nothing if theres nothing
        return None

    # go to the next character and increment line/column variables
    def go_next(self):
        # check if already at the end of source
        if self.pos < len(self.source):
            # if current char is a newline, go to next line and first char
            if self.source[self.pos] == '\n':
                self.line += 1
                self.column = 1
            # if its any other char, increment column (go to next char)
            else:
                self.column += 1
            self.pos += 1

    # keeps going to nect while current char is a space tab or newline
    def skip_whitespace(self):
        # while theres chars left and there is whitespace
        while self.current_char() is not None and self.current_char() in ' \t\n':
            # call go_next function to move forward, update line/column
            self.go_next()
        
    # called after seeing (* reads until *), error if EOF reached without *
    def skip_comment(self):
        # move past the ( and * chars
        self.go_next()
        self.go_next()
        
        # keep looking until EOF is reached
        while self.current_char() is not None:
            # check if the current char ends comment
            if self.current_char() == '*' and self.peek() == ')':
                # move past the 2 ending comment chars
                self.go_next()
                self.go_next()
                # exit function if comment ended
                return
            
            # if enf wasnt found just move to the next char
            self.go_next()
            
        # if loop finishes and comment didnt end, its an error
        print(f"Lexical Error at line {self.line}, column {self.column}: unterminated comment")
        # stop program completely so it doesnt keep running
        exit(1)

    # collects digits and returns INT token
    def read_number(self):
        # this is an empty string for the digits
        num = ""
        # save the start position of the token
        start_col = self.column
        
        # while current char is a digit
        while self.current_char() is not None and self.current_char().isdigit():
            # add digit to string and go to next char
            num += self.current_char()
            self.go_next()
            
        # add all the data into a new Token object and then return it
        new_token = Token('INT', num, self.line, start_col)
        return new_token


    # collects letters/digits/_'s then checks keyword dict to find specific type or 'ID'
    def read_word(self):
        # similar to prev method, empty string for word and save start pos
        word = ''
        start_col = self.column
        
        # loop while the current char is a letter/number/_
        while self.current_char() is not None and (self.current_char().isalnum() 
                                                   or self.current_char() == '_'):
            # add current char to word string and move to next char in source
            word += self.current_char()
            self.go_next()
            
        # check if word is in the keywords dictionary
        if word in KEYWORDS:
            # if found, use that specific type 
            token_type = KEYWORDS[word]
        # else it is a regular variable name
        else:
            token_type = 'ID'
            
        # create token object using the type and word found and return it
        new_token = Token(token_type, word, self.line, start_col)
        return new_token        
        
    # checks the char at current pos and the next for special 2-char operators <=
    # return the specific token or error if no match
    def read_operator(self):
        # save the starting pos for the token and get current char
        start_col = self.column
        char = self.current_char()

        # first check for 2 char operators
        if char == '<' and self.peek() == '=':
            self.go_next()
            self.go_next()
            new_token = Token('LEQ', '<=', self.line, start_col)
            return new_token
            
        if char == '>' and self.peek() == '=':
            self.go_next()
            self.go_next()
            new_token = Token('GEQ', '>=', self.line, start_col)
            return new_token
            
        if char == '<' and self.peek() == '>':
            self.go_next()
            self.go_next()
            new_token = Token('NEQ', '<>', self.line, start_col)
            return new_token
            
        if char == '-' and self.peek() == '>':
            self.go_next()
            self.go_next()
            new_token = Token('ARROW', '->', self.line, start_col)
            return new_token
            
        if char == '&' and self.peek() == '&':
            self.go_next()
            self.go_next()
            new_token = Token('AND', '&&', self.line, start_col)
            return new_token
            
        if char == '|' and self.peek() == '|':
            self.go_next()
            self.go_next()
            new_token = Token('OR', '||', self.line, start_col)
            return new_token

        # now handle single char operators
        if char == '+':
            self.go_next()
            new_token = Token('PLUS', '+', self.line, start_col)
        elif char == '-':
            self.go_next()
            new_token = Token('MINUS', '-', self.line, start_col)
        elif char == '*':
            self.go_next()
            new_token = Token('MULT', '*', self.line, start_col)
        elif char == '/':
            self.go_next()
            new_token = Token('DIV', '/', self.line, start_col)
        elif char == '=':
            self.go_next()
            new_token = Token('EQ', '=', self.line, start_col)
        elif char == '<':
            self.go_next()
            new_token = Token('LT', '<', self.line, start_col)
        elif char == '>':
            self.go_next()
            new_token = Token('GT', '>', self.line, start_col)
        elif char == '(':
            self.go_next()
            new_token = Token('LPAREN', '(', self.line, start_col)
        elif char == ')':
            self.go_next()
            new_token = Token('RPAREN', ')', self.line, start_col)
        else:
            # if no operators match, its an error
            print(f"Lexical Error at line {self.line}, column {start_col}: unrecognized character '{char}'")
            exit(1)
            
        return new_token
    
    # this is the main loop, calls methods based on current_char func, returns self.tokens at end
    def tokenize(self):
        # keep going until eof is reached
        while self.current_char() is not None:
            # get the current character to check
            c = self.current_char()
            
            # skip whitespace (tabs/space/newlines)
            if c in ' \t\n':
                self.skip_whitespace()
                # go back to top of loop to see what the next real char is
                continue

            # check for the start of a comment 
            elif c == '(' and self.peek() == '*':
                self.skip_comment()
                # go back to top after comment is gone
                continue

            # if its a number, read the whole integer
            elif c.isdigit():
                # add the number token to list
                self.tokens.append(self.read_number())

            # if it is a letter, read the word (ID or Keyword)
            # words start with a lowercase letter in MiniML
            elif c.islower():
                # add the word token to our list
                self.tokens.append(self.read_word())

            # if not the things above, check if its an operator, error check in function
            else:
                self.tokens.append(self.read_operator())
        
        # add end of file token so the parser knows when to stop
        self.tokens.append(Token('EOF', 'EOF', self.line, self.column))

        # once end of the string reached, return the final list
        return self.tokens