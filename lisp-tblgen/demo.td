class WriteRes<list<string> res> {
  list<string> Resources = res;
  int Latency = 1;
}

def ALU0 : WriteRes<["P73IALU"]> {
  let Latency = 2;
}

multiclass LoadStore<int lat> {
  def _LD : WriteRes<["P23LD"]> { let Latency = lat; }
  def _ST : WriteRes<["P4ST"]> { let Latency = lat; }
}

defm MEM : LoadStore<4>;

def : WriteRes<["P0"]>;
