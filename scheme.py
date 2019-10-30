# scheme.py
#
# Challenge:  Can you implement a mini-scheme interpreter capable of 
# executing the following code:
env = {
    '+' : lambda x, y: x + y,
    '-' : lambda x, y: x - y,
    '*' : lambda x, y: x * y,
    '/' : lambda x, y: x / y,
    '!=' : lambda x, y: x != y,
    '=' : lambda x, y: x == y,
    '>' : lambda x, y: x > y,
    '<' : lambda x, y: x < y,
    '<=' : lambda x, y: x <= y,
    '>=' : lambda x, y: x >= y,
}

def substitute(exp, name, value):
    if exp == name:
        return value
    elif isinstance(exp, tuple):
        return tuple([substitute(part, name, value) for part in exp])
    else:
        return exp #Unchanged

class Procedure:
    def __init__(self, parameters, expressions, env):
        self.parameters = parameters
        self.expressions = expressions
        self.env = env

    def __call__(self, *args):
        for expression in self.expressions:        # Substitute the arguments for parameter names
            for names, values in zip(self.parameters, args):
                expression = substitute(expression, names, values)

            result = seval(expression,             # Evaluate the resulting expression
                           dict(self.env))         # makes a copy of env
        return result

def seval(sexp, env):
    if isinstance(sexp, (int, float, Procedure)):
        return sexp
    elif isinstance(sexp, str):  # A symbol of some kind
        return env[sexp]         # Environment lookup
    elif isinstance(sexp, tuple):
        if sexp[0] == 'define':
            name = sexp[1]
            value = seval(sexp[2], env)
            env[name] = value
            return
        elif sexp[0] == 'if':
            condition = sexp[1]
            thenClause = sexp[2]
            elseClause = sexp[3]
            if seval(condition, env):
                return seval(thenClause, env)
            else:
                return seval(elseClause, env)
        elif sexp[0] == 'lambda':
            parameters = sexp[1]
            expressions = sexp[2:]
            return Procedure(parameters=parameters, expressions=expressions, env=env)
        return sapply(sexp[0], sexp[1:], env)
    else:
        raise RuntimeError("bad expression")

# Applies a procedure (calling a procedure)
def sapply(proc, args, env=env):
    actual_proc = seval(proc, env)                      # Get the "procedure" itself
    evaluated_args = [seval(arg, env) for arg in args]  # Evaluate the arguments
    return actual_proc(*evaluated_args)                 # Call Procedure

assert seval(23, {}) == 23
assert seval("x", {"x": 23}) == 23
assert seval(("+", 1, 2), env) == 3
assert seval(("+", 1, ("*", 2, 3)), env) == 7

seval(("define", "x", 13), env) == 7
assert seval(("x"), env) == 13

assert seval(("if", ("<", 2, 3), 4, 5), env) == 4
assert seval(("if", (">", 2, 3), 4, 5), env) == 5

assert substitute(('*', ('+', 'x', 'y'), ('x',)), 'x', 2) == ('*', ('+', 2, 'y'), (2,))

# A function definition expressed as a S-expression (in tuples)
fact = ('define', 'fact',
        ('lambda', ('n',), ('if', ('=', 'n', 1), 1, ('*', 'n', ('fact', ('-', 'n', 1))))))

seval(fact, env)
seval(('define', 'n', 5), env)
result = seval(('fact', 'n'), env)
assert result == 120