#!/usr/bin/env python3

from common.printer import CoriolisPrinter


class InstrumenterPrinter(CoriolisPrinter):
    def __init__(self, using_verbosity=False):
        super().__init__(using_verbosity)

    def print_instrument_summary(self, source, destination, language, checkpoints):
        self._print_over_separator("INSTRUMENTING CODE")
        self._print_left_right_aligned("Source:", source)
        self._print_left_right_aligned("Destination:", destination)
        self._print_left_right_aligned("Language:", language)
        self._print_left_right_aligned("Checkpoints:", checkpoints)
