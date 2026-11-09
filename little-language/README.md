# little-language

87 行 `.td`，定义一门带幂运算和阶乘的表达式语言。同一份定义喂给两个互不相识的后端。

## 跑

```bash
make                 # expr.td → expr.json → parser_gen.py + GRAMMAR.md → 跑测试
python3 run_tests.py # 只要 python3
```

`llvm-tblgen` 不在 PATH 上：`make TBLGEN=/path/to/llvm-tblgen`

## 结构

```
expr.td                 87 行   语言定义（唯一事实来源）
├─ tools/gen_parser.py          后端 A：读 json，生成解析表
└─ tools/gen_doc.py             后端 B：读 json，生成语法文档
pratt.py               143 行   解析引擎（手写一次，与语言无关）
eval.py                 41 行   语义
run_tests.py                    11 正例 + 5 负例
```

生成物 `expr.json` / `parser_gen.py` / `GRAMMAR.md` 已经提交，所以不装 LLVM 也能直接跑测试。`make clean && make` 可以验证它们确实是生成的。

## 两个后端

`gen_parser.py` 和 `gen_doc.py` 没有任何共享代码，只共享输入 `expr.json`。改 `expr.td`，两边同时变——因为它们不持有语法副本。

## 加一个运算符

`expr.td` 加一行 `defm`，`eval.py` 的语义表加一行。引擎和后端 0 行。

## 预期输出

```
1 + 2 * 3         (add 1 (mul 2 3))                7  PASS
2 ^ 3 ^ 2         (pow 2 (pow 3 2))              512  PASS
-3!               (neg (fac 3))                   -6  PASS
...
16 passed, 0 failed
```

`2 ^ 3 ^ 2 = 512` 而不是 64，说明右结合是被声明出来的，不是引擎里写死的。

## 两张图

文章里用的示意图，源文件是手写 SVG（文字精确，不靠生成模型）：

| 文件 | 讲什么 |
|---|---|
| `figs/little-language-flow.svg` | 一份 `expr.td` → `expr.json` → 两个互不相识的后端 → 两份产物 |
| `figs/little-language-assoc.svg` | `2 ^ 3 ^ 2` 两种结合性 = 两棵树，512 与 64 |

同名 `.png` 是 2400 px 渲染，给知乎上传用。
