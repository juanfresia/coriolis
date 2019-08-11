import unittest

from runner.lang_instrumenter import *


class TestNoOpInstrumenter(unittest.TestCase):
    def test_file(self):
        r = NoOpInstrumenter('/vagrant/resources/prod_cons.chk').can_instrument("")
        self.assertEqual(r, False)

class TestCInstrumenter(unittest.TestCase):
    def test_normal_line(self):
        l = LanguageCInstrumenter('/vagrant/resources/prod_cons.chk').instrument_line('printf("Hello world")')
        self.assertEqual(l, 'printf("Hello world")')

    def test_checkpoint_line(self):
        l = LanguageCInstrumenter('/vagrant/resources/prod_cons.chk').instrument_line('// @checkpoint produce 1 2')
        self.assertEqual(l, 'coriolis_logger_write("%s  %d  %d", "produce", 1, 2);\n')

    def test_checkpoint_not_in_table(self):
        l = LanguageCInstrumenter('/vagrant/resources/prod_cons.chk').instrument_line('// @checkpoint magic 8')
        self.assertEqual(l, '// @checkpoint magic 8')

    def test_line_without_annotation(self):
        l = LanguageCInstrumenter("/vagrant/resources/prod_cons.chk").instrument_line("// checkpoint produce 1 2")
        self.assertEqual(l, '// checkpoint produce 1 2')

if __name__ == '__main__':
    unittest.main()