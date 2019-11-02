import unittest

from verifier.verifier_cli import *
from common.utils import *

class VerifierArgs:
    def __init__(self, log_path, checkpoints):
        self.mongo_host = MONGO_DEFAULT_HOST
        self.mongo_port = MONGO_DEFAULT_PORT
        self.verbose = False
        self.log_path = log_path
        self.checkpoints = checkpoints


class TestVerifyProdCons(unittest.TestCase):
    log_file = "resources/prod_cons_1.log"
    checkpoints_file = "resources/prod_cons.chk"
    exec(open("resources/prod_cons_1_rules.py").read())

    def test_all_prod_cons_rules(self):
        args = VerifierArgs(self.log_file, self.checkpoints_file)
        log_passed = run_verifier(args, self.all_rules)
        self.assertTrue(log_passed)


class TestVerifyH2O(unittest.TestCase):
    log_file = "resources/h2o_1.log"
    checkpoints_file = "resources/h2o.chk"
    exec(open("resources/h2o_1_rules.py").read())

    def test_all_h2o_rules(self):
        args = VerifierArgs(self.log_file, self.checkpoints_file)
        log_passed = run_verifier(args, self.all_rules)
        self.assertTrue(log_passed)


class TestVerifySanta(unittest.TestCase):
    log_file = "resources/santa_1.log"
    checkpoints_file = "resources/santa.chk"
    exec(open("resources/santa_1_rules.py").read())

    def test_all_santa_rules(self):
        args = VerifierArgs(self.log_file, self.checkpoints_file)
        log_passed = run_verifier(args, self.all_rules)
        self.assertTrue(log_passed)

if __name__ == '__main__':
    unittest.main(buffer=True)
