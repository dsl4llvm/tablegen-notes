class WriteRes<list<string> res> {
  list<string> Resources = res;
  int Latency = 1;
}

def Bad : WriteRes<["P0"]> {
  let Latency = "two";
}
