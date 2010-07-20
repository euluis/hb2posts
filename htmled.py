# Python file - http://www.python.org/

# Automation for my HTML and Handbook to blog author's tasks.

from datetime import date
import re

def getHbFileName(filename):
    import os.path
    """getHbFileName(filenameAsString) -> str
    
    Given a HbFile filename as a string, determine its filename as a string
    without any path part, i.e., getHbFileName('path/to/filename.html') -> 'filename.html'
    """
    return os.path.basename(filename)


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

    def getFileName(self):
        assert self.f.name != None
        return getHbFileName(self.f.name)


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


class Post:
    """A weblog post."""
    def __init__(self, date, title, contents, subjname, hbfname):
        self.date = date
        self.title = title
        self.contents = contents
        self.subjname = subjname
        self.hbfname = hbfname
        self.setPostNames()

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

    def setPostNames(self):
        """setPostNames()
        
        Add attribute names, containing the HTML referenceable
        names contained in the post.
        """
        assert(dir(self).count('names') == 0)
        self.names = []
        start = 0
        namePos = -1
        if self.contents:
            namePos = self.contents.find('<a name="', start)
        while namePos != -1:
            nameStart = self.contents.find('"', namePos) + 1
            name = self.contents[nameStart: self.contents.find('"', nameStart)]
            self.names.append(name)
            namePos = self.contents.find('<a name="', nameStart)


class PostExtractor:
    """The PostExtractor class extracts Posts from HbFile instances."""
    def __init__(self, *hbfs):
        """PostExtractor([hbf1[,hbf2[,hbf3[...]]]]) -> postExtractor

        Create a PostExtractor class to extract posts from the HbFile instances
        it was given.
        """
        self.hbfs = hbfs

    def getPosts(self, d1 = None, d2 = None):
        posts = []
        for hbf in self.hbfs:
            for de in hbf.dailyEntries:
                for subj in de.subjects:
                    postTitle = self.stripTags(subj.title)
                    post = Post(de.date, postTitle, subj.contents, subj.name,
                                hbf.getFileName())
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
    
    HbfIntraLinkPattern = r'<a\s+href="(?P<filename>[^:]*?)#(?P<anchor>.+?)".*?>'

    def searchHbfIntraLink(self, text):
        return re.search(PostExtractor.HbfIntraLinkPattern, text, re.IGNORECASE)

    def blogLinkFromHbfLink(self, posts, post, match):
        """blogLinkFromHbfLink(posts, post.hbfname, match) -> blogLink
        
        Get a blog link corresponding to the handbook file link in match that
        belongs to a post which file in named post.hbfname, by looking in all
        posts for the name. In principle posts should contain a reference to
        the post from where match comes from, to resolve intra-post links.
        If it isn't successful in finding something, it returns match.group()
        (i.e., the original link). Oh(!), match is a re.MatchObject instance
        resulting from a search with PostExtractor.HbfIntraLinkPattern.
        """
        filePath = post.hbfname
        if len(match.group('filename')) > 0:
            filePath = match.group('filename')
        relevantPosts = [p for p in posts if p.hbfname == filePath]
        link = match.group()
        if match.group('anchor') in post.names and len(match.group('filename')) == 0:
            return link
        for post in relevantPosts:
            if post.subjname == match.group('anchor'):
                return link[:match.start('filename') - match.start()] + \
                    post.getPermaLink() + link[match.end('anchor') - match.start():]
            elif match.group('anchor') in post.names:
                return link[:match.start('filename') - match.start()] + \
                    post.getPermaLink() + link[match.end('filename') - match.start():]
        return link

    def adaptPostsLinks(self, posts):
        """adaptPostsLinks(self, posts)

        Adapt the links contained in the posts so that they work in the blog.
        """
        for post in posts:
            post.contents = re.sub(PostExtractor.HbfIntraLinkPattern,
                                   lambda match: self.blogLinkFromHbfLink(posts,
                                                                          post, match),
                                   post.contents)

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


from HTMLParser import HTMLParser

class HbFileParsingState:
    """Base state for the implementation of the Hand-book file parsing finite
    state machine."""
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
    """Implements a Finite State Machine for the Handbook File Parser."""
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
            print '\n' + self.feededData[self.curSE.startPos: self.curSE.endPos]
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
            if len(lines[i]) > 0 and len(lines[i + 1]) > 0:
                if not re.match('\\s', lines[i][-1:]) and \
                        not re.match('^<[phuo]', lines[i + 1], re.IGNORECASE):
                    lines[i] = lines[i] + ' '
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
