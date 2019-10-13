#!/usr/bin/env python3

import os
import distutils.dir_util

from runner import lang_instrumenter


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


def run_instrumenter(args):
    print("Source: ", args.source)
    print("Destination: ", args.destination)
    print("Language: ", args.language)
    print("Checkpoints: ", args.checkpoints)

    inst = Instrumenter(args.language[0], args.checkpoints)
    inst.instrument(args.source, args.destination)

    # TODO: Remove this (it copies the coriolis logger)
    distutils.dir_util.copy_tree("/vagrant/runner/libs/", args.destination)
