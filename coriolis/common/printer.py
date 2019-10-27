#!/usr/bin/env python3

from colorama import Fore, Back, Style  # pip3 install colorama
from textwrap import wrap
from math import ceil, floor

SEPARATOR_LENGTH = 96
SEPARATOR = "=" * int(SEPARATOR_LENGTH)


class CoriolisPrinter:
    def __init__(self, using_verbosity=False):
        self.using_verbosity = using_verbosity

    def _print_separator(self):
        print(SEPARATOR)

    def _print_over_separator(self, text):
        #d = (SEPARATOR_LENGTH - len(text) - 2) / 2
        print(SEPARATOR)
        print(text.center(SEPARATOR_LENGTH))
        #print("{} {} {}".format(SEPARATOR[:floor(d)], text, SEPARATOR[-ceil(d):]))
        print(SEPARATOR)

    def _print_left_right_aligned(self, left_text, right_text, left_fore=None, right_fore=None):
        left_text = "{}".format(left_text).ljust(SEPARATOR_LENGTH - len(right_text))
        left_text = left_fore + left_text + Style.RESET_ALL if left_fore else left_text
        right_text = right_fore + right_text + Style.RESET_ALL if right_fore else right_text
        print("{}{}".format(left_text, right_text))

    def _print_wrapped_text(self, text):
        s = wrap(text, SEPARATOR_LENGTH)
        print(*s, sep="\n")
