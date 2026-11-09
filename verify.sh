#!/usr/bin/env bash
# 跑一遍不需要额外前置成本的例子。缺 llvm-tblgen / LLVM 源码时自动跳过，并说明原因。
set -uo pipefail
cd "$(dirname "$0")"

TBLGEN="${TBLGEN:-llvm-tblgen}"
LLVM_SRC="${LLVM_SRC:-}"
fail=0
ok()   { printf '  \033[32mPASS\033[0m  %s\n' "$*"; }
bad()  { printf '  \033[31mFAIL\033[0m  %s\n' "$*"; fail=1; }
skip() { printf '  \033[33mSKIP\033[0m  %s\n' "$*"; }

echo
echo "== little-language：87 行 td → 两个后端 =="
if out=$(cd little-language && python3 run_tests.py 2>&1); then
  if grep -q "0 failed" <<<"$out"; then
    ok "$(grep -o '[0-9]* passed, [0-9]* failed' <<<"$out")"
  else
    bad "测试输出里没有 0 failed"; echo "$out" | tail -5
  fi
else
  bad "run_tests.py 退出码非 0"; echo "$out" | tail -5
fi

echo
echo "== recordkind：层是两张 map =="
if command -v "$TBLGEN" >/dev/null 2>&1; then
  if "$TBLGEN" recordkind/probe.td -print-records >/dev/null 2>&1; then
    ok "probe.td 同名 class/def 共存"
  else
    bad "probe.td 应该正常打印"
  fi
  for f in probe1 probe2; do
    msg=$("$TBLGEN" "recordkind/$f.td" -print-records 2>&1)
    if [[ "$msg" == *"Couldn't find class 'D'"* ]]; then
      ok "$f.td 报 Couldn't find class 'D'"
    else
      bad "$f.td 没有报出预期错误"
    fi
  done
else
  skip "找不到 llvm-tblgen（export TBLGEN=/path/to/llvm-tblgen）"
fi

echo
echo "== escape-hatch：量 td 的逃生舱密度 =="
if [ -n "$LLVM_SRC" ] && [ -d "$LLVM_SRC/llvm" ]; then
  python3 escape-hatch/measure_escape.py "$LLVM_SRC" || fail=1
elif [ -d /home/ubuntu/llvm/llvm-project/llvm ]; then
  python3 escape-hatch/measure_escape.py /home/ubuntu/llvm/llvm-project || fail=1
else
  skip "需要一个 llvm-project 源码树（export LLVM_SRC=/path/to/llvm-project）"
fi

echo
echo "== ternary-parser / legalizer-compare =="
skip "ternary-parser 需要打补丁后重编 llvm-tblgen（见该目录 README）"
skip "legalizer-compare 需要带 -gen-legalizer-core 的 llvm-tblgen（尚未上游）"

echo
if [ "$fail" -ne 0 ]; then
  echo "有失败项。"
  exit 1
fi
echo "能跑的都过了。"
