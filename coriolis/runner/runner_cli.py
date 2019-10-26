#!/usr/bin/env python3

import os
import distutils.dir_util

from runner import lang_instrumenter
from runner.runner_printer import RunnerPrinter


class Runner:
    def __init__(self, language, checkpoints, verbose_mode=False):
        self.instrumenter = lang_instrumenter.get_file_instrumenter(language, checkpoints, verbose_mode)
        self.printer = RunnerPrinter(verbose_mode)
        self.language = language
        self.checkpoints = checkpoints

    def instrument(self, src_dir, dst_dir):
        self.printer.print_instrument_summary(src_dir, dst_dir, self.language, self.checkpoints)
        try:
            distutils.dir_util.copy_tree(src_dir, dst_dir)
        except Exception as err:
            print("Error copying files:")
            print("\t", err)
            return

        for dirpath, _, files in os.walk(dst_dir):
            for file in files:
                file = os.path.join(dirpath, file)

                if self.instrumenter.can_instrument(file):
                    self.instrumenter.instrument_file_inline(file)
                    self.printer.print_instrument_file(file, True)
                else:
                    self.printer.print_instrument_file(file, False)


def run_instrumenter(args):
    coriolis_runner = Runner(args.language[0], args.checkpoints, args.verbose)
    coriolis_runner.instrument(args.source, args.destination)
