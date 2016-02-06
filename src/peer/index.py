

class Index(object):

    def __init__(self):

        self._terms = dict()

    def add(self, doc):
        tokens = self._tokenize(doc.contents)

        for token in tokens:
            self._terms.setdefault(token, set()).add(doc)

    def query(self, s):

        tokens = self._tokenize(s)

        if len(tokens) == 0:
            return list()

        first_token = tokens.pop()

        if first_token not in self._terms:
            return list()

        matches = set(self._terms[first_token])

        for token in tokens:
            if token not in self._terms:
                return list()

            matches.intersection_update(self._terms[token])
                
        return matches
        

    def _tokenize(self, s):
        return s.lower().split()

    
