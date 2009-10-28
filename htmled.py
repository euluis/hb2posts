# Python file - http://www.python.org/

# Automation for my HTML and Handbook to blog author's tasks.

import unittest
from datetime import date
import re

class HbFile:
    """A Handbook file, which contains daily entries."""
    def __init__(self, f):
        """HbFile(f) -> hbFile

        Returns the HbFile constructed from the f HTML file.
        """
        assert not f.closed
        self.f = f
        self.parseHbFile()

    def parseHbFile(self):
        parser = HbFileParser(self.f)
        self.dailyEntries = parser.parse()


class HbDailyEntry:
    """A Handbook daily entry, which contains subject entries."""
    def __init__(self, date):
        self.date = date
        self.subjects = []

    def addSubject(self, se):
        self.subjects.append(se)

class HbSubjectEntry:
    """A Handbook subject entry, which contains text for a specific subject."""
    def __init__(self, title, name = None):
        self.title = title
        self.name = name


# Unit tests for the HbFile class.
class HbFileTest(unittest.TestCase):

    def setUp(self):
        self.hbf = HbFile(open("dummy_hbfile.html"))
    
    def testCreation(self):
        assert None != self.hbf

    def testDailyEntries(self):
        assert None != self.hbf.dailyEntries
        self.assertEquals(3, len(self.hbf.dailyEntries))
        assert date(2010, 2, 6) == self.hbf.dailyEntries[0].date
        assert date(2010, 2, 8) == self.hbf.dailyEntries[1].date
        assert date(2010, 5, 16) == self.hbf.dailyEntries[2].date

    def testSubjectEntries(self):
        d1 = self.hbf.dailyEntries[0]
        d2 = self.hbf.dailyEntries[1]
        self.assertEquals(2, len(d1.subjects))
        self.assertEquals(1, len(d2.subjects))

        d1s1Title = 'Idiota gets 1 million euros profit'
        d1s1 = d1.subjects[0]
        self.assertEquals(d1s1Title, d1s1.title)
        
        d1s2Contains = '<p>The release 2.0 of ArgoUML has UML 2.0 support.</p>'
        d1s2 = d1.subjects[1]
        self.assertTrue(d1s2.contents.count(d1s2Contains) > 0)

        d2s1 = d2.subjects[0]
        self.assertEquals(d2.date.isoformat(), d2s1.title)
        self.assertEquals('<p>This daily entry contains no subject entry.</p>',
                          d2s1.contents)

        navParts = '<p><a href="#topo"'
        self.assertEquals(0, d1s2.contents.count(navParts))

    def testSubjectEntriesNames(self):
        des = self.hbf.dailyEntries
        self.assertEquals('idiota_1st_mil', des[0].subjects[0].name)
        self.assertEquals('argo_with_uml2', des[0].subjects[1].name)
        self.assertEquals('2010-02-08', des[1].subjects[0].name)

    def testParsingSentencesLeavesWhitespace(self):
        des = self.hbf.dailyEntries
        self.assertEquals('2010-05-16', des[2].subjects[0].name)
        self.assertEquals('<p>The first sentence. The second sentence.</p>',
                          des[2].subjects[0].contents)



class Post:
    """A weblog post"""
    def __init__(self, date, title, contents, subjname):
        self.date = date
        self.title = title
        self.contents = contents
        self.subjname = subjname

    def __str__(self):
        return 'Date: ' + str(self.date) + '\n' + 'Title: ' + self.title + \
               '\n' + self.contents

    def __cmp__(self, other):
        if other:
            return (self.date - other.date).days
        else:
            return 1

    def __hash__(self):
        return self.date.__hash__() | self.title.__hash__()

    BlogURL = 'http://argonauts-life.blogspot.com/'

    def getPermaLink(self):
        yearNMonth = str(self.date.year) + '/' + \
            str(self.date.month).rjust(2, '0') + '/'
        modTitle = self.title.lower()
        words = modTitle.split()
        modTitle = ''
        for word in words:
            w2 = ''
            for c in word:
                if c.isalnum():
                    w2 += c
            if not w2.isalnum() or self.wordToRemove(w2):
                continue
            tmpModTitle = modTitle
            if len(modTitle) > 0:
                tmpModTitle += '-' + w2
            else:
                tmpModTitle = w2
            if len(tmpModTitle) >= 39:
                break
            modTitle = tmpModTitle
        return Post.BlogURL + yearNMonth + modTitle + '.html'

    def wordToRemove(self, w):
        return w == 'a' or w == 'the' or w == 'ndash'


