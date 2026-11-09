#!/usr/bin/env python3
"""后端 B：同一份记录图，发射成人读的语法文档。

和 gen_parser.py 吃的是同一个 expr.json。这就是"共享层厚度 >= 2"。
"""
import json, sys, pathlib
from collections import defaultdict

src = json.load(open(sys.argv[1], encoding="utf-8"))
inst = src["!instanceof"]

toks = [(src[n]["Name"], src[n]["Pattern"]) for n in inst.get("Token", [])]
ops  = [(src[n]["Spelling"], src[n]["Precedence"], src[n]["Assoc"],
         src[n]["Kind"], src[n]["Semantics"]) for n in inst.get("Operator", [])]

by_prec = defaultdict(list)
for sp, p, a, k, s in ops:
    if k == "Binary":
        by_prec[p].append((sp, a))

lines = ["# 表达式语言语法（自动生成）", "",
         "## 词法", "", "| Token | 模式 |", "|---|---|"]
lines += [f"| `{n}` | `{p}` |" for n, p in toks]
lines += ["", "## 优先级（从松到紧）", "", "| 级别 | 运算符 | 结合 |", "|---|---|---|"]
for p in sorted(by_prec):
    ls = sorted(by_prec[p])
    lines.append(f"| {p} | {' '.join('`'+sp+'`' for sp, _ in ls)} | {ls[0][1]} |")

pre = [(sp, p) for sp, p, a, k, s in ops if k == "Unary"]
post = [(sp, p) for sp, p, a, k, s in ops if k == "Postfix"]
lines += ["", "## 一元", "", f"- 前缀：{' '.join('`'+s+'`'+f'({p})' for s,p in pre) or '无'}",
          f"- 后缀：{' '.join('`'+s+'`'+f'({p})' for s,p in post) or '无'}", "",
          "## EBNF", "", "```ebnf",
          "expr    ::= binary ;",
          "binary  ::= unary { op unary } ;",
          "unary   ::= prefix* primary postfix* ;",
          "primary ::= INT | FLOAT | IDENT | '(' expr ')' ;",
          "```"]

out = pathlib.Path(sys.argv[2])
out.write_text("\n".join(lines) + "\n", encoding="utf-8")
print(f"wrote {out}: {len(toks)} tokens, {len(ops)} operators")
