# escape-hatch

量 td 里两种逃生舱的密度。同一个脚本、同一个分母，只换目录。

## 跑

```bash
python3 measure_escape.py /path/to/llvm-project
```

## 指标

| 指标 | 定义 |
|---|---|
| `lines` | 该目录下所有 `.td` 的行数 |
| `code/1k` | 以 `code X =` 开头的行数 / 千行 |
| `dag/1k` | 以 `dag X =` 开头的行数 / 千行 |

用密度不用绝对值，是为了消除体量差异：642,026 行里有 18 个 `code`，和 109,673 行里有 96 个，不是一回事。

## 2026-11-09 实测

```
llvm/include     lines=  69733  code/1k=0.70  dag/1k=0.37
llvm/lib/Target  lines= 641326  code/1k=0.03  dag/1k=1.85
clang/include    lines= 109768  code/1k=0.87  dag/1k=0.15
mlir/include     lines= 158738  code/1k=0.57  dag/1k=0.55
```

数字随上游漂移。要看的不是 0.03 还是 0.04，是**同一个仓库里两个子系统的用法差了近两个数量级**。

## 判据

密度本身不是好坏。要问的是：这段东西，值不值得被机器理解？

目标描述的消费者是算法（指令选择器要拿 `Pat<...>` 做匹配），所以它长出了 `dag`；
Clang 大量消费者的读者是人（整段 Markdown 文档、整段 C++ 序列化代码），所以它长出了 `code`。
