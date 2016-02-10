from bs4 import BeautifulSoup
from html.parser import HTMLParser

# see: http://stackoverflow.com/questions/753052/strip-html-from-strings-in-python
class MLStripper(HTMLParser):
    def __init__(self):
        super(HTMLParser, self).__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.fed = []

    def handle_data(self, d):
        self.fed.append(d)

    def get_data(self):
        return ''.join(self.fed)
            
    def strip_tags(html):
        s = MLStripper()
        s.feed(html)
        return s.get_data()

class Document(object):


    @staticmethod
    def from_html(html_anything, url):

        bs = BeautifulSoup(html_anything)

        doc = Document()

        doc.contents = MLStripper.strip_tags(str(bs))

        doc._extract_metadata(bs)

        doc.url = url

        return doc
        

    def _extract_metadata(self, bs):
        if bs.title:
            self.title = bs.title.text
        elif bs.h1:
            self.title = bs.h1.text
        elif bs.h2:
            self.title = bs.h2.text
        else:
            self.title = 'Unknown Document'

