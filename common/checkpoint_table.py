#!/usr/bin/env python3

class Argument:
    def __init__(self, name, type):
        self.name = name
        self.type = type

    def __str__(self):
        return ':'.join([self.name, self.type])

class Checkpoint:
    def __init__(self, name, args=None):
        self.name = name
        if not args:
            args = []
        self.args = args

    def add_arg(self, arg):
        self.args.append(arg)
    
    def get_arg_types(self):
        return [arg.type for arg in self.args]

    def __str__(self):
        return ' '.join([self.name] + [str(a) for a in self.args])

class CheckpointTable:
    def __init__(self, file):
        self.checkpoints = {}
        self.parse_file(file)
    
    def parse_argument(self, str):
        name, type = str.split(':')
        return Argument(name, type)

    def parse_checkpoint(self, str):
        words = str.split()
        chk = Checkpoint(words[0])
        if len(words) > 1:
            for arg in words[1:]:
                chk.add_arg(self.parse_argument(arg))

        return chk
       
    def get_checkpoint(self, checkpoint_name):
        if not checkpoint_name in self.checkpoints:
            raise Exception("Checkpoint {} not found".format(checkpoint_name))
        return self.checkpoints[checkpoint_name]

    def parse_file(self, file):
        with open(file, 'r') as f:
            lines = f.readlines()

        # Keep only non-blank lines
        lines = [line.strip() for line in lines]
        lines = [line for line in lines if line]
        # Ignore lines starting with '#'
        lines = [line for line in lines if line[0] != '#']

        for line in lines:
            chk = self.parse_checkpoint(line)
            self.checkpoints[chk.name] = chk

if __name__ == "__main__":
    chkt = CheckpointTable()
    print(chkt.parse_argument("name:lala"))
    print(chkt.parse_checkpoint("lala name:lala yey:sup"))
