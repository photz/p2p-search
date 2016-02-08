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
    def from_html(html, url):
        if type(html) is not str:
            raise TypeError('expected a string')

        doc = Document()

        doc.contents = MLStripper.strip_tags(html)

        doc.extract_metadata(html)

        doc.url = url

        return doc
        

    def extract_metadata(self, html):
        bs = BeautifulSoup(html)
        if bs.title:
            self.title = bs.title.text
        else:
            self.title = 'Unknown Document'
