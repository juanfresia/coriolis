
GRAMMAR:=Jarl
GRAMMAR_LOWER:=$(shell echo $(GRAMMAR) | tr A-Z a-z)

RULE_FILE?=parser/example_rule

antlr4:=java -Xmx500M -cp /usr/local/lib/antlr-4.7.1-complete.jar: org.antlr.v4.Tool
grun:=java org.antlr.v4.gui.TestRig

build_java:
	@$(antlr4) $(GRAMMAR).g4
	@javac $(GRAMMAR)*.java
.PHONY: build_java

build:
	@$(antlr4) -Dlanguage=Python3 $(GRAMMAR).g4
.PHONY: build

# This will run from the parent directory... TODO: fixme into a better makefile structure
run:
	cd .. && python3 -m parser.JarlParserCLI $(RULE_FILE)
.PHONY: run

test: build_java
	@$(grun) $(GRAMMAR) $(GRAMMAR_LOWER) -tree
.PHONY: test

clean:
	rm *.java *.interp *.tokens *.class
.PHONY: clean
