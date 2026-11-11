# mini-tbl：TableGen 的记录层，用 Common Lisp 复刻

配套文章：《如果 TableGen 是用 Lisp 写的》。

目的不是替代 tblgen，是把"宏展开成一张记录表"这件事摊开：`class` 是模板，
`def` 是实例化，`let` 是字段覆盖，`multiclass` / `defm` 是批量展开。骨架就这几样。

## 文件

| 文件 | 作用 |
| --- | --- |
| `mini-tbl.lisp` | 142 行（去注释与空行 109 行）：记录表、继承、类型检查、multiclass、JSON 输出 |
| `demo.lisp` | 13 行：和 `demo.td` 语义相同的一份程序，写成 S-表达式 |
| `demo.td` | 同一份程序，TableGen 语法 |
| `negative.td` / `negative.lisp` | 同一条类型错误，两边都应该拒绝 |
| `compare.py` | 跑 `llvm-tblgen -dump-json` 与 `sbcl --script demo.lisp`，逐条比对 |

## 跑

```bash
sudo apt-get install -y sbcl
python3 compare.py
```

输出：

```
ALU0          ok   ...
MEM_LD        ok   ...
MEM_ST        ok   ...
anonymous_0   ok   ...

4 条记录，3 个键，0 处分歧
```

负例：

```bash
llvm-tblgen -dump-json negative.td   # Field 'Latency' of type 'int' is incompatible ...
sbcl --script negative.lisp          # BAD.LATENCY: expects INT, got "two"
```

## 边界

只比 名字 / 直接基类 / Latency / Resources 四个键，**不构成等价证明**。
未实现：`include`、`foreach`、`!if`、`!cast`、多继承、位域、模板特化。
负例只覆盖"字段类型不匹配"一种。

## 写这版时踩的坑

第一版 `type-ok-p` 用 `(case type (int ...))` 判类型。`case` 比的是符号本身，
而 demo 里的 `int` 在 `cl-user` 包里读出来，函数里的 `int` 在 `mini-tbl` 包里，
两个符号不相等，一路落到 `(t t)` 兜底——**所有类型检查静默失效**。
demo 能跑、对拍也通过，是负例把它抓出来的。

修法：按 `symbol-name` 比字符串，兜底改成报错。
