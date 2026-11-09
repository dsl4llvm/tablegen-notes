# tablegen-notes

《TableGen 深度笔记》九篇的验证代码。

每个目录对应文章里一个**可以自己跑一遍**的结论。不是教程，是证据。

九篇里只有五个有可跑的代码，另外四篇是源码阅读和计数（改 parser 要编 LLVM、量生成器大小要数行），没法做成一个 `make` 就出结果的例子——那种情况这里不硬凑。

## 五个例子

| 目录 | 验证什么 | 依赖 | 状态 |
|---|---|---|---|
| `little-language/` | 87 行 `.td` 定义一门表达式语言；一份定义喂给两个后端，加一个运算符只改 2 行 | `python3`；重新生成需要 `llvm-tblgen` | ✅ 16 条测试全过 |
| `recordkind/` | 「元模型层」物理上只是两张 map + 一个 enum；`class` / `def` 同名共存，`:` 右边只查 class 表 | `llvm-tblgen` | ✅ 三组最小实验 |
| `escape-hatch/` | 量 td 里 `code` 和 `dag` 的密度（每千行），同一把尺子 | `python3` + 一份 llvm-project 源码 | ✅ 可对任意 llvm-project 跑 |
| `ternary-parser/` | 给 TableGen 加一条三元语法：52 行，其中 17 行是语法 | 需要编 `llvm-tblgen`（约 2 分钟）；补丁已在 `tablegen/ternary-sugar` 分支上 | ✅ 已复现，diff 为空 |
| `legalizer-compare/` | 同一份 `.td`，两个后端归一化后逐条比对（63/63、53/53） | 需要带 `-gen-legalizer-core` 的 `llvm-tblgen` | ⚠️ 该后端尚未上游 |

最后两个不是"跑不起来"，是**跑起来要付前置成本**：一个要编 LLVM（约 25 分钟），一个需要本文作者的分支。代码和预期输出都在，代价写在这里，不藏。

## 快速开始

```bash
./verify.sh          # 把不需要额外依赖的都跑一遍
```

单独跑第一个：

```bash
cd little-language
make                 # 重新生成 + 跑测试（需要 llvm-tblgen）
python3 run_tests.py # 不重新生成，直接跑（只需要 python3）
```

`llvm-tblgen` 不在 PATH 上时：

```bash
make TBLGEN=/path/to/llvm-tblgen
```

## 依赖

- Python 3.8+
- `llvm-tblgen`（可选）。任意 LLVM ≥ 15 都能跑前三个例子；`ternary-parser` 需要自己打补丁重编。

## 数字会漂

上游一直在动。文章里的行数是某个 commit 的快照，脚本重跑得到的数会略有不同。

2026-11-09 实测（`llvm-project` main）：

```
llvm/include     lines=  69733  code/1k=0.70  dag/1k=0.37
llvm/lib/Target  lines= 641326  code/1k=0.03  dag/1k=1.85
clang/include    lines= 109768  code/1k=0.87  dag/1k=0.15
mlir/include     lines= 158738  code/1k=0.57  dag/1k=0.55
```

**看趋势，不要背数字。** 文章里写 1.84 还是 1.85 不重要，`code` 比 `dag` 少两个数量级才是那个结论。

## 目录

```
little-language/    一份 td → 解析表 + 语法文档 → Pratt 引擎 → 求值
  expr.td             语言定义（87 行，唯一事实来源）
  tools/gen_parser.py 后端 A：生成解析表
  tools/gen_doc.py    后端 B：生成语法文档
  pratt.py            解析引擎（143 行，手写一次，与语言无关）
  eval.py             语义（41 行）
  run_tests.py        11 条正例 + 5 条负例
recordkind/         三个 .td，证明"层"在实现里只是两张 map
escape-hatch/       measure_escape.py
ternary-parser/     ternary.patch + test.td + expected.txt
legalizer-compare/  compare.py + REPORT.md
```

## 许可

MIT，见 `LICENSE`。