class TestPost(unittest.TestCase):
    def setUp(self):
        self.title = 'The Title!'
        self.date = date.today()
        self.post = Post(self.date, self.title, 'contents', 'name')
    
    def testStr(self):
        self.assertTrue(str(self.post).count(str(self.date)) == 1)

    def testGetPermaLink(self):
        month = str(self.date.month).rjust(2, '0')
        self.assertEquals(Post.BlogURL + str(self.date.year) + '/' +
                          month + '/' + 'title.html',
                          self.post.getPermaLink())

    def assertCorrectPostPermalink(self, expectedVariablePermalinkPart, title,
                                   year, month, day):
        d = date(year, month, day)
        self.assertEquals(Post.BlogURL + expectedVariablePermalinkPart,
                          Post(d, title, '', 'name').getPermaLink())
    
    def testGetPermaLink4BlogExample01(self):
        self.assertCorrectPostPermalink('2006/02/am-i-software-engineer.html',
                                        'Am I a Software Engineer?', 2006, 2, 1)
    
    def testGetPermaLink4BlogExample02(self):
        self.assertCorrectPostPermalink('2006/02/argouml-next-release.html',
                                        'ArgoUML next release', 2006, 2, 1)
    
    def testGetPermaLink4BlogExample03(self):
        self.assertCorrectPostPermalink('2005/11/starting-with-parameterized-classes.html',
                                        'starting with parameterized classes and UmlUnit',
                                        2005, 11, 24)
    
    def testGetPermaLink4BlogExample04(self):
        self.assertCorrectPostPermalink('2005/10/c-module-documentation.html',
                                        'C++ module documentation', 2005, 10, 14)
    
    def testGetPermaLink4BlogExample05(self):
        self.assertCorrectPostPermalink('2005/08/drop-1-updated-plan-version-5.html',
                                        'Drop 1 updated plan - Version 5', 2005, 8, 18)
    
    def testGetPermaLink4BlogExample06(self):
        self.assertCorrectPostPermalink('2005/06/modelerimpl-and-new-mda-ideas.html',
                                        'ModelerImpl and new MDA ideas', 2005, 6, 20)
    
    def testGetPermaLink4BlogExample07(self):
        self.assertCorrectPostPermalink('2005/05/pluggableimport-implementation-and-4th.html',
                                        'PluggableImport implementation and 4th plan update of reveng drop 1 (also some new ideas)',
                                        2005, 5, 24)
    
    def testGetPermaLink4BlogExample08(self):
        self.assertCorrectPostPermalink('2005/04/fixing-grammar-ii.html',
                                        'fixing the grammar II', 2005, 4, 1)
    
    def testGetPermaLink4BlogExample09(self):
        self.assertCorrectPostPermalink('2005/03/half-way-to-drop-1.html',
                                        'half way to drop 1', 2005, 3, 1)
    
    def testGetPermaLink4BlogExample10(self):
        self.assertCorrectPostPermalink('2005/03/first-c-parser-commit-and-type-bug.html',
                                        'First C++ parser commit and type bug', 2005, 3, 1)
    
    def testGetPermaLink4BlogExample11(self):
        self.assertCorrectPostPermalink('2006/02/htmled-revisited-handbook-entries-to.html',
                                        'htmled revisited &ndash; Handbook entries to blog posts automated',
                                        2006, 2, 6)
    
    def testGetPermaLink4BlogExample12(self):
        self.assertCorrectPostPermalink('2009/09/customizing-eeebuntu-gnulinux-30.html',
                                        'Customizing Eeebuntu GNU/Linux 3.0 Standard into a development environment',
                                        2009, 9, 21)

    def test__hash__fullyInitializedPost(self):
        post = Post(date(2009, 10, 2), 'title', 'contents', 'name')
        self.assertTrue(isinstance(post.__hash__(), int))

    def test__hash__NoneInitializedPost(self):
        post = Post(None, None, None, None)
        self.assertTrue(isinstance(post.__hash__(), int))

    def test__hash__PostWithDateButWithNoneTitle(self):
        post = Post(date(2009, 10, 2), None, None, None)
        self.assertTrue(isinstance(post.__hash__(), int))
    

