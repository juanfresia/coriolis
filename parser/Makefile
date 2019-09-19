
GRAMMAR:=Jarl
GRAMMAR_LOWER:=$(shell echo $(GRAMMAR) | tr A-Z a-z)

RULE_FILE?=example_rule

antlr4:=java -Xmx500M -cp /usr/local/lib/antlr-4.7.1-complete.jar: org.antlr.v4.Tool
grun:=java org.antlr.v4.gui.TestRig

build:
	@$(antlr4) $(GRAMMAR).g4
	@javac $(GRAMMAR)*.java

build_python:
	@$(antlr4) -Dlanguage=Python3 $(GRAMMAR).g4

run:
	@python3 -m JarlParserCLI $(RULE_FILE)

test: build
	@$(grun) $(GRAMMAR) $(GRAMMAR_LOWER) -tree

clean:
	rm *.java *.interp *.tokens *.class
