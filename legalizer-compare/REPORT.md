# 两个后端的一致性报告（X86 legalizer）

- 输入：`llvm/lib/Target/X86/GISel/X86LegalizerInfo.td`（984 行）
- 分支：`feat/legalizer-answers` @ `dac078582b28`
- 工具：`llvm-tblgen` 24.0.0git（`/home/ubuntu/llvm/builds/dsl-tablegen`）
- 比对器：`compare.py`（本目录）

## 产物

| 后端 | 产物 | 大小 |
|---|---|---|
| `-gen-legalizer` | C++ 调用链 | 441 行 / 26,232 字节 |
| `-gen-legalizer-core` | JSON IR（`legalizer-spec-core` v0.1） | 231,187 字节 |
| `-gen-legalizer-table` | 决策表 + gaps | 98,949 字节 |

## 结果

```
L1 结构
  ruleset : C++ 63 / JSON 63        ← 完全一致
  opcode  : C++ 115 / JSON 115      ← 完全一致
  JSON 规则 570 条，escapes 0，hasFeature 谓词 219

L2 legal 签名
  可比 opcode        53 / 65（12 个用了未实现的 builder）
  归一化前一致        44 / 53
  归一化后一致        53 / 53        ← 唯一差异是 p0:* vs p0:64
```

## 唯一差异：指针宽度

`X86_p0` 在 C++ 里是 `LLT::pointer(0, Subtarget.isTarget64BitLP64() ? 64 : 32)`——**动态**；
JSON 里是 `p0:64`——**按 `config.pointer_width` 固化**。

结论：Core IR 产物带配置维度，C++ 产物不带。
把 JSON 喂给 32 位目标之前必须重新生成。

## 未覆盖

- 11 个 opcode 使用 `legalForTypesWithMemDesc` / `legalForTypeWithAnyImm` / `legalForCartesianProduct`
- 1 个（`G_INTTOPTR`）的元组里含动态类型 `X86_sMaxScalar`
- 12 / 65 = 18% 未比对

## 意外发现

1. `escapes: []` 是空的，但 **219 条规则的 `hasFeature` 参数里装着原始 C++ 表达式**
   （例如 `"!Subtarget.useSoftFloat() && Subtarget.hasX87()"`）。
   逃生舱没有消失，它被重新记账了。
2. `-gen-legalizer-table` 会输出 `X86TableGaps`：显式声明哪些 ruleset **无法被表化**，
   原因码 `{"X86_STORE", 2}`。
