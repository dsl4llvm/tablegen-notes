//===-- expr.td - 一个表达式语言的定义（元模型 + 模型） --------*- TableGen -*-===//
//
// 这份文件里没有一行 C++，也没有一行 "怎么求值"。
// 它只描述五件事：有哪些 token、有哪些节点、谁比谁紧、往哪边结合、谁来算。
//
// 语义（semantics）字段存的是名字，不是代码——它是给后端的接口约定。
//
//===----------------------------------------------------------------------===//

// ---------------------------------------------------------------------------
// 词法层：终结符
// ---------------------------------------------------------------------------

class Token<string name_, string pattern_> {
  string Name     = name_;
  string Pattern  = pattern_;
}

def tok_int   : Token<"INT",   "[0-9]+">;
def tok_float : Token<"FLOAT", "[0-9]+\\.[0-9]+">;
def tok_ident : Token<"IDENT", "[A-Za-z_][A-Za-z0-9_]*">;

// ---------------------------------------------------------------------------
// 抽象语法层：节点种类
//   这不是"写起来长什么样"，是"解析完长什么样"。
// ---------------------------------------------------------------------------

class NodeKind<string name_> {
  string Name = name_;
}

def nk_literal : NodeKind<"Literal">;   // 叶子：数字
def nk_var     : NodeKind<"Var">;       // 叶子：变量
def nk_binary  : NodeKind<"Binary">;    // 二元：lhs op rhs
def nk_unary   : NodeKind<"Unary">;     // 一元：op operand
def nk_postfix : NodeKind<"Postfix">;   // 后缀：operand op

// ---------------------------------------------------------------------------
// 具体语法层：运算符
//   Precedence 越大越紧；Assoc 决定同级的结合方向。
//   Semantics 是交给后端的名字——本文件不解释它。
// ---------------------------------------------------------------------------

class Operator<string spelling_, int precedence_, string assoc_,
               NodeKind kind_, string semantics_> {
  string  Spelling   = spelling_;
  int     Precedence = precedence_;
  string  Assoc      = assoc_;      // "left" | "right" | "none"
  string  Kind       = kind_.Name;
  string  Semantics  = semantics_;
}

// 一元前缀：-x。给一个"比乘紧、比幂松"的位置，是为了让 -2^2 == -(2^2)。
class PrefixOp<string spelling_, int precedence_, string semantics_>
    : Operator<spelling_, precedence_, "right", nk_unary, semantics_>;

// 后缀：x!，最紧。
class PostfixOp<string spelling_, string semantics_>
    : Operator<spelling_, 40, "left", nk_postfix, semantics_>;

// 二元：用 multiclass 一次生成一整族，避免手抄。
multiclass BinOp<string spelling_, int precedence_, string assoc_, string sem_> {
  def VAR : Operator<spelling_, precedence_, assoc_, nk_binary, sem_>;
}

defm op_add : BinOp<"+", 10, "left",  "add">;
defm op_sub : BinOp<"-", 10, "left",  "sub">;
defm op_mul : BinOp<"*", 20, "left",  "mul">;
defm op_div : BinOp<"/", 20, "left",  "div">;
defm op_pow : BinOp<"^", 30, "right", "pow">;

def op_neg : PrefixOp<"-", 25, "neg">;
def op_fac : PostfixOp<"!", "fac">;

// ---------------------------------------------------------------------------
// 括号：不是运算符，是语法结构。
//   把它声明成 Operator 是个常见错误——它没有优先级，也不产生节点。
//   单独一类，后端才知道"这里要递归，然后丢掉括号"。
// ---------------------------------------------------------------------------

class SyntaxForm<string name_, string open_, string close_> {
  string Name  = name_;
  string Open  = open_;
  string Close = close_;
}

def form_paren : SyntaxForm<"Group", "(", ")">;
