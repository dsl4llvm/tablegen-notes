# 给 TableGen 加一条三元语法

`ternary.patch`：52 行新增、0 行删除、单文件 `llvm/lib/TableGen/TGParser.cpp`。

## 复现

```bash
cd /path/to/llvm-project
git checkout dac078582b28
git apply /path/to/ternary.patch
ninja llvm-tblgen
./bin/llvm-tblgen test.td -print-records | diff - expected.txt
```

## 覆盖的东西

`test.td` 里有 11 个 def/class，分别测：

1. 常量折叠（`1 ? 10 : 20` → `10`）
2. 未解析条件（class 里 `!gt(v, 100) ? 1 : 0` 保留为 `!if(...)`，实例化时求值）
3. 嵌套右结合（`1 ? 2 : 0 ? 3 : 4` → `2`）
4. 列表元素位（`[1 ? 2 : 3, 4]` → `[2, 4]`）
5. 字符串分支
6. `bits<8>` 分支
7. `?`（unset）作为分支

## 关键数字

| 项 | 值 |
|---|---|
| patch 新增 | 52 行 |
| 其中语法 | 17 行 |
| 其中类型规则 + 辅助 | 24 行 |
| 其中注释/空行/BNF | 11 行 |
| `check-llvm-tablegen` | 500/500 |
| X86 `-print-records` 新旧比对 | 3,307,328 行逐字节相同 |