# The PostExtractor class
class PostExtractor:
    """The PostExtractor class extracts Posts from HbFile instances."""
    def __init__(self, hbf = None):
        self.hbf = hbf

    def getPosts(self, d1 = None, d2 = None):
        posts = []
        for de in self.hbf.dailyEntries:
            for subj in de.subjects:
                postTitle = self.stripTags(subj.title)
                post = Post(de.date, postTitle, subj.contents, subj.name)
                posts.append(post)
        posts.sort()
        self.adaptPostsLinks(posts)
        if d1 != None and d2 != None:
            assert d1 <= d2
        if d1 != None:
            posts = [post for post in posts if d1 <= post.date]
        if d2 != None:
            posts = [post for post in posts if d2 >= post.date]
        return posts

    def adaptPostsLinks(self, posts):
        """adaptPostsLinks(self, posts)
        Adapt the links contained in the posts so that they work in the blog.
        TODO: handle inter-file links in the handbook.
        """
        self.setPostsNames(posts)
        for post in posts:
            start = 0
            internalLinkPos = post.contents.find('<a href="#', start)
            while internalLinkPos != -1:
                nameStart = post.contents.find('#', internalLinkPos) + 1
                name = post.contents[nameStart:post.contents.find('"', nameStart)]
                if post.names.count(name) > 0:
                    internalLinkPos = post.contents.find('<a href="#', nameStart)
                    continue
                linkedPost = self.getLinkedPost(posts, name)
                # if found replace the link with a link to the other post
                if linkedPost:
                    linkReplacer = linkedPost.getPermaLink()
                    if linkedPost.subjname != name:
                        linkReplacer += '#' + name
                    post.contents = post.contents.replace('#' + name, linkReplacer, nameStart - 3)
                internalLinkPos = post.contents.find('<a href="#', nameStart)

    def setPostsNames(self, posts):
        """setPostsNames(posts)
        Add attribute names to all posts, containing the HTML referenceable
        names contained in the posts.
        """
        for post in posts:
            assert(dir(post).count('names') == 0)
            post.names = []
            start = 0
            namePos = post.contents.find('<a name="', start)
            while namePos != -1:
                nameStart = post.contents.find('"', namePos) + 1
                name = post.contents[nameStart: post.contents.find('"', nameStart)]
                post.names.append(name)
                namePos = post.contents.find('<a name="', nameStart)

    def getLinkedPost(self, posts, name):
        for post in posts:
            if post.subjname == name or post.names.count(name) > 0:
                return post
        return None

    def stripTags(self, text):
        """stripTags(text) -> textWithoutTags

        Removes tags (i.e., HTML tags) from text and returns text without tags.
        """
        start = 0
        tagStart = text.find('<')
        if tagStart == -1:
            return text
        twt = ''
        while tagStart != -1:
            twt += text[start: tagStart]
            start = text.find('>', tagStart) + 1
            tagStart = text.find('<', start)
            if tagStart == -1:
                twt += text[start:]
        return twt


# Test cases for the PostExtractor class
class TestPostExtractor(unittest.TestCase):
    def setUp(self):
        self.hbf = HbFile(open('dummy_hbfile.html'))
        self.pe = PostExtractor(self.hbf)
    
    def testCreate(self):
        pe = PostExtractor()
        assert pe.hbf == None
        assert self.pe.hbf == self.hbf

    def testGetPosts(self):
        des = self.hbf.dailyEntries
        self.assertEquals(2, len(des[0].subjects))
        self.assertEquals(1, len(des[1].subjects))
        posts = self.pe.getPosts()
        self.assertEquals(4, len(posts))
        self.assertEquals(date(2010, 2, 6), posts[0].date)
        self.assertEquals(date(2010, 2, 6), posts[1].date)
        self.assertEquals(date(2010, 2, 8), posts[2].date)

    def testGetPostsReturnsOrdered(self):
        d = date(2006, 4, 10)
        newDE = HbDailyEntry(d)
        subj = HbSubjectEntry("subject title")
        subj.name = 'theName'
        subj.contents = '<p>Hello World!</p>'
        newDE.addSubject(subj)
        self.hbf.dailyEntries.append(newDE)
        posts = self.pe.getPosts()
        self.assertEquals(d, posts[0].date)

    def testGetPostsFiltersByDate(self):
        d1 = date(2010, 2, 7)
        d2 = date(2010, 2, 8)
        posts = self.pe.getPosts(d1, d2)
        self.assertEquals(1, len(posts))
        posts = self.pe.getPosts(d1, d1)
        self.assertEquals(0, len(posts))
        posts = self.pe.getPosts(d2, d2)
        self.assertEquals(1, len(posts))
        self.assertEquals(4, len(self.pe.getPosts(date(2010, 2, 6))))

    def testPostLinksAdapted(self):
        des = self.hbf.dailyEntries
        des[0].subjects[0].contents += '<p><a href="#2010-02-08">see this</a></p>'
        posts = self.pe.getPosts()
        contents0 = posts[0].contents
        self.assertTrue(contents0.count('<a href="http://argonauts-life.blogspot.com/2010/02/20100208.html">see this</a>') == 1)

    def testPostLinksAdapted4InternalNames(self):
        des = self.hbf.dailyEntries
        des[0].subjects[0].contents += '<p><a name="subj0_ancor">Subject 0 ancor</a>.</p>'
        des[0].subjects[1].contents += '<p><a href="#subj0_ancor">see this...</a></p>'
        des[0].subjects[1].contents += '<p><a name="subj1_ancor">Subject 1 ancor</a>.</p>'
        des[0].subjects[1].contents += '<p><a href="#subj1_ancor">see my ancor</a>, nothing should be changed!</p>'
        des[1].subjects[0].contents += '<p><a href="#subj0_ancor">Subject 0 ancor</a></p>'
        des[1].subjects[0].contents += '<p><a href="#subj1_ancor">Subject 1 ancor</a></p>'
        posts = self.pe.getPosts()
        contents0 = posts[0].contents
        self.assertEquals(des[0].subjects[0].contents, contents0)
        self.assertEquals(['subj0_ancor'], posts[0].names)
        contents1 = posts[1].contents
        self.assertEquals(1, contents1.count('<a href="' + \
                                             posts[0].getPermaLink() + \
                                             '#subj0_ancor">'))
        self.assertEquals(['subj1_ancor'], posts[1].names)
        self.assertEquals(1, contents1.count('<a href="#subj1_ancor">see my ancor</a>'))
        contents2 = posts[2].contents
        self.assertEquals(1, contents2.count(posts[0].getPermaLink() + '#subj0_ancor"'))
        self.assertEquals(1, contents2.count(posts[1].getPermaLink() + '#subj1_ancor"'))

    def testPostTitleFreeOfTags(self):
        subj = HbSubjectEntry('<code>Xpto</code> testing', 'subj_name')
        subj.contents = 'some contents'
        self.hbf.dailyEntries[1].subjects.append(subj)
        self.pe = PostExtractor(self.hbf)
        posts = self.pe.getPosts()
        self.assertEquals('Xpto testing', posts[3].title)
 

