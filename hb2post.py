# -*- mode: Python; coding: utf-8 -*-
# By Luis Sergio Oliveira a command line utility to extract blog posts from my
# digital programming handbook.

from htmled import HbFile, PostExtractor
import sys
import os
from optparse import OptionParser
from datetime import date, datetime

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


def main():
    options = CadernosOptions()
    hbfauto = HbFileAuto(options.hbfilenames())
    pe = PostExtractor(*hbfauto.hbfs)
    posts = pe.getPosts(options.startdate(), options.enddate())
    for post in posts:
        print post


if __name__ == "__main__":
    main()
