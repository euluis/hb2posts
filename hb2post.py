# -*- mode: Python; coding: utf-8 -*-
# By Luis Sergio Oliveira a command line utility to extract blog posts from my
# digital programming handbook.

from htmled import HbFile, PostExtractor
import sys
import os
from optparse import OptionParser
from datetime import date, datetime
import unittest
import re

class CadernosOptions:
    def __init__(self, args=sys.argv[1:]):
        parser = OptionParser()
        parser.add_option('-s', '--startdate', default=date.today().__str__(),
                          help='the start date of the date interval for which to get posts, inclusive')
        parser.add_option('-e', '--enddate', default=date.today().__str__(),
                          help='the end date of the date interval for which to get posts, inclusive')
        parser.add_option('--handbook', default='programacao',
                          help="the handbook from which you want to retrieve posts: "
                          "cpp, ensino, idiota, pessoal, programacao or web [default: %default")
        parser.add_option('-t', '--tests', action='store_true', default=False,
                          help='execute the automated tests of this module and exit')
        (self.options, args) = parser.parse_args(args)

    def hbfilenames(self):
        baseHandbooksDir = os.getenv('HOME') + '/documentos/cadernos/'
        if self.options.handbook == 'programacao':
            handbookDir = baseHandbooksDir + 'programacao/'
            filenames = [handbookDir + 'parte01.html']
            for i in range(2,6):
                filenames.append(handbookDir + 'ficheiro0' + str(i) + '.html')
            return filenames
        pass

    def parseIsoDate(self, strIsoDate):
        return datetime.strptime(strIsoDate, '%Y-%m-%d').date()

    def startdate(self):
        return self.parseIsoDate(self.options.startdate)

    def enddate(self):
        return self.parseIsoDate(self.options.enddate)

    def tests(self):
        return self.options.tests

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

def getPostsFromHbFile(hbfilename, startDate, endDate):
    f = file(hbfilename)
    pe = PostExtractor(HbFile(f))
    f.close()
    return pe.getPosts(startDate, endDate)

class HbFileAuto():
    def __init__(self, filenames):
        if filenames == None or len(filenames) == 0:
            raise ValueError(
                "'filenames' must be a list containing at least one file name. It is: '"\
                    + str(filenames) + "'")
        self.filenames = filenames
        self.createHbFiles(filenames)

    def createHbFiles(self, fns):
        self.hbfs = []
        for fn in fns:
            self.hbfs.append(self.hbf(fn))

    def hbf(self, fn):
        f = self.openFile(fn)
        hbf = self.createHbFile(f)
        self.closeFile(f)
        return hbf

    def openFile(self, fn):
        return file(fn)

    def closeFile(self, f):
        f.close()

    def createHbFile(self, f):
        return HbFile(f)

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

def main():
    options = CadernosOptions()
    if options.tests():
        import hb2post
        unittest.main(module=hb2post, argv=[''])
    else:
        hbfauto = HbFileAuto(options.hbfilenames())
        pe = PostExtractor(*hbfauto.hbfs)
        posts = pe.getPosts(options.startdate(), options.enddate())
        for post in posts:
            print post

if __name__ == "__main__":
    main()