from HTMLParser import HTMLParser

# Base state for the implementation of the Hand-book file parsing finite state
# machine.
class HbFileParsingState:
    def __str__(self):
        return 'Base HbFileParsingState (Illegal)'

    def h2Begin(self, parsing):
        raise StateError('h2Begin', parsing.state)

    def h2End(self, parsing):
        raise StateError('h2End', parsing.state)

    def h3Begin(self, parsing):
        raise StateError('h3Begin', parsing.state)

    def h3End(self, parsing):
        raise StateError('h3End', parsing.state)

    def divEnd(self, parsing):
        raise StateError('divEnd', parsing.state)

    def aBegin(self, parsing, attrs):
        raise StateError('aBegin', parsing.state)

    def tagBegin(self, parsing):
        raise StateError('tagBegin', parsing.state)

    def data(self, parsing, data):
        raise StateError('data', parsing.state)

    def entry(self, parsing):
        pass

    def exit(self, parsing):
        pass


class StateError(RuntimeError):
    def __init__(self, event, state):
        RuntimeError.__init__(self,
            'unexpected "' + event + '" event in state ' + str(state))


class IdleHbFileParsingState(HbFileParsingState):
    def __str__(self):
        return 'Idle'

    def h2Begin(self, parsing):
        parsing.setState2DailyEntry()

    def h2End(self, parsing):
        pass

    def h3Begin(self, parsing):
        pass

    def h3End(self, parsing):
        pass

    def divEnd(self, parsing):
        pass

    def aBegin(self, parsing, attrs):
        pass

    def tagBegin(self, parsing):
        pass

    def data(self, parsing, data):
        pass


class DailyEntryHbFileParsingState(HbFileParsingState):
    def __str__(self):
        return 'DailyEntry'
    
    def h2End(self, parsing):
        pass

    def h3Begin(self, parsing):
        parsing.setState2SubjectEntry()

    def data(self, parsing, data):
        parsing.setDailyEntryDate(data)

    def h2Begin(self, parsing):
        parsing.setState2DailyEntry()

    def aBegin(self, parsing, attrs):
        # no need to handle this since we already have its name which is the
        # same as the date
        pass

    def tagBegin(self, parsing):
        parsing.setState2DefaultSubjectEntryOfDailyEntry()

    def entry(self, parsing):
        parsing.beginDailyEntryHeader()


class DailyEntryContentsHbFileParsingState(HbFileParsingState):
    def __str__(self):
        return 'DailyEntryContents'

    def h3Begin(self, parsing):
        parsing.setState2SubjectEntry()

    def h3End(self, parsing):
        pass

    def aBegin(self, parsing, attrs):
        pass

    def tagBegin(self, parsing):
        parsing.setState2SubjectEntryContents()

    def h2Begin(self, parsing):
        parsing.setState2DailyEntry()

    def divEnd(self, parsing):
        parsing.setState2Idle()


class SubjectEntryHbFileParsingState(DailyEntryContentsHbFileParsingState):
    def __str__(self):
        return 'SubjectEntry'

    def aBegin(self, parsing, attrs):
        parsing.handleABegin(attrs)

    def h3End(self, parsing):
        parsing.setSubjectEntryTitle(None)
        parsing.setState2SubjectEntryContents()

    def tagBegin(self, parsing):
        pass

    def data(self, parsing, data):
        pass

    def entry(self, parsing):
        parsing.beginSubjectEntryHeader()

class DefaultSubjectEntryOfDailyEntryHbFileParsingState(DailyEntryContentsHbFileParsingState):
    def __str__(self):
        return 'DefaultSubjectEntryOfDailyEntry'

    def entry(self, parsing):
        parsing.beginSubjectEntryHeader()
        parsing.setSubjectEntryTitle()

