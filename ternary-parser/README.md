# 给 TableGen 加一条三元语法

`ternary.patch`：52 行新增、0 行删除，单文件 `llvm/lib/TableGen/TGParser.cpp`。

补丁已经打在公开分支上，可以直接 clone 下来编：

```bash
git clone --depth 1 -b tablegen/ternary-sugar \
  https://github.com/dsl4llvm/llvm-project.git
cd llvm-project
cmake -G Ninja -S llvm -B build -DCMAKE_BUILD_TYPE=Release \
  -DLLVM_TARGETS_TO_BUILD=X86 -DLLVM_ENABLE_PROJECTS= \
  -DLLVM_INCLUDE_TESTS=OFF
ninja -C build llvm-tblgen
./build/bin/llvm-tblgen test.td -print-records | diff - expected.txt
```

320 个目标，`-j24` 约 2 分钟。**实测：diff 无输出，和 `expected.txt` 逐字节相同。**

不想 clone 整个仓库，也可以自己打：

```bash
cd /path/to/llvm-project
git apply /path/to/ternary.patch    # 对当前 main 也能干净应用
ninja llvm-tblgen
```

## 改了什么

```
ValueSuffix ::= '?' Value ':' Value     // sugar for !if(Cond, A, B)
```

`?` 本来就有——但那是 unset 字面量，只出现在一个值**开始**的位置。这里加的是它出现在一个值**结束之后**的第二种用法。两种含义靠语法位置区分，不靠词法。

解析出来没有新节点：常量在解析期就折叠，条件暂时算不出来的保留成 `!if(...)`，等实例化时再求值。

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
