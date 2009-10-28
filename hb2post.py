# -*- mode: Python; coding: utf-8 -*-
# By Luis Sergio Oliveira a command line utility to extract blog posts from my
# digital programming handbook.

from htmled import HbFile, PostExtractor
import sys
import os
from optparse import OptionParser
from datetime import date
import unittest

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
        if self.options.handbook == 'programacao':
            return os.getenv('HOME') + '/documentos/cadernos/programacao/ficheiro04.html'
        pass

    def tests(self):
        return self.options.tests

class CadernosOptionsTest(unittest.TestCase):
    def test_hbfilenames_default(self):
        options = CadernosOptions([])
        self.assertEqual('/home/luis/documentos/cadernos/programacao/ficheiro04.html',
                         options.hbfilenames())
    
    def test_hbfilenames_programacao_old_file(self):
        options = CadernosOptions(['--handbook', 'programacao', '-s2005-05-10', '-e2005-10-31'])
        self.assertEqual('/home/luis/documentos/cadernos/programacao/ficheiro03.html',
                         options.hbfilenames())

def main():
    options = CadernosOptions()
    if options.tests():
        import hb2post
        unittest.main(module=hb2post, argv=[''])
    else:
        f = file(options.hbfilenames()[0]) # FIXME
        hbf = HbFile(f)
        f.close()
        pe = PostExtractor(hbf)
        posts = pe.getPosts(options.startdate(), options.enddate())
        for post in posts:
            print post

if __name__ == "__main__":
    main()
