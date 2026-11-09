# legalizer-compare

同一份 `X86LegalizerInfo.td`，两个后端各生成一份产物，归一化成同一个签名后逐条比对。

## 依赖

`compare.py` 吃两份输入：

```bash
llvm-tblgen -gen-legalizer      X86LegalizerInfo.td  > x86_leg.inc
llvm-tblgen -gen-legalizer-core X86LegalizerInfo.td  > x86_core.json
python3 compare.py x86_leg.inc x86_core.json
```

`-gen-legalizer-core` **尚未进上游**，来自本文作者的 `feat/legalizer-answers` 分支。所以这个例子在这里标 ⚠️：代码和结果都在，但你要先有那个 `llvm-tblgen`。

## 结果

见 `REPORT.md`：ruleset 63/63、opcode 115/115、归一化后 legal 签名 53/53。

唯一差异是指针宽度（`p0:*` vs `p0:64`）——它不是 bug，是 Core IR 把配置维度花掉了。

## 为什么留着它

全系列唯一一处外部背书：不是"我觉得两个后端一致"，是"机器比对过，差异只有一处，且能解释"。

## `schema/` 里是什么

两份 `.td` 的原件，供上面对账：

| 文件 | 行数 | 字节 | 来源 |
|---|---|---|---|
| `LegalizerInfo.td` | 760 | 32,904 | 作者的 POC 分支，`llvm/include/llvm/Target/`（未进上游） |
| `X86LegalizerInfo.td` | 984 | 40,554 | 同一分支，`llvm/lib/Target/X86/GISel/` |

快照 `dac078582b28`。两份都带 LLVM 的 Apache-2.0 WITH LLVM-exception 头，
这里只是原样存档，便于按行核对文中的数字（760 行、36 个字段、1 个 `code`、2 个 `dag`）。