class SubjectEntryContentsHbFileParsingState(DailyEntryContentsHbFileParsingState):
    def __str__(self):
        return "SubjectEntryContents"

    def data(self, parsing, data):
        pass

    def entry(self, parsing):
        parsing.startPos()

    def exit(self, parsing):
        parsing.endPos()

    def tagBegin(self, parsing):
        pass


class HbFileParsing:
    """Implements a Finite State Machine for the Handbook File Parser.
    """
    Idle = IdleHbFileParsingState()
    DailyEntry = DailyEntryHbFileParsingState()
    SubjectEntry = SubjectEntryHbFileParsingState()
    DefaultSubjectEntryOfDailyEntry = \
        DefaultSubjectEntryOfDailyEntryHbFileParsingState()
    SubjectEntryContents = SubjectEntryContentsHbFileParsingState()
    
    def __init__(self, parser):
        self.parser = parser
        self.state = HbFileParsing.Idle
    
    def h2Begin(self):
        self.state.h2Begin(self)

    def h2End(self):
        self.state.h2End(self)

    def h3Begin(self):
        self.state.h3Begin(self)

    def h3End(self):
        self.state.h3End(self)

    def divEnd(self):
        self.state.divEnd(self)

    def aBegin(self, attrs):
        self.state.aBegin(self, attrs)

    def tagBegin(self):
        self.state.tagBegin(self)

    def data(self, data):
        self.state.data(self, data)

    def setState2Idle(self):
        self.state.exit(self)
        self.state = HbFileParsing.Idle
        self.state.entry(self)

    def setState2DailyEntry(self):
        self.state.exit(self)
        self.state = HbFileParsing.DailyEntry
        self.state.entry(self)

    def setState2SubjectEntry(self):
        self.state.exit(self)
        self.state = HbFileParsing.SubjectEntry
        self.state.entry(self)

    def setState2DefaultSubjectEntryOfDailyEntry(self):
        self.state.exit(self)
        self.state = HbFileParsing.DefaultSubjectEntryOfDailyEntry
        self.state.entry(self)
        self.setState2SubjectEntryContents()

    def setState2SubjectEntryContents(self):
        self.state.exit(self)
        self.state = HbFileParsing.SubjectEntryContents
        self.state.entry(self)
    
    def beginDailyEntryHeader(self):
        self.parser.beginDailyEntryHeader()

    def beginSubjectEntryHeader(self):
        self.parser.beginSubjectEntryHeader()

    def setDailyEntryDate(self, data):
        self.parser.setDailyEntryDate(data)

    def setSubjectEntryTitle(self, data = None):
        self.parser.setSubjectEntryTitle(data)

    def handleABegin(self, attrs):
        self.parser.handleABegin(attrs)

    def startPos(self):
        self.parser.startPos()

    def endPos(self):
        self.parser.endPos()


