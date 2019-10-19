#!/usr/bin/env python3

import argparse
import os

from verifier.rule_checker import run_verifier
from runner.instrument import run_instrumenter
from parser.jarl_parser_cli import run_parser
from common.utils import FullPaths

class CoriolisCLI():
    def __init__(self):
        self.parser = argparse.ArgumentParser(description='Coriolis CLI tool')
        self.subcommands = self.parser.add_subparsers()
        self._add_verify_subcommand()
        self._add_instrument_subcommand()
        self._add_parse_subcommand()
        self.parser.set_defaults(func=self.print_usage)

    def print_usage(self, args):
        # TODO: fill this
        print("Usage: TODO fill-me")

    def _add_verify_subcommand(self):
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

    def _add_instrument_subcommand(self):
        CURDIR = os.getcwd()
        instrument_parser = self.subcommands.add_parser('instrument', description='Instrument code.')
        instrument_parser.add_argument('-s', '--source', metavar='source', nargs=1,
                            help='Source directory', default=CURDIR, action=FullPaths)
        instrument_parser.add_argument('-d', '--destination', metavar='destination', nargs=1,
                            help='Destination directory', default=CURDIR+"/out/", action=FullPaths)
        instrument_parser.add_argument('-l', '--language', metavar='language', nargs=1,
                            help='Source code language', default='c', choices=["c", "cpp", "py", "noop"])
        instrument_parser.add_argument('-c', '--checkpoints', metavar='checkpoints', nargs=1,
                            action=FullPaths, help='Checkpoint list file',
                            default='{}/test.chk'.format(CURDIR))
        instrument_parser.add_argument('-v', '--verbose',action='store_true', help="Enables verbosity")
        instrument_parser.set_defaults(func=run_instrumenter)

    def _add_parse_subcommand(self):
        CURDIR = os.getcwd()
        parse_parser = self.subcommands.add_parser('parse', description='Parse .jarl file.')
        parse_parser.add_argument('rules_file', metavar='file', nargs=1,
                            help='Rules file', action=FullPaths)
        parse_parser.set_defaults(func=run_parser)

    def parse_args(self):
        return self.parser.parse_args()

if __name__ == "__main__":
    parser = CoriolisCLI()
    args = parser.parse_args()
    args.func(args)
