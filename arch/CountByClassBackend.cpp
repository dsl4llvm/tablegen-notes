//===- CountByClassBackend.cpp - count records per class ------------------===//
//
// Part of the LLVM Project, under the Apache License v2.0 with LLVM Exceptions.
// See https://llvm.org/LICENSE.txt for license information.
// SPDX-License-Identifier: Apache-2.0 WITH LLVM-exception
//
//===----------------------------------------------------------------------===//

#include "llvm/ADT/StringRef.h"
#include "llvm/TableGen/Record.h"
#include "llvm/TableGen/TableGenBackend.h"

using namespace llvm;

namespace {

class CountByClassEmitter {
  const RecordKeeper &Records;

public:
  CountByClassEmitter(const RecordKeeper &RK) : Records(RK) {}
  void run(raw_ostream &OS);
};

} // namespace

void CountByClassEmitter::run(raw_ostream &OS) {
  emitSourceFileHeader("Records per class", OS);

  for (const Record *C : Records.getClasses())
    OS << C->getName() << " "
       << Records.getAllDerivedDefinitions(C->getName()).size() << "\n";
}

static TableGen::Emitter::OptClass<CountByClassEmitter>
    X("gen-count-by-class", "Count records derived from each class");