class HbFileParsingTest(unittest.TestCase):
    """Test cases for the HbFileParsing class.
    """
    def setUp(self):
        self.parsing = HbFileParsing(self)
        self.beginDailyEntryHeaderCalled = False
        self.beginSubjectEntryHeaderCalled = False
        self.setDailyEntryDateCalled = False
        self.setDailyEntryDateCalledWith = None
        self.subjectEntryTitle = None
        self.aAttributes = None
    
    def testIdle2DailyEntry(self):
        self.parsing.h2Begin()
        assert self.parsing.state == HbFileParsing.DailyEntry
        assert self.beginDailyEntryHeaderCalled

    def beginDailyEntryHeader(self):
        self.beginDailyEntryHeaderCalled = True

    def testDailyEntry2SubjectEntry(self):
        self.parsing.state = HbFileParsing.DailyEntry
        self.parsing.h3Begin()
        assert self.parsing.state == HbFileParsing.SubjectEntry
        assert self.beginSubjectEntryHeaderCalled

    def testDailyEntry2DefaultSubjectEntry(self):
        self.parsing.state = HbFileParsing.DailyEntry
        self.parsing.data("2006-03-08")
        self.parsing.h2End()
        self.parsing.tagBegin()
        assert self.parsing.state == HbFileParsing.SubjectEntryContents

    def beginSubjectEntryHeader(self):
        self.beginSubjectEntryHeaderCalled = True

    def testDailyEntryDataEvent(self):
        self.parsing.state = HbFileParsing.DailyEntry
        theDate = "2006-03-05"
        self.parsing.data(theDate)
        assert self.parsing.state == HbFileParsing.DailyEntry
        assert self.setDailyEntryDateCalledWith == theDate

    def setDailyEntryDate(self, data):
        self.setDailyEntryDateCalledWith = data

    def setSubjectEntryTitle(self, data = None):
        if self.subjectEntryTitle != None:
            pass
        elif data == None:
            self.subjectEntryTitle = self.setDailyEntryDateCalledWith
        else:
            self.subjectEntryTitle = data

    def startPos(self):
        self.startPosCalled = True

    def endPos(self):
        self.endPosCalled = True

    def testSubjectEntry2SubjectEntryContents(self):
        self.parsing.state = HbFileParsing.DailyEntry
        self.parsing.h3Begin()
        assert self.parsing.state == HbFileParsing.SubjectEntry
        title = 'title'
        self.parsing.data(title)
        self.parsing.h3End()
        self.parsing.tagBegin()
        assert self.parsing.state == HbFileParsing.SubjectEntryContents

    def testDaily2Subject2Contents2Daily(self):
        self.parsing.state = HbFileParsing.DailyEntry
        self.parsing.h3Begin()
        self.assertEquals(HbFileParsing.SubjectEntry,
                          self.parsing.state)
        self.parsing.h3End()
        self.parsing.tagBegin()
        self.assertEquals(HbFileParsing.SubjectEntryContents,
                          self.parsing.state)
        self.parsing.h2Begin()
        self.assertEquals(HbFileParsing.DailyEntry,
                          self.parsing.state)
        self.assertTrue(self.beginDailyEntryHeaderCalled)

    def testDaily2DefaultSubject2Contents2Daily(self):
        self.parsing.state = HbFileParsing.DailyEntry
        date = "2006-04-02"
        self.parsing.data(date)
        self.parsing.h2End()
        self.parsing.tagBegin()
        self.assertEquals(HbFileParsing.SubjectEntryContents,
                          self.parsing.state)
        self.assertEquals(date, self.subjectEntryTitle)
        self.parsing.h2Begin()
        self.assertEquals(HbFileParsing.DailyEntry, self.parsing.state)

    def test_aBegin_within_h2(self):
        self.parsing.state = HbFileParsing.DailyEntry
        attrs = {'name': '#theName', 'class': 'ancora'}
        self.parsing.aBegin(attrs)
        self.parsing.h2End()
        self.parsing.h3Begin()
        self.assertEquals(HbFileParsing.SubjectEntry, self.parsing.state)
        self.assertEquals(None, self.aAttributes)

    def handleABegin(self, attrs):
        self.aAttributes = attrs

    def test_aBegin_within_h3(self):
        self.parsing.state = HbFileParsing.SubjectEntry
        attrs = {'name': '#theName', 'class': 'ancora'}
        self.parsing.aBegin(attrs)
        self.parsing.h3End()
        self.parsing.tagBegin()
        self.assertEquals(HbFileParsing.SubjectEntryContents, self.parsing.state)
        self.assertEquals(attrs, self.aAttributes)


