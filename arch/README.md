# arch

一个 36 行的后端，验证《TableGen 的架构：改动落在哪一层》里的两句话：

1. 加一个产物 = 新建一个 `.cpp` + 在 `CMakeLists.txt` 里加一行，前端一行不动；
2. 后端能拿到的全部输入就是 `RecordKeeper`，`.td` 长什么样它看不见。

## 先看代价

这个例子要动 LLVM 源码、重编 `llvm-tblgen`，不是 `verify.sh` 能跑的那一类。

- 一份配好的 LLVM 构建（`ninja llvm-tblgen` 可用）；
- 增量重编约 300 条边，半分钟到一分钟。

## 三步

在 LLVM 源码树里：

```bash
# 1. 把后端放进内核（和骨架后端做邻居）
cp CountByClassBackend.cpp llvm/lib/TableGen/

# 2. 进 CMake，加一行
#    llvm/lib/TableGen/CMakeLists.txt
#      TableGenBackendSkeleton.cpp
#      CountByClassBackend.cpp      <-- 加这行

# 3. 重编
ninja -C <build-dir> llvm-tblgen
```

## 跑

```bash
# 最小输入
llvm-tblgen count.td -gen-count-by-class
# → Instr 2

# 整份 X86（在 llvm-project 根目录下）
llvm-tblgen -I llvm/include -I llvm/lib/Target/X86 \
            llvm/lib/Target/X86/X86.td -gen-count-by-class \
  | sort -k2 -rn | head -5
# → 见 expected-x86-top5.txt
```

完整输出在 `expected-tiny.txt`；X86 那份只存了前五名，全量有 1,587 个 class（多数是 0）。

`Instruction` 底下两万两千条，这个数 `.td` 里没有写，是从记录之间的继承关系走出来的——只有拿着 `RecordKeeper` 的后端才知道。

## 为什么放在 lib/TableGen

为了把改动压到最小：和 `TableGenBackendSkeleton.cpp` 做邻居，加一行就能编。

真要往上游提交，位置应该是 `llvm/utils/TableGen/`：那是"LLVM 自己的后端"该待的地方，`lib/TableGen` 只放内核和官方骨架。放到 `utils/` 还要多改一处它自己的 `CMakeLists.txt`，并用 `-DLLVM_TARGETS_TO_BUILD=...` 确认不牵连别的 target。

这个差别本身就是文章第六节那张表：同一个产物，放内核和放 utils，动的地方不一样。

## 代码

`CountByClassBackend.cpp` 36 行，`run()` 占 8 行，剩下是 license 头、include、类声明和末尾一行注册。

它没有分析的成分，只是把 `RecordKeeper` 的两张表读了一遍：`getClasses()` 拿所有 class，`getAllDerivedDefinitions()` 数每个 class 下面挂了多少条 def。
