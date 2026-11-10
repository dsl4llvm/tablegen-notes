class Instr<string mnemonic, bits<8> opcode> {
  string Mnemonic = mnemonic;
  bits<8> Opcode = opcode;
}
def ADD : Instr<"add", 0x01>;
def SUB : Instr<"sub", 0x02>;
