#!/usr/bin/make -f
TBLGEN ?= llvm-tblgen

.PHONY: test clean
test:
	@TBLGEN="$(TBLGEN)" ./verify.sh

clean:
	@$(MAKE) -C little-language clean
