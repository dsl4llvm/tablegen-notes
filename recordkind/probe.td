// 三组最小实验：TableGen 的"层"由谁强制？
// 用 llvm-tblgen -print-records probe.td 逐组跑（注释掉其它组）

// ---- 组 1：class 继承 def ----
// def D { int x = 1; }
// class C : D;

// ---- 组 2：def 继承 def ----
// def D { int x = 1; }
// def E : D;

// ---- 组 3：同名 class 与 def 共存 ----
def TB { int a = 1; }
class TB { int b = 2; }
def U : TB;
