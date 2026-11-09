"""Pratt 解析器：算法手写一次，表来自 out/parser_gen.py。

这个文件里没有任何"哪门语言"的知识——它只认记录图给出的五种字段。
换一份 .td，它解析的就是另一门语言。
"""
import re
from parser_gen import TOKENS, OPERATORS, FORMS


class ParseError(Exception):
    def __init__(self, msg, col):
        super().__init__(f"第 {col + 1} 列: {msg}")
        self.col = col


class Tok:
    __slots__ = ("kind", "text", "col")

    def __init__(self, kind, text, col):
        self.kind, self.text, self.col = kind, text, col

    def __repr__(self):
        return f"Tok({self.kind},{self.text!r})"


# ---- 拼写 -> 角色。同一个 '-' 既是前缀(25)又是中缀(10)，靠位置区分。----
INFIX = {}
PREFIX = {}
for sp, prec, assoc, kind, sem in OPERATORS:
    if kind in ("Binary", "Postfix"):
        INFIX[sp] = (prec, assoc, kind, sem)
    elif kind == "Unary":
        PREFIX[sp] = (prec, sem)

FORMS_BY_OPEN = {o: (n, c) for n, o, c in FORMS}


def tokenize(src):
    out, i, n = [], 0, len(src)
    while i < n:
        ch = src[i]
        if ch.isspace():
            i += 1
            continue
        hit = None
        for _, open_, close in FORMS:          # 语法结构优先，避免 '(' 被当成运算符
            for kind, lit in (("open", open_), ("close", close)):
                if src.startswith(lit, i):
                    hit = (f"Form_{kind}", lit, len(lit))
                    break
            if hit:
                break
        if not hit:
            for sp in INFIX.keys() | PREFIX.keys():
                if src.startswith(sp, i):
                    hit = ("Op", sp, len(sp))
                    break
        if not hit:
            for name, pat in TOKENS:
                m = re.match(pat, src[i:])
                if m:
                    hit = (name, m.group(0), len(m.group(0)))
                    break
        if not hit:
            raise ParseError(f"无法识别的字符 {ch!r}", i)
        out.append(Tok(hit[0], hit[1], i))
        i += hit[2]
    out.append(Tok("EOF", "", n))
    return out


def parse(src):
    toks = tokenize(src)
    pos = 0

    def peek():
        return toks[pos]

    def take():
        nonlocal pos
        t = toks[pos]
        pos += 1
        return t

    def parse_expr(min_prec):
        left = parse_prefix()
        while True:
            t = peek()
            if t.kind != "Op" or t.text not in INFIX:
                return left
            prec, assoc, kind, sem = INFIX[t.text]
            if prec < min_prec:
                return left
            take()
            if kind == "Postfix":                 # 后缀不吞右操作数
                left = ("Postfix", sem, left)
                continue
            nxt = prec + 1 if assoc == "left" else prec   # 结合性只影响这一行
            left = ("Binary", sem, left, parse_expr(nxt))

    def parse_prefix():
        t = peek()
        if t.kind in ("INT", "FLOAT"):
            take()
            val = float(t.text) if t.kind == "FLOAT" else int(t.text)
            return ("Literal", val)
        if t.kind == "IDENT":
            take()
            return ("Var", t.text)
        if t.kind == "Op" and t.text in PREFIX:
            prec, sem = PREFIX[t.text]
            take()
            return ("Unary", sem, parse_expr(prec))
        if t.kind == "Form_open":
            take()
            e = parse_expr(1)
            if peek().kind != "Form_close":
                raise ParseError(f"缺少 {FORMS_BY_OPEN[t.text][1]!r}", peek().col)
            take()
            return e
        if t.kind == "EOF":
            raise ParseError("期望一个表达式，但输入结束了", t.col)
        raise ParseError(f"期望一个表达式，得到 {t.text!r}", t.col)

    if peek().kind == "EOF":
        raise ParseError("输入为空", 0)
    node = parse_expr(1)
    if peek().kind != "EOF":
        raise ParseError(f"多余的内容 {peek().text!r}", peek().col)
    return node


def show(node):
    """把 AST 打成 s-expression，方便肉眼核对结合性。"""
    if node[0] == "Literal":
        return str(node[1])
    if node[0] == "Var":
        return node[1]
    if node[0] == "Unary":
        return f"({node[1]} {show(node[2])})"
    if node[0] == "Postfix":
        return f"({node[1]} {show(node[2])})"
    return f"({node[1]} {show(node[2])} {show(node[3])})"
