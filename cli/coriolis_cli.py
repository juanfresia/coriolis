#!/usr/bin/env python3

import argparse
import os

from verifier.rule_checker import run_verifier
from common.utils import FullPaths

class CoriolisCLI():
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Coriolis CLI tool')
        self.subcommands = self.parser.add_subparsers()
        self._add_verify_subcomand()

    def _add_verify_subcomand(self):
        CURDIR = os.getcwd()
        verify_parser = self.subcommands.add_parser('verify', description='Verifies concurrent rules based on log file.')
        verify_parser.add_argument('-l', '--log-file', metavar='logfile', nargs=1,
                            action=FullPaths, help='Log file',
                            default='{}/coriolis_run.log'.format(CURDIR))
        verify_parser.add_argument('-c', '--checkpoints', metavar='checkpoints', nargs=1,
                            action=FullPaths, help='Checkpoint list file',
                            default='{}/rules.chk'.format(CURDIR))
        verify_parser.add_argument('-r', '--rules', metavar='rules', nargs=1,
                            action=FullPaths, help='Rules parsed .py file',
                            default='{}/rules.py'.format(CURDIR))
        verify_parser.add_argument('-v', '--verbose',action='store_true', help="Enables verbosity")
        verify_parser.set_defaults(func=run_verifier)

    def parse_args(self):
        return self.parser.parse_args()

if __name__ == "__main__":
    parser = CoriolisCLI()
    args = parser.parse_args()
    args.func(args)
    print(args)
