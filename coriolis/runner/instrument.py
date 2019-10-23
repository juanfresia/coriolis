#!/usr/bin/env python3

import os
import distutils.dir_util

from runner import lang_instrumenter
from runner.instrumenter_printer import InstrumenterPrinter


class Instrumenter:
    def __init__(self, language, checkpoints, verbose_mode=False):
        self.instrumenter = lang_instrumenter.get_file_instrumenter(language, checkpoints, verbose_mode)
        self.printer = InstrumenterPrinter(verbose_mode)

    def instrument(self, src_dir, dst_dir):
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
    InstrumenterPrinter(args.verbose).print_instrument_summary(args.source, args.destination, args.language[0], args.checkpoints)

    inst = Instrumenter(args.language[0], args.checkpoints, args.verbose)
    inst.instrument(args.source, args.destination)

    # TODO: Remove this (it copies the coriolis logger)
    distutils.dir_util.copy_tree("runner/libs/", args.destination)
