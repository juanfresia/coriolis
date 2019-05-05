#!/usr/bin/env python3

import re
import os

import breakpoint

class FileInstrumenter:
    def __init__(self, breakpoint_file):
        self.breakpoints = breakpoint.parse_from_file(breakpoint_file)

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
    type_to_format = {
        "string": " %s",
        "int":    " %d",
        "float":  " %f"
    }

    def __init__(self, breakpoints):
        super().__init__(breakpoints)

        self.pattern = re.compile(r'^.*// @(\w*).*')
        self.left_spaces = re.compile(r'^\s*')

    def format_logging_line(self, args):
        log_line = "longstrider_write(\""

        format_string = ""
        argument_string = ""
        
        brk_name = args[0]

        if not brk_name in self.breakpoints:
            print("[C] Breakpoint {} not found".format(brk_name))
            raise Exception

        brk = self.breakpoints[brk_name]
        if len(args[1:]) != len(brk.args):
            print("[C] arguments for {} dont match".format(brk_name))
            raise Exception

        format_string = " ".join(["%s"] + [LanguageCInstrumenter.type_to_format[arg.type] for arg in brk.args])
        args[0] = "\"{}\"".format(args[0])
        argument_string = ", ".join(args)

        log_line += format_string + "\", "
        log_line += argument_string
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
                if len(line_args):
                    try:
                        log_line = self.format_logging_line(line_args)
                        log_line = indentation + log_line
                    except:
                        log_line = line

                print("[C] New line is: \n", log_line)
            elif match.group(1) == "loginclude":
                print("[C] Other new line is: \n", line)
                log_line = '#include \"longstrider.h\"'
            return log_line

        return line

LANGUAGES = {'c': LanguageCInstrumenter,
             'noop': NoOpInstrumenter}

def get_file_instrumenter(lang, breakpoints):
    if lang in LANGUAGES.keys():
        return LANGUAGES[lang](breakpoints)
    return LANGUAGES['noop'](breakpoints)

