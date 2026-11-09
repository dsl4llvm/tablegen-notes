import sys
from pratt import parse, show, ParseError
from eval import evaluate, EvalError

CASES = [
    ("1 + 2 * 3", 7, {}),
    ("(1 + 2) * 3", 9, {}),
    ("1 - 2 - 3", -4, {}),
    ("2 ^ 3 ^ 2", 512, {}),
    ("-2 ^ 2", -4, {}),
    ("-3!", -6, {}),
    ("2 ^ 3!", 64, {}),
    ("5!", 120, {}),
    ("x * 2", 42, {"x": 21}),
    ("1 / 2", 0.5, {}),
    ("10 - 2 * 3 + 1", 5, {}),
]
ERR = [
    ("1 +", "期望一个表达式"),
    ("(1 + 2", "缺少 ')'"),
    ("1 + + 2", "期望一个表达式"),
    ("y + 1", "未定义的变量"),
    ("(-3)!", "阶乘只接受非负整数"),
]

ok = bad = 0
print(f"{'表达式':<18}{'AST':<26}{'结果':>8}  状态")
print("-" * 64)
for src, want, env in CASES:
    try:
        ast = parse(src)
        got = evaluate(ast, env)
        good = got == want
        ok += good; bad += not good
        print(f"{src:<18}{show(ast):<26}{got:>8}  {'PASS' if good else 'FAIL want ' + str(want)}")
    except Exception as e:
        bad += 1
        print(f"{src:<18}{'-':<26}{'-':>8}  FAIL {type(e).__name__}: {e}")

print("\n负例（必须被拒绝）：")
for src, want in ERR:
    try:
        evaluate(parse(src))
        print(f"  {src!r:<14} FAIL 居然通过了")
        bad += 1
    except (ParseError, EvalError) as e:
        good = want in str(e)
        ok += good; bad += not good
        print(f"  {src!r:<14} {'PASS' if good else 'FAIL'} {type(e).__name__}: {e}")

print(f"\n{ok} passed, {bad} failed")
sys.exit(1 if bad else 0)
