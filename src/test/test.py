import unittest
import sys
sys.path.append('../peer')
import document, index


class IndexTest(unittest.TestCase):
    
    def test_fillIndex(self):
	i=index.Index()
	d=document.Document("Hallo ich liebe Katzen")
	i.add(d)
	d2=document.Document("Hallo ich hasse Katzen")
	i.add(d2)
	count = len(i.query("katzen"))
        self.assertEqual(count,2, 'i.query liefert falschen Wert')

    def test_proxy(self):
	self.assert
	
    def test_fail(self):
        self.assertTrue(False, 'failure message goes here')

if __name__ == '__main__':
    unittest.main()

