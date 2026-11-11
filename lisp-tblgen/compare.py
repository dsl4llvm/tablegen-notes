#!/usr/bin/env python3
"""把 mini-tbl 展开出来的记录表，和 llvm-tblgen -dump-json 的结果逐条对拍。

比对范围是有意收窄的：只比 名字 / 直接基类 / Latency / Resources 四个键。
这不是在证明两个实现等价，只是在证明：同一份语义，两个语法外壳，展开出的表一样。
"""
import json, subprocess, sys

TBLGEN = "/home/ubuntu/llvm/builds/dsl-tablegen/bin/llvm-tblgen"
KEYS = ("Latency", "Resources")

def norm(d):
    out = {}
    for name, rec in d.items():
        if name.startswith("!"):
            continue
        out[name.lower()] = {
            "supers": [s.lower() for s in rec["!superclasses"]],
            **{k: rec[k] for k in KEYS},
        }
    return out

tbl = norm(json.loads(subprocess.check_output([TBLGEN, "-dump-json", "demo.td"])))
lisp = norm(json.loads(subprocess.check_output(["sbcl", "--script", "demo.lisp"])))

names = sorted(set(tbl) | set(lisp))
bad = 0
for n in names:
    if n not in tbl or n not in lisp:
        print(f"  {n:12s} 只在一侧存在"); bad += 1; continue
    if tbl[n] == lisp[n]:
        print(f"  {n:12s} ok   {tbl[n]}")
    else:
        bad += 1
        print(f"  {n:12s} DIFF")
        for k in ("supers",) + KEYS:
            if tbl[n][k] != lisp[n][k]:
                print(f"      {k}: tblgen={tbl[n][k]!r}  lisp={lisp[n][k]!r}")

print(f"\n{len(names)} 条记录，{1+len(KEYS)} 个键，{bad} 处分歧")
sys.exit(1 if bad else 0)
