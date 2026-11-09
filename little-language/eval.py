"""语义层：第三层。td 里只有名字，真行为在这里。

这就是"语义外置"：换一个 eval.py，同一份 AST 可以是求值器、编译器、类型检查器。
"""

class EvalError(Exception):
    pass


def _fact(n):
    if not isinstance(n, int) or n < 0:
        raise EvalError(f"阶乘只接受非负整数，得到 {n!r}")
    r = 1
    for i in range(2, n + 1):
        r *= i
    return r


SEM = {
    "add": lambda a, b: a + b,
    "sub": lambda a, b: a - b,
    "mul": lambda a, b: a * b,
    "div": lambda a, b: a / b,
    "pow": lambda a, b: a ** b,
    "neg": lambda a: -a,
    "fac": _fact,
}


def evaluate(node, env=None):
    env = env or {}
    kind = node[0]
    if kind == "Literal":
        return node[1]
    if kind == "Var":
        if node[1] not in env:
            raise EvalError(f"未定义的变量 {node[1]!r}")
        return env[node[1]]
    if kind in ("Unary", "Postfix"):
        return SEM[node[1]](evaluate(node[2], env))
    return SEM[node[1]](evaluate(node[2], env), evaluate(node[3], env))
