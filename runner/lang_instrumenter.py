#!/usr/bin/env python3

import re
import os

from common import checkpoint_table

class FileInstrumenter:
    def __init__(self, checkpoint_file):
        self.checkpoint_table = checkpoint_table.CheckpointTable(checkpoint_file)

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

    def __init__(self, checkpoints):
        super().__init__(checkpoints)
        self.pattern = re.compile(r'^.*// @(\w*).*')
        self.left_spaces = re.compile(r'^\s*')

    def format_logging_line(self, args):
        log_line = "longstrider_write(\""
        format_string = ""
        argument_string = ""
        
        try:
            arg_types = self.checkpoint_table.get_checkpoint(args[0]).get_arg_types()
        except Exception as e:
            print("[C] {}".format(e))
            raise Exception
        
        if len(args[1:]) != len(arg_types):
            print("[C] arguments for {} dont match".format(args[0]))
            raise Exception

        format_string = " ".join(["%s"] + [LanguageCInstrumenter.type_to_format[t] for t in arg_types])
        args[0] = "\"{}\"".format(args[0])
        argument_string = ", ".join(args)

        log_line += (format_string + "\", " + argument_string + ");\n")

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
            if match.group(1) == "checkpoint":
                line_args = line.replace("//", "").replace("@checkpoint", "").split()
                if len(line_args):
                    try:
                        log_line = self.format_logging_line(line_args)
                        log_line = indentation + log_line
                    except:
                        log_line = line

                print("[C] New line is: \n", log_line)
            elif match.group(1) == "has_checkpoints":
                print("[C] Other new line is: \n", line)
                log_line = '#include \"longstrider.h\"'
            return log_line

        return line

LANGUAGES = {
    'c': LanguageCInstrumenter,
    'noop': NoOpInstrumenter
}

def get_file_instrumenter(lang, checkpoints):
    if lang in LANGUAGES.keys():
        return LANGUAGES[lang](checkpoints)
    return LANGUAGES['noop'](checkpoints)