class HbFileParser(HTMLParser):
    def __init__(self, f):
        HTMLParser.__init__(self)
        self.f = f
        self.dailyEntries = []
        self.parsing = HbFileParsing(self)
        self.feededData = ''

    def parse(self):
        self.feed(self.f.read())
        return self.dailyEntries

    def feed(self, data):
        self.feededData += data
        HTMLParser.feed(self, data)

    def handle_starttag(self, tag, attrs):
        if tag == 'h2':
            self.parsing.h2Begin()
        elif tag == 'h3':
            self.parsing.h3Begin()
        elif tag == 'a':
            self.parsing.aBegin(attrs)
        else:
            self.parsing.tagBegin()

    def beginDailyEntryHeader(self):
        self.curDE = HbDailyEntry(None)
        self.dailyEntries.append(self.curDE)

    def beginSubjectEntryHeader(self):
        self.curSE = HbSubjectEntry(None)
        self.curDE.addSubject(self.curSE)
        self.curSE.startPos = self.charNumFromLineAndOffset(self.getpos())

    def setDailyEntryDate(self, data):
        if self.curDE.date == None:
            self.curDE.date = self.parseIsoDate(data)

    def setSubjectEntryTitle(self, data = None):
        if self.curSE.title != None:
            pass
        elif self.parsing.state == HbFileParsing.DefaultSubjectEntryOfDailyEntry:
            self.curSE.title = self.curDE.date.isoformat()
        else:
            self.curSE.title = self.getTitleOfSubjectEntry()
        # set DefaultSubjectEntries names
        if self.curSE.name == None:
            self.curSE.name = self.curSE.title

    def getTitleOfSubjectEntry(self):
        self.curSE.endPos = self.charNumFromLineAndOffset(self.getpos())
        aStart = self.feededData.find('<a', self.curSE.startPos)
        titleStart = self.feededData.find('>', aStart) + 1
        assert titleStart > self.curSE.startPos
        titleEnd = self.feededData.find('</a>', titleStart)
        if titleEnd >= self.curSE.endPos:
            print 'titleEnd', titleEnd
            print 'self.curSE.endPos', self.curSE.endPos
            print self.feededData[self.curSE.startPos: self.curSE.endPos]
        assert titleEnd < self.curSE.endPos
        del self.curSE.startPos
        del self.curSE.endPos
        return self.stripNewLines(self.feededData[titleStart: titleEnd])

    def handleABegin(self, attrs):
        if self.curSE.name == None:
            for attr in attrs:
                if attr[0] == 'name':
                    self.curSE.name = attr[1]

    def parseIsoDate(self, data):
        return date(int(data[:4]), int(data[5:7]), int(data[8:10]))

    def handle_endtag(self, tag):
        if tag == 'h2':
            self.parsing.h2End()
        elif tag == 'h3':
            self.parsing.h3End()
        elif tag == 'div':
            self.parsing.divEnd()

    def handle_data(self, data):
        self.parsing.data(data)

    def startPos(self):
        self.start = self.charNumFromLineAndOffset(self.getpos())

    def endPos(self):
        self.end = self.charNumFromLineAndOffset(self.getpos())
        self.curSE.contents = self.feededData[self.start: self.end + 1]
        self.curSE.contents = self.stripNewLinesOutsideOfPreElements(self.curSE.contents)
        self.curSE.contents = self.stripTopoFundoNavigation(self.curSE.contents)
        self.curSE.contents = self.curSE.contents.replace('</h3>', '')
        if (self.curSE.contents[-1:] == '<'):
            self.curSE.contents = self.curSE.contents[:-1]

    def charNumFromLineAndOffset(self, pos):
        start = 0
        line = 1
        moreLines = True
        while moreLines:
            if line == pos[0]:
                return start + pos[1]
            start = self.feededData.find('\n', start)
            moreLines = start != -1
            line += 1
            start += 1

    def stripNewLines(self, text):
        lines = re.split('\\n', text)
        for i in range(0, len(lines) - 1):
            if (len(lines[i])) > 0:
                if not re.match('\\s', lines[i][-1:]) and \
                   re.match('^\w', lines[i + 1]):
                    lines[i] = lines[i] + ' '
        def add_strs(s1, s2): return s1 + s2
        from functools import reduce
        return reduce(lambda s1, s2: s1 + s2, lines, '')

    def stripNewLinesOutsideOfPreElements(self, text):
        result = ''
        start = 0
        for match_pre in re.finditer('<pre>.*?</pre>', text[start:],
                                     re.IGNORECASE | re.MULTILINE | re.DOTALL):
            result += self.stripNewLines(text[start:match_pre.start()])
            result += text[match_pre.start():match_pre.end()]
            start = match_pre.end()
        result += self.stripNewLines(text[start:])
        return result

    TopoFundoNavigation = '<p><a href="#topo" class="ligacao">topo</a> | ' + \
                          '<a href="#fundo" class="ligacao">fundo</a></p>'

    def stripTopoFundoNavigation(self, text):
        return self.stripTextOf(text, HbFileParser.TopoFundoNavigation)

    def stripTextOf(self, text, text2Strip):
        if text.find(text2Strip) == -1:
            return text
        start = 0
        found = True
        strippedText = ''
        while found:
            end = text.find(text2Strip, start)
            found = end != -1
            strippedText += text[start: end]
            start = end + len(text2Strip)
        return strippedText


