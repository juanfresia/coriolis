#!/usr/bin/env python3

class Argument:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __str__(self):
        return ':'.join([self.name, self.type])

class Breakpoint:
    def __init__(self, name, args=None):
        self.name = name
        if not args:
            args = []
        self.args = args

    def add_arg(self, arg):
        self.args.append(arg)

    def __str__(self):
        return ' '.join([self.name] + [str(a) for a in self.args])

def parse_argument(str):
    name, type = str.split(':')
    return Argument(name, type)

def parse_breakpoint(str):
    words = str.split()
    brk = Breakpoint(words[0])
    if len(words) > 1:
        for arg in words[1:]:
            brk.add_arg(parse_argument(arg))

    return brk

def parse_from_file(file):
    with open(file, 'r') as f:
        lines = f.readlines()

    # Keep only blank lines
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if line]

    # Ignore lines starting with '#'
    lines = [line for line in lines if line[0] != '#']

    brks = {}

    for line in lines:
        brk = parse_breakpoint(line)
        brks[brk.name] = brk

    return brks

if __name__ == "__main__":
    print(parse_argument("name:lala"))
    print(parse_breakpoint("lala name:lala yey:sup"))
