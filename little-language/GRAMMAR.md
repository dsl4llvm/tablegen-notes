# 表达式语言语法（自动生成）

## 词法

| Token | 模式 |
|---|---|
| `FLOAT` | `[0-9]+\.[0-9]+` |
| `IDENT` | `[A-Za-z_][A-Za-z0-9_]*` |
| `INT` | `[0-9]+` |

## 优先级（从松到紧）

| 级别 | 运算符 | 结合 |
|---|---|---|
| 10 | `+` `-` | left |
| 20 | `*` `/` | left |
| 30 | `^` | right |

## 一元

- 前缀：`-`(25)
- 后缀：`!`(40)

## EBNF

```ebnf
expr    ::= binary ;
binary  ::= unary { op unary } ;
unary   ::= prefix* primary postfix* ;
primary ::= INT | FLOAT | IDENT | '(' expr ')' ;
```