# Unit tests for the HbFileParser class.
class HbFileParserTest(unittest.TestCase):
    def setUp(self):
        self.parser = HbFileParser(None)
        self.p1 = self.makeParagraph(1)
        
    def testCreate(self):
        assert list == type(self.parser.dailyEntries)

    def testParseIsoDate(self):
        assert self.parser.parseIsoDate("2006-03-03") == date(2006, 3, 3)
    
    dailyEntryHeaderDate = "2006-02-11"

    def makeDailyEntryHeader(self, date):
        return '<h2><a name="' + date + '" class="ancora">' + date + '</a></h2>'

    def testParseH2Tag(self):
        date = HbFileParserTest.dailyEntryHeaderDate
        self.parser.feed(self.makeDailyEntryHeader(date))
        assert 1 == len(self.parser.dailyEntries)
        assert self.parser.parseIsoDate(date) == self.parser.dailyEntries[0].date

    def testParseH2TagTwice(self):
        self.testParseH2Tag()
        date = "2006-03-05"
        self.parser.feed(self.makeDailyEntryHeader(date))
        assert 2 == len(self.parser.dailyEntries)
        assert self.parser.parseIsoDate(date) == self.parser.dailyEntries[1].date

    def testParseAnonymousSubjectEntry(self):
        p2 = self.makeParagraph(2)
        self.parser.feed(
            self.makeDailyEntryHeader(HbFileParserTest.dailyEntryHeaderDate) +
            '\n' + self.p1 + '\n' + p2 +
            self.makeDailyEntryHeader('2006-03-20'))
        self.assertEquals(1, len(self.parser.dailyEntries[0].subjects))
        assert HbFileParserTest.dailyEntryHeaderDate == \
            self.parser.dailyEntries[0].subjects[0].title
        self.assertEquals(self.parser.curSE.contents, self.p1 + p2)

    def makeParagraph(self, i):
        return '<p>Paragraph' + str(i) + '.</p>'

    def testParseSubjectEntry(self):
        title = 'subject entry title'
        name = 'subject_entry_name'
        self.parser.feed(self.makeDailyEntryHeader('2006-03-20') + '\n' +
                         self.makeSubjectEntryHeader(name, title) + '\n' +
                         self.p1 + '\n' +
                         HbFileParser.TopoFundoNavigation + '\n'+ 
                         self.makeDailyEntryHeader('2006-03-21'))
        assert self.parser.dailyEntries[0].subjects[0].title == title
        self.assertEquals(self.p1, self.parser.dailyEntries[0].subjects[0].contents)
        self.assertEquals(name, self.parser.dailyEntries[0].subjects[0].name)
                          

    def makeSubjectEntryHeader(self, name, title):
        return '<h3><a name="' + name + '" class="ancora">' + title + '</a></h3>'

    def testParseH2H3H2Tags(self):
        date1 = "2006-03-30"
        date2 = "2006-03-31"
        seName = "se_name"
        seTitle = "SE Title"
        self.parser.feed(self.makeDailyEntryHeader(date1) + '\n' +
                         self.makeSubjectEntryHeader(seName, seTitle) + '\n' +
                         self.p1 + '\n' + 
                         self.makeDailyEntryHeader(date2) + '\n')
        self.assertEquals(2, len(self.parser.dailyEntries))

    def testStripTopoFundoNavigation(self):
        contents = self.p1 + HbFileParser.TopoFundoNavigation
        self.assertEquals(self.p1,
                          self.parser.stripTopoFundoNavigation(contents))

    def testStripTitleOfNewlines(self):
        date1 = "2006-04-10"
        date2 = "2006-04-11"
        seName = "se_name"
        seTitle = "SE \nTitle\n"
        self.parser.feed(self.makeDailyEntryHeader(date1) + '\n' +
                         self.makeSubjectEntryHeader(seName, seTitle) + '\n' +
                         self.p1 + '\n' +
                         self.makeDailyEntryHeader(date2) + '\n')
        self.assertEquals('SE Title',
                          self.parser.dailyEntries[0].subjects[0].title)

    def testStripNewlinesWithoutTrailingWhitespaceDoesntColateWords(self):
        textWithNewlines = "Line1\nLast line \n"
        self.assertEquals('Line1 Last line ',
                          self.parser.stripNewLines(textWithNewlines))

    def testStripNewlinesOutsideOfPreElements(self):
        textWithNewlines = "Line1\n<pre>X\nY</pre>\n\nLast line \n"
        self.assertEquals('Line1<pre>X\nY</pre>Last line ',
                          self.parser.stripNewLinesOutsideOfPreElements(textWithNewlines))

    def testStripTitleOfNewlinesWithoutTrailingWhitespace(self):
        date1 = "2006-04-10"
        seName = "se_name"
        seTitle = "SE\nTitle\n"
        self.parser.feed(self.makeDailyEntryHeader(date1) + '\n' +
                         self.makeSubjectEntryHeader(seName, seTitle) + '\n' +
                         self.p1 + '\n')
        self.assertEquals('SE Title',
                          self.parser.dailyEntries[0].subjects[0].title)

    def test_parse_SubjectEntry_with_code_tag_in_header(self):
        title = '<code>Xpto</code> testing'
        name = 'se_name'
        self.parser.feed(self.makeDailyEntryHeader('2006-05-02') + '\n' +
                         self.makeSubjectEntryHeader(name, title) + '\n' +
                         self.p1 + '\n' +
                         HbFileParser.TopoFundoNavigation + '\n' +
                         self.makeDailyEntryHeader('2006-05-03'))
        self.assertEquals(title, self.parser.dailyEntries[0].subjects[0].title)

    def test_parse_SubjectEntry_with_newline_in_header(self):
        title = 'The title with \n newline'
        name = 'se_name'
        self.parser.feed(self.makeDailyEntryHeader('2006-05-02') + '\n' +
                         self.makeSubjectEntryHeader(name, title) + '\n' +
                         self.p1 + '\n' +
                         HbFileParser.TopoFundoNavigation + '\n' +
                         self.makeDailyEntryHeader('2006-05-03'))
        self.assertEquals('The title with  newline',
                          self.parser.dailyEntries[0].subjects[0].title)

    def test_PRE_element_contents_arent_changed(self):
        pre = "<pre>  line1 of PRE\n  line2 of PRE</pre>"
        self.parser.feed(self.makeDailyEntryHeader('2006-05-02') + '\n' +
                         self.makeSubjectEntryHeader('name', 'The title') + '\n' +
                         self.p1 + '\n' +
                         pre +
                         self.makeDailyEntryHeader('2006-05-03'))
        contents = self.parser.dailyEntries[0].subjects[0].contents
        self.assertTrue(contents.find(pre) != -1,
                        'No match for "' + pre + '" in "' + contents + '".')


if __name__ == "__main__":
    unittest.main()
