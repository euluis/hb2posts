# -*- mode: Python; coding: utf-8 -*-
# Automated tests for hb2post Python module, by Luis Sergio Oliveira.

from datetime import date
import unittest
import re
from hb2post import *


class CadernosOptionsTest(unittest.TestCase):
    def options_hbfilenames_match_programacao_hb(self, options):
        self.assertTrue(5 <= len(options.hbfilenames()))
        reStr = '/cadernos/programacao/(?:parte|ficheiro){1}\d{2}.html'
        reCompiled = re.compile(reStr)
        for hbfn in options.hbfilenames():
            assert re.search(reCompiled, hbfn),\
                "\"" + hbfn + "\" doesn't match the regular expression \"" + reStr + "\"."

    def assertDateEquals(self, expectedDate, actualDate):
        assert expectedDate == actualDate, \
            'Expected ' + str(expectedDate) + ', but was ' + str(actualDate) + '.'

    def test_hbfilenames_default(self):
        options = CadernosOptions([])
        self.options_hbfilenames_match_programacao_hb(options)
        self.assertDateEquals(date.today(), options.startdate())
        self.assertDateEquals(date.today(), options.enddate())

    def test_hbfilenames_programacao_start_n_end_date_defined(self):
        options = CadernosOptions(['--handbook', 'programacao', '-s2005-05-10', '-e2005-10-31'])
        self.options_hbfilenames_match_programacao_hb(options)
        self.assertDateEquals(date(2005,5,10), options.startdate())
        self.assertDateEquals(date(2005,10,31), options.enddate())

    def options_hbfilenames_match_idiota_hb(self, options):
        self.assertTrue(2 <= len(options.hbfilenames()))
        reStr = '/cadernos/idiota/ficheiro0[12].html'
        reCompiled = re.compile(reStr)
        for hbfn in options.hbfilenames():
            assert re.search(reCompiled, hbfn),\
                "\"" + hbfn + "\" doesn't match the regular expression \"" + reStr + "\"."

    def test_hbfilenames_idiota_default(self):
        options = CadernosOptions(['--handbook', 'idiota'])
        self.options_hbfilenames_match_idiota_hb(options)
        self.assertDateEquals(date.today(), options.startdate())
        self.assertDateEquals(date.today(), options.enddate())


class HbFileAutoTest(unittest.TestCase):
    def setUp(self):
        self.non_existing_file = 'non_existing_file.html'
        self.non_existing_file_error = IOError("IOError: No such file or directory: '"\
                                                   + self.non_existing_file + "'")
    class HbFileAutoStub(HbFileAuto):
        def __init__(self, test, files):
            self.test = test
            self.openedfiles = []
            self.hbfiles = []
            HbFileAuto.__init__(self, files)
        def openFile(self, fn):
            if self.test.non_existing_file == fn:
                raise self.test.non_existing_file_error
            self.openedfiles.append(fn)
            return fn
        def closeFile(self, f):
            self.openedfiles.remove(f)
        def createHbFile(self, fn):
            assert fn
            self.hbfiles.append(fn)
            return fn

    def test_process_hbfiles_happy_path(self):
        files = ['file1.html', 'file2.html']
        hbfAuto = HbFileAutoTest.HbFileAutoStub(self, files)
        self.assertEquals([], hbfAuto.openedfiles)
        self.assertEquals(files, hbfAuto.hbfiles)

    def test_process_hbfiles_non_existing_file(self):
        files = ['file1.html', self.non_existing_file]
        try:
            hbfAuto = HbFileAutoTest.HbFileAutoStub(self, files)
            self.fail("Expected " + str(self.non_existing_file_error))
        except IOError as e:
            pass # expected

    def test_create_HbFileAuto_with_no_filenames_fails(self):
        files = []
        try:
            HbFileAuto(files)
            self.fail("Expected ValueError: filenames must have at least one element.")
        except ValueError:
            pass


if __name__ == "__main__":
    unittest.main()
