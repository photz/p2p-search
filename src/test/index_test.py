import unittest
import sys
sys.path.append('../peer')
import document, index


class IndexTest(unittest.TestCase):
    
    def NOT_test_html_tags_are_stripped(self):

        html = '''
        <html>
        <head>
        <title>Test</title>
        </head>
        <body>
        <h1>Hello world</h1>
        <p>test</p>
        </body>
        </html>
        '''

        doc = document.Document.from_html(html, 'http://example.com')

        self.assertEqual(doc.contents, 'Test Hello world test')


    def test_fillIndex(self):
        i=index.Index()
        d=document.Document.from_html("<html>Hallo ich liebe Katzen</html>",
                                      'http://cats.com')
        i.add(d)
        d2=document.Document.from_html("<html>Hallo ich hasse Katzen</html>",
                                       'http://dogs.com')
        i.add(d2)
        print(d2.contents)

        count = len(i.query("katzen"))
        self.assertEqual(count,2, 'i.query liefert falschen Wert')

if __name__ == '__main__':
    unittest.main()

