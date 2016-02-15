import unittest

from analysis.topics_typeahead import tokenize


class TopicsTypeaheadBuilderTestCase(unittest.TestCase):

    def test_tokenize(self):
        sentence = 'La nature est un temple'
        expected = ['La', 'nature', 'est', 'un', 'temple']
        actual = tokenize(sentence)
        self.assertEqual(expected, actual)