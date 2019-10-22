import unittest

from runner.lang_instrumenter import *


class TestNoOpInstrumenter(unittest.TestCase):
    def test_file(self):
        r = NoOpInstrumenter('./resources//prod_cons.chk').can_instrument("")
        self.assertFalse(r)

class TestCInstrumenter(unittest.TestCase):
    def test_can_instrument(self):
        l = LanguageCInstrumenter('./resources//prod_cons.chk')
        self.assertTrue(l.can_instrument("test.c"))
        self.assertTrue(l.can_instrument("test.h"))
        self.assertFalse(l.can_instrument("test.py"))

    def test_normal_line(self):
        l = LanguageCInstrumenter('./resources//prod_cons.chk').instrument_line('printf("Hello world");')
        self.assertEqual(l, 'printf("Hello world");')

    def test_checkpoint_line(self):
        l = LanguageCInstrumenter('./resources//prod_cons.chk').instrument_line('// @checkpoint produce 1 2')
        self.assertEqual(l, 'coriolis_logger_write("%s  %d  %d", "produce", 1, 2);\n')

    def test_checkpoint_not_in_table(self):
        l = LanguageCInstrumenter('./resources//prod_cons.chk').instrument_line('// @checkpoint magic 8')
        self.assertEqual(l, '// @checkpoint magic 8')

    def test_line_without_annotation(self):
        l = LanguageCInstrumenter("./resources//prod_cons.chk").instrument_line("// checkpoint produce 1 2")
        self.assertEqual(l, '// checkpoint produce 1 2')

class TestCPPInstrumenter(unittest.TestCase):
    def test_can_instrument(self):
        l = LanguageCppInstrumenter('./resources//prod_cons.chk')
        self.assertTrue(l.can_instrument("test.cpp"))
        self.assertTrue(l.can_instrument("test.h"))
        self.assertFalse(l.can_instrument("test.py"))

    def test_normal_line(self):
        l = LanguageCppInstrumenter('./resources//prod_cons.chk').instrument_line('printf("Hello world");')
        self.assertEqual(l, 'printf("Hello world");')

    def test_checkpoint_line(self):
        l = LanguageCppInstrumenter('./resources//prod_cons.chk').instrument_line('// @checkpoint produce 1 2')
        self.assertEqual(l, 'coriolis_logger_write("%s  %d  %d", (char*) "produce", 1, 2);\n')

    def test_checkpoint_not_in_table(self):
        l = LanguageCppInstrumenter('./resources//prod_cons.chk').instrument_line('// @checkpoint magic 8')
        self.assertEqual(l, '// @checkpoint magic 8')

    def test_line_without_annotation(self):
        l = LanguageCppInstrumenter("./resources//prod_cons.chk").instrument_line("// checkpoint produce 1 2")
        self.assertEqual(l, '// checkpoint produce 1 2')

class TestPyInstrumenter(unittest.TestCase):
    def test_can_instrument(self):
        l = LanguagePyInstrumenter('./resources//prod_cons.chk')
        self.assertTrue(l.can_instrument("test.py"))
        self.assertFalse(l.can_instrument("test.c"))

    def test_normal_line(self):
        l = LanguagePyInstrumenter('./resources//prod_cons.chk').instrument_line('print("Hello world")')
        self.assertEqual(l, 'print("Hello world")')

    def test_checkpoint_line(self):
        l = LanguagePyInstrumenter('./resources//prod_cons.chk').instrument_line('# @checkpoint produce 1 2')
        self.assertEqual(l, 'coriolis_logger_write("{}  {}  {}".format("produce", 1, 2))\n')

    def test_checkpoint_not_in_table(self):
        l = LanguagePyInstrumenter('./resources//prod_cons.chk').instrument_line('# @checkpoint magic 8')
        self.assertEqual(l, '# @checkpoint magic 8')

    def test_line_without_annotation(self):
        l = LanguagePyInstrumenter("./resources//prod_cons.chk").instrument_line("# checkpoint produce 1 2")
        self.assertEqual(l, '# checkpoint produce 1 2')

class TestRustInstrumenter(unittest.TestCase):
    def test_can_instrument(self):
        l = LanguageRustInstrumenter('./resources//prod_cons.chk')
        self.assertTrue(l.can_instrument("test.rs"))
        self.assertFalse(l.can_instrument("test.py"))

    def test_normal_line(self):
        l = LanguageRustInstrumenter('./resources//prod_cons.chk').instrument_line('println!("Hello world");')
        self.assertEqual(l, 'println!("Hello world");')

    def test_checkpoint_line(self):
        l = LanguageRustInstrumenter('./resources//prod_cons.chk').instrument_line('// @checkpoint produce 1 2')
        self.assertEqual(l, 'coriolis_logger::coriolis_logger_write(format!("{}  {}  {}\\n", "produce", 1, 2));\n')

    def test_checkpoint_not_in_table(self):
        l = LanguageRustInstrumenter('./resources//prod_cons.chk').instrument_line('// @checkpoint magic 8')
        self.assertEqual(l, '// @checkpoint magic 8')

    def test_line_without_annotation(self):
        l = LanguageRustInstrumenter("./resources//prod_cons.chk").instrument_line("// checkpoint produce 1 2")
        self.assertEqual(l, '// checkpoint produce 1 2')

if __name__ == '__main__':
    unittest.main(buffer=True)