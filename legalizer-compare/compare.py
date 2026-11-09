#!/usr/bin/env python3
"""比对 -gen-legalizer (C++ 调用链) 与 -gen-legalizer-core (JSON IR)。

把两边都归一化成同一个模型：
    签名 = (守卫归一化文本, ((type_idx, 类型), ...))
然后做集合比对。

用法：compare.py <x86_leg.inc> <x86_core.json>
"""
import json, re, sys, collections

# ------------------------------------------------------------------ 归一化
def norm_type(t):
    t = t.strip()
    m = re.match(r'LLT::scalar\((\d+)\)', t)
    if m: return f"s{m.group(1)}"
    m = re.match(r'LLT::fixed_vector\((\d+),\s*(\w+)\)', t)
    if m:
        n = m.group(2)
        inner = f"s{n}" if n.isdigit() else norm_type(n)
        return f"v{m.group(1)}{inner}"
    if re.match(r'LLT::pointer\(0,.*\)', t): return "p0:*"
    m = re.match(r'X86_(\w+)', t)
    if m: return m.group(1)
    return None


def _split_top(s, op):
    out, depth, cur = [], 0, ""
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "(": depth += 1
        elif ch == ")": depth -= 1
        if depth == 0 and s.startswith(op, i):
            out.append(cur); cur = ""; i += len(op); continue
        cur += ch; i += 1
    out.append(cur)
    return out


def _strip_outer(s):
    while s.startswith("(") and s.endswith(")"):
        depth = 0
        for i, ch in enumerate(s):
            depth += ch == "("
            depth -= ch == ")"
            if depth == 0 and i != len(s) - 1:
                return s
        s = s[1:-1]
    return s


def canon(g):
    """把布尔表达式归一化成可比较的形式：去空格、去外层括号、同层操作数排序。"""
    g = g.strip()
    if not g: return ""
    g = _strip_outer(g).replace(" ", "")
    parts = _split_top(g, "||")
    if len(parts) > 1:
        return "(" + "|".join(sorted(canon(x) for x in parts)) + ")"
    parts = _split_top(g, "&&")
    if len(parts) > 1:
        return "(" + "&".join(sorted(canon(x) for x in parts)) + ")"
    if g.startswith("!"):
        return "!" + canon(g[1:])
    return g


def split_args(s):
    out, depth, cur = [], 0, ""
    for ch in s:
        if ch in "([{": depth += 1
        elif ch in ")]}": depth -= 1
        if ch == "," and depth == 0:
            out.append(cur.strip()); cur = ""
        else:
            cur += ch
    if cur.strip(): out.append(cur.strip())
    return out


# ------------------------------------------------------------------ C++ 侧
class Cpp:
    def __init__(self, path):
        self.feats, self.llt, self.lists, self.rulesets = {}, {}, {}, []
        cur = None
        for i, L in enumerate(open(path, encoding="utf-8").read().splitlines(), 1):
            m = re.match(r'\s*bool (\w+) = (.+);\s*$', L)
            if m: self.feats[m.group(1)] = m.group(2); continue
            m = re.match(r'\s*const LLT (\w+) = (.+);\s*$', L)
            if m: self.llt[m.group(1)] = m.group(2); continue
            m = re.match(r'\s*const std::initializer_list<LLT> (\w+) = \{(.*)\};\s*$', L)
            if m: self.lists[m.group(1)] = split_args(m.group(2)); continue
            m = re.match(r'\s*getActionDefinitionsBuilder\((.*)\)\s*$', L)
            if m:
                cur = {"opcodes": split_args(m.group(1).strip("{} ")), "calls": [], "line": i}
                self.rulesets.append(cur); continue
            m = re.match(r'\s*\.(\w+)\((.*)\);?\s*$', L)
            if m and cur is not None:
                cur["calls"].append((m.group(1), m.group(2), i))

    def expand_guard(self, g):
        """把局部 bool 名替换成它的定义，递归一轮即可。"""
        out = g
        for name, expr in self.feats.items():
            out = re.sub(rf"\b{name}\b", expr, out)
        return out

    def type_of(self, tok, depth=0):
        tok = tok.strip()
        if tok in self.lists:
            return [self.type_of(x, depth + 1) for x in self.lists[tok]]
        if tok in self.llt:
            return self.type_of(self.llt[tok], depth + 1) if depth < 3 else None
        return norm_type(tok)

    def signatures(self):
        """返回 {opcode: {(guard_norm, ((idx,type),...))}} 以及未实现 builder 的 opcode 集合。"""
        sig = collections.defaultdict(set)
        self.all_opcodes = set()
        unsupported = set()
        UNSUP = {"legalForTypesWithMemDesc", "legalForTypeWithAnyImm", "legalForCartesianProduct"}
        for rs in self.rulesets:
            self.all_opcodes.update(rs["opcodes"])
            for name, _, _ in rs["calls"]:
                if name in UNSUP:
                    unsupported.update(rs["opcodes"])
            for name, args, ln in rs["calls"]:
                if name != "legalFor": continue
                parts = split_args(args)
                guard = None if len(parts) == 1 else parts[0]
                types = parts[-1].strip()
                if types.startswith("{") and types.endswith("}"):
                    types = types[1:-1]          # 只剥一层，别把元组的括号剥掉
                elements = split_args(types)
                for e in elements:
                    if e.startswith("{"):                       # 元组：{t0, t1}
                        xs = split_args(e[1:-1])
                        tc = tuple((i, self.type_of(x)) for i, x in enumerate(xs))
                    else:
                        tc = ((0, self.type_of(e)),)
                    if any(t is None for _, t in tc): continue
                    g = self.expand_guard(guard) if guard else ""
                    for op in rs["opcodes"]:
                        sig[op].add((canon(g), tc))
        return sig, unsupported


