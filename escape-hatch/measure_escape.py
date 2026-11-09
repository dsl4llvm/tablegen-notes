#!/usr/bin/env python3
"""测量 td 的逃生舱密度。用法：python3 measure_escape.py <llvm-project 根目录>"""
import os, re, sys

pat_code = re.compile(r'^[ \t]*code[ \t]+[A-Za-z_]')
pat_dag  = re.compile(r'^[ \t]*dag[ \t]+[A-Za-z_]')

root_all = sys.argv[1] if len(sys.argv) > 1 else "."
for root in ["llvm/include", "llvm/lib/Target", "clang/include", "mlir/include"]:
    base = os.path.join(root_all, root)
    if not os.path.isdir(base):
        continue
    lines = code = dag = 0
    for dp, _, fns in os.walk(base):
        for fn in fns:
            if not fn.endswith(".td"):
                continue
            txt = open(os.path.join(dp, fn), encoding="utf-8", errors="ignore").read()
            lines += txt.count("\n")
            code += sum(1 for L in txt.splitlines() if pat_code.match(L))
            dag  += sum(1 for L in txt.splitlines() if pat_dag.match(L))
    k = lines / 1000 or 1
    print(f"{root:16} lines={lines:7} code/1k={code/k:.2f} dag/1k={dag/k:.2f}")
