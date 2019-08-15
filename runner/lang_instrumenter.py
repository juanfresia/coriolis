#!/usr/bin/env python3

import re
import os

from common import checkpoint_table

class FileInstrumenter:
    def __init__(self, checkpoint_file, debug=False):
        self.checkpoint_table = checkpoint_table.CheckpointTable(checkpoint_file)
        self.debug = debug

    def _debug_message(self, msg):
        if self.debug: print(msg)

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
    def __init__(self, checkpoints, debug=False):
        super().__init__(checkpoints, debug)

    def instrument_line(self, line):
        return line

    def can_instrument(self, path):
        self._debug_message("[NoOp] Can instrument?: {}".format(path))
        return False

class LanguageCInstrumenter(FileInstrumenter):
    type_to_format = {
        "string": " %s",
        "int":    " %d",
        "float":  " %f"
    }

    def __init__(self, checkpoints, debug=False):
        super().__init__(checkpoints, debug)
        self.pattern = re.compile(r'^.*// @(\w*).*')
        self.left_spaces = re.compile(r'^\s*')

    def format_logging_line(self, args):
        log_line = "coriolis_logger_write(\""
        format_string = ""
        argument_string = ""
        
        try:
            arg_types = self.checkpoint_table.get_checkpoint(args[0]).get_arg_types()
        except Exception as e:
            self._debug_message("[C] {}".format(e))
            raise Exception
        
        if len(args[1:]) != len(arg_types):
            self._debug_message("[C] arguments for {} dont match".format(args[0]))
            raise Exception

        format_string = " ".join(["%s"] + [LanguageCInstrumenter.type_to_format[t] for t in arg_types])
        args[0] = "\"{}\"".format(args[0])
        argument_string = ", ".join(args)

        log_line += (format_string + "\", " + argument_string + ");\n")

        return log_line

    def can_instrument(self, path):
        self._debug_message("[C] Can instrument?: {}".format(path))
        ext = os.path.splitext(path)[-1].lower()
        return ext in [".c", ".h"]

    def instrument_file_inline(self, path):
        self._debug_message("[C] Instrumenting: ".format(path))
        super().instrument_file_inline(path)

    def instrument_line(self, line):
        match = self.pattern.match(line)
        if match:
            indentation = self.left_spaces.match(line).group()
            self._debug_message("[C] Matched line is:\n{}".format(line))

            log_line = line
            if match.group(1) == "checkpoint":
                line_args = line.replace("//", "").replace("@checkpoint", "").split()
                if len(line_args):
                    try:
                        log_line = self.format_logging_line(line_args)
                        log_line = indentation + log_line
                    except:
                        log_line = line

                self._debug_message("[C] New line is:\n{}".format(log_line))
            elif match.group(1) == "has_checkpoints":
                self._debug_message("[C] Other new line is:\n{}".format(line))
                log_line = '#include \"coriolis_logger.h\"\n'
            return log_line

        return line

class LanguagePyInstrumenter(FileInstrumenter):
    def __init__(self, checkpoints, debug=False):
        super().__init__(checkpoints, debug)
        self.pattern = re.compile(r'^.*# @(\w*).*')
        self.left_spaces = re.compile(r'^\s*')

    def format_logging_line(self, args):
        log_line = "coriolis_logger_write(\""
        format_string = ""
        argument_string = ""

        try:
            arg_types = self.checkpoint_table.get_checkpoint(args[0]).get_arg_types()
        except Exception as e:
            self._debug_message("[Py] {}".format(e))
            raise Exception

        if len(args[1:]) != len(arg_types):
            self._debug_message("[Py] arguments for {} dont match".format(args[0]))
            raise Exception

        format_string = " ".join(["{}"] + ["{} " for t in arg_types])
        args[0] = "\"{}\"".format(args[0])
        argument_string = ", ".join(args)

        log_line += (format_string + "\".format(" + argument_string + "))\n")

        return log_line

    def can_instrument(self, path):
        self._debug_message("[Py] Can instrument?: {}".format(path))
        ext = os.path.splitext(path)[-1].lower()
        return ext in [".py"]

    def instrument_file_inline(self, path):
        self._debug_message("[Py] Instrumenting: ".format(path))
        super().instrument_file_inline(path)

    def instrument_line(self, line):
        match = self.pattern.match(line)
        if match:
            indentation = self.left_spaces.match(line).group()
            self._debug_message("[Py] Matched line is:\n{}".format(line))

            log_line = line
            if match.group(1) == "checkpoint":
                line_args = line.replace("#", "").replace("@checkpoint", "").split()
                if len(line_args):
                    try:
                        log_line = self.format_logging_line(line_args)
                        log_line = indentation + log_line
                    except:
                        log_line = line

                self._debug_message("[Py] New line is:\n{}".format(log_line))
            elif match.group(1) == "has_checkpoints":
                self._debug_message("[Py] Other new line is:\n{}".format(line))
                log_line = 'from coriolis_logger import *\n'
            return log_line

        return line

LANGUAGES = {
    'c': LanguageCInstrumenter,
    'py': LanguagePyInstrumenter,
    'noop': NoOpInstrumenter
}

def get_file_instrumenter(lang, checkpoints):
    if lang in LANGUAGES.keys():
        return LANGUAGES[lang](checkpoints, True)
    return LANGUAGES['noop'](checkpoints)
