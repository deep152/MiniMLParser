"""
Lexer and Parser for MiniML

These are the AST node classes, one for each type of expression in MiniML
"""

# just a number eg 42
class IntLiteral:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"IntLiteral({self.value})"

# true or false
class BoolLiteral:
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return f"BoolLiteral({self.value})"

# variable name eg x, var1
class Variable:
    def __init__(self, name):
        self.name = name
    def __repr__(self):
        return f"Variable({self.name})"

# any two sided operation eg x + 1
class BinaryOp:
    def __init__(self, op, left, right):
        self.op = op
        self.left = left
        self.right = right
    def __repr__(self):
        return f"BinaryOp({self.op!r}, {self.left}, {self.right})"

# not or unary minus eg -x or not true
class UnaryOp:
    def __init__(self, op, expr):
        self.op = op
        self.expr = expr
    def __repr__(self):
        return f"UnaryOp({self.op!r}, {self.expr})"

# let and let rec
class Let:
    def __init__(self, name, params, value, body, is_rec=False):
        self.name = name
        self.params = params
        self.value = value
        self.body = body
        self.is_rec = is_rec
    def __repr__(self):
        return f"Let({self.name!r}, {self.params}, {self.value}, {self.body}, is_rec={self.is_rec})"

# if conditions
class If:
    def __init__(self, condition, then_branch, else_branch):
        self.condition = condition
        self.then_branch = then_branch
        self.else_branch = else_branch
    def __repr__(self):
        return f"If({self.condition}, {self.then_branch}, {self.else_branch})"

# function definitions
class Fun:
    def __init__(self, params, body):
        self.params = params
        self.body = body
    def __repr__(self):
        return f"Fun({self.params}, {self.body})"

# function call eg f 5 
class App:
    def __init__(self, func, arg):
        self.func = func
        self.arg = arg
    def __repr__(self):
        return f"App({self.func}, {self.arg})"