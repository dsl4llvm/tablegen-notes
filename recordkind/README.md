# recordkind

三个最小的 `.td`，验证一件事：TableGen 的「元模型层」在实现里不是类型，是两张 `std::map` 加一个 `enum` 标签。

## 跑

```bash
llvm-tblgen probe.td  -print-records   # 同名 class / def 共存，不报错
llvm-tblgen probe1.td -print-records   # error: Couldn't find class 'D'
llvm-tblgen probe2.td -print-records   # error: Couldn't find class 'D'
llvm-tblgen probe3.td -print-records   # error: Couldn't find class 'M'. Use 'defm' ...
```

## 三个文件

| 文件 | 内容 | 预期 |
|---|---|---|
| `probe.td` | 同名 `class TB` 与 `def TB` | 正常打印，两条记录互不干扰 |
| `probe1.td` | `class C : D;`，`D` 是 def | `Couldn't find class 'D'` |
| `probe2.td` | `def E : D;`，`D` 是 def | `Couldn't find class 'D'` |
| `probe3.td` | `def D : M;`，`M` 是 multiclass | `Couldn't find class 'M'`，并提示改用 `defm` |

前两个的报错文案完全一样——因为 `:` 右边只查 class 表，查不到就报「找不到 class」，不管那个名字在 def 表里存不存在。

第三个多出半句提示：parser 知道 `M` 是 multiclass（它自己在另一张表里记着），所以能告诉你「要用 defm」。知道，但不在同一条查找路径上。

## 结论

结构能被强制，语义只能被约定。你能让编译器拒绝一次继承，但你不能让它拒绝一个坏设计。
