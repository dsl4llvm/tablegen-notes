def A { int x = 1 ? 10 : 20; }
def B { int y = 0 ? 10 : 20; }
def C { bit flag = 1; int z = flag ? 1 : 2; }
class P<bits<8> v> { int big = !gt(v, 100) ? 1 : 0; }
def D : P<200>;
def E : P<50>;
def Nested { int n = 1 ? 2 : 0 ? 3 : 4; }
def InList { list<int> l = [1 ? 2 : 3, 4]; }
def Str { string s = 1 ? "yes" : "no"; }
def Bits { bits<8> b = 1 ? 0xFF : 0x00; }
def Unset { int u = 1 ? ? : 5; }
