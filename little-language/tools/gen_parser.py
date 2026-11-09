#!/usr/bin/env python3
"""后端 A：把记录图发射成解析表。

注意这个文件里没有任何关于"表达式"的领域知识——
它只知道记录上有 Precedence / Assoc / Kind / Semantics 这几个字段。
这就是"后端是解释器"的含义。
"""
import json, sys, pathlib

src = json.load(open(sys.argv[1], encoding="utf-8"))
inst = src["!instanceof"]

tokens, ops = [], []
for name in inst.get("Token", []):
    r = src[name]
    tokens.append((r["Name"], r["Pattern"]))

for name in inst.get("Operator", []):
    r = src[name]
    ops.append((r["Spelling"], r["Precedence"], r["Assoc"], r["Kind"], r["Semantics"]))

forms = []
for name in inst.get("SyntaxForm", []):
    r = src[name]
    forms.append((r["Name"], r["Open"], r["Close"]))

# 词法歧义：长模式优先。这是后端的决定，td 里没写——语义在后端。
tokens.sort(key=lambda t: -len(t[1]))
# 运算符：长的先匹配（本例都是单字符，规则写在这里是为了以后扩展）
ops.sort(key=lambda o: -len(o[0]))

out = pathlib.Path(sys.argv[2])
with out.open("w", encoding="utf-8") as f:
    f.write("# 由 tools/gen_parser.py 从 expr.td 生成，不要手改。\n")
    f.write("# 生成命令：llvm-tblgen -dump-json expr.td -o expr.json && python3 tools/gen_parser.py expr.json out/parser_gen.py\n\n")
    f.write("TOKENS = [\n")
    for n, p in tokens:
        f.write(f"    ({n!r}, {p!r}),\n")
    f.write("]\n\nOPERATORS = [\n")
    f.write("    # (拼写, 优先级, 结合性, 节点种类, 语义名)\n")
    for o in ops:
        f.write(f"    {o!r},\n")
    f.write("]\n\n# 语法结构（不是运算符）：(name, open, close)\nFORMS = [\n")
    for fm in forms:
        f.write(f"    {fm!r},\n")
    f.write("]\n")
print(f"wrote {out}: {len(tokens)} tokens, {len(ops)} operators, {len(forms)} forms")
