TBLGEN ?= llvm-tblgen

all: parser_gen.py GRAMMAR.md
	python3 run_tests.py

expr.json: expr.td
	$(TBLGEN) -dump-json $< -o $@

parser_gen.py: expr.json
	python3 tools/gen_parser.py $< $@

GRAMMAR.md: expr.json
	python3 tools/gen_doc.py $< $@

clean:
	$(RM) expr.json parser_gen.py GRAMMAR.md
.PHONY: all clean
