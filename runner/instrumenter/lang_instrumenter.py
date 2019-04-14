#!/usr/bin/env python3

import re
import os

class FileInstrumenter:
    def process_lines(self, lines):
        for n, line in enumerate(lines):
            lines[n] = self.instrument_line(line)
        return lines

    def instrument_file_inline(self, path):
        with open(path, 'r') as f:
            lines = f.readlines()

        lines = self.process_lines(lines)

        with open(path, 'w') as f:
            f.write(''.join(lines))

    def instrument_line(self, line):
        raise NotImplementedError

    def can_instrument(self, path):
        raise NotImplementedError

class NoOpInstrumenter(FileInstrumenter):
    def instrument_line(self, line):
        return line

    def can_instrument(self, path):
        print("[NoOp] Can instrument?: ", path)
        return False

class LanguageCInstrumenter(FileInstrumenter):
    def __init__(self):
        self.pattern = re.compile(r'^.*// @(\w*).*')
        self.left_spaces = re.compile(r'^\s*')

    def format_logging_argument(self, line_args, index):
        # TODO: format arguments properly with %s or %d looking on the table
        if (index == 0) or (index == 2): return "%s", "\"" + line_args[index] + "\""
        return "%d", line_args[index]

    def format_logging_line(self, args):
        log_line = "longstrider_write(\""
        for arg in args:
            log_line += " %s"

        for arg in args:
            log_line += ", \"{}\"".format(arg)

        log_line += ");\n"

        return log_line

    def can_instrument(self, path):
        print("[C] Can instrument?: ", path)
        ext = os.path.splitext(path)[-1].lower()
        return ext in ['.c', '.h']

    def instrument_file_inline(self, path):
        print("[C] Instrumenting: ", path)
        super().instrument_file_inline(path)

    def instrument_line(self, line):
        match = self.pattern.match(line)
        if match:
            indentation = self.left_spaces.match(line).group()
            print("[C] Matched line is:\n", line)

            log_line = line
            if match.group(1) == "log":
                line_args = line.replace("//", "").replace("@log", "").split()
                if len(line_args) > 2:
                    log_line = self.format_logging_line(line_args)
                    log_line = indentation + log_line

                print("[C] New line is: \n", log_line)
            elif match.group(1) == "loginclude":
                print("[C] Other new line is: \n", line)
                log_line = '#include \"longstrider.h\"'
            return log_line

        return line

LANGUAGES = {'c': LanguageCInstrumenter(),
             'noop': NoOpInstrumenter()}

def get_file_instrumenter(lang):
    if lang in LANGUAGES.keys():
        return LANGUAGES[lang]
    return LANGUAGES['noop']

