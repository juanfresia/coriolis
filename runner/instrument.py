#!/usr/bin/env python3

import argparse
import os
import distutils.dir_util

from runner import lang_instrumenter


class FullPaths(argparse.Action):
    """Expand user- and relative-paths"""

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest,
                os.path.abspath(os.path.expanduser(values[0])))


class Instrumenter:
    def __init__(self, language, checkpoints):
        self.instrumenter = lang_instrumenter.get_file_instrumenter(language, checkpoints)
        print(self.instrumenter.__dict__)

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


if __name__ == "__main__":
    # Set arguments
    CURDIR = os.getcwd()
    parser = argparse.ArgumentParser(description='Instrument code.')
    parser.add_argument('-s', '--source', metavar='source', nargs=1,
                        help='Source directory', default=CURDIR, action=FullPaths)
    parser.add_argument('-d', '--destination', metavar='destination', nargs=1,
                        help='Destination directory', default=CURDIR + "/out/", action=FullPaths)
    parser.add_argument('-l', '--language', metavar='language', nargs=1,
                        help='Source code language', default='c', choices=["c", "cpp", "py", "rs", "noop"])
    parser.add_argument('-c', '--checkpoints', metavar='checkpoints', nargs=1,
                        action=FullPaths, help='Checkpoint list file',
                        default='{}/test.chk'.format(CURDIR))

    # Parse and log captured arguments
    args = parser.parse_args()

    print("Source: ", args.source)
    print("Destination: ", args.destination)
    print("Language: ", args.language)
    print("Checkpoints: ", args.checkpoints)

    inst = Instrumenter(args.language[0], args.checkpoints)
    inst.instrument(args.source, args.destination)

    # TODO: Remove this (it copies the coriolis logger)
    distutils.dir_util.copy_tree("/vagrant/runner/libs/", args.destination)