# ------------------------------------------------------------------ JSON 侧
def json_signatures(path):
    d = json.load(open(path, encoding="utf-8"))
    sig = collections.defaultdict(set)
    stats = {"rulesets": len(d["rulesets"]), "rules": 0, "features": 0,
             "escapes": len(d.get("escapes", [])), "opcodes": 0}
    for rs in d["rulesets"]:
        stats["opcodes"] += len(rs["opcodes"])
        for r in rs["rules"]:
            stats["rules"] += 1
            if r["action"] != "Legal": continue
            typs = []

            def walk(p):
                k = p.get("kind")
                if k == "leaf":
                    if p["name"] == "typeIs":
                        typs.append((p["args"][0], p["args"][1])); return None
                    if p["name"] == "hasFeature":
                        stats["features"] += 1; return p["args"][0]
                    return p["name"]
                if k == "not":
                    inner = walk(p["arg"])
                    return f"!({inner})" if inner else None
                op = "||" if p.get("op") == "any_of" else "&&"
                parts = [x for x in (walk(a) for a in p.get("args", [])) if x]
                if not parts: return None
                return "(" + op.join(parts) + ")" if len(parts) > 1 else parts[0]

            guard = walk(r["predicate"]) or ""
            if not typs: continue
            tc = tuple(sorted(typs))
            for op in rs["opcodes"]:
                sig[op].add((canon(guard), tc))
    return sig, stats, d


# ------------------------------------------------------------------ 比对
def main():
    cpp = Cpp(sys.argv[1])
    csig, unsupported = cpp.signatures()
    jsig, stats, d = json_signatures(sys.argv[2])

    print("L1 结构")
    print(f"  ruleset : C++ {len(cpp.rulesets):>4}   JSON {stats['rulesets']:>4}")
    print(f"  opcode  : C++ {len(cpp.all_opcodes):>4}   JSON {stats['opcodes']:>4}"
          f"   （其中带 legal 规则：C++ {len(csig)} / JSON {len(jsig)}）")
    print(f"  JSON 规则总数 {stats['rules']}，escapes {stats['escapes']}，hasFeature 谓词 {stats['features']}")
    print(f"  config.pointer_width = {d['config']['pointer_width']}")

    print("\nL2 legal 签名比对（守卫 + 类型元组）")
    common = sorted(set(csig) & set(jsig) - unsupported)
    same = [op for op in common if csig[op] == jsig[op]]
    diff = [op for op in common if csig[op] != jsig[op]]
    print(f"  可比 opcode {len(common)}，完全一致 {len(same)}，不一致 {len(diff)}")
    print(f"  排除（使用了本工具未实现的 builder）: {len(unsupported)} 个 opcode → {sorted(unsupported)[:5]}")

    # 差分归类
    only_c, only_j, guard_only = 0, 0, 0
    examples = []
    for op in diff:
        c, j = csig[op], jsig[op]
        ct = {(g, t) for g, t in c}
        jt = {(g, t) for g, t in j}
        oc, oj = ct - jt, jt - ct
        if oc: only_c += 1
        if oj: only_j += 1
        if oc and oj and {t for _, t in oc} == {t for _, t in oj}:
            guard_only += 1
        if len(examples) < 6:
            examples.append((op, sorted(oc)[:2], sorted(oj)[:2]))
    print(f"  差异分类：仅 C++ 有 {only_c} 个 opcode；仅 JSON 有 {only_j} 个；"
          f"类型相同但守卫文本不同 {guard_only} 个")

    def ptr_fix(sig):
        return {(g, tuple((i, "p0:64" if t == "p0:*" else t) for i, t in tc)) for g, tc in sig}
    same2 = [op for op in common if ptr_fix(csig[op]) == jsig[op]]
    print(f"  把 p0:* 归一化成 p0:64 之后：{len(same2)}/{len(common)} 一致")
    for op, oc, oj in examples:
        print(f"    {op}")
        if oc: print(f"      C++ : {oc}")
        if oj: print(f"      JSON: {oj}")


if __name__ == "__main__":
    main()
