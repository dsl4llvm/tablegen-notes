# 由 tools/gen_parser.py 从 expr.td 生成，不要手改。
# 生成命令：llvm-tblgen -dump-json expr.td -o expr.json && python3 tools/gen_parser.py expr.json out/parser_gen.py

TOKENS = [
    ('IDENT', '[A-Za-z_][A-Za-z0-9_]*'),
    ('FLOAT', '[0-9]+\\.[0-9]+'),
    ('INT', '[0-9]+'),
]

OPERATORS = [
    # (拼写, 优先级, 结合性, 节点种类, 语义名)
    ('+', 10, 'left', 'Binary', 'add'),
    ('/', 20, 'left', 'Binary', 'div'),
    ('!', 40, 'left', 'Postfix', 'fac'),
    ('*', 20, 'left', 'Binary', 'mul'),
    ('-', 25, 'right', 'Unary', 'neg'),
    ('^', 30, 'right', 'Binary', 'pow'),
    ('-', 10, 'left', 'Binary', 'sub'),
]

# 语法结构（不是运算符）：(name, open, close)
FORMS = [
    ('Group', '(', ')'),
]
