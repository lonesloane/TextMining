import unittest

import index.loader as loader


class IndexTestCase(unittest.TestCase):

    def test_create(self):
        self.assertRaises(Exception, loader.Index, "")
        values = loader.Index(index_filename="../testOutput/Test_Topics_Index")._index
        self.assertEquals(values['30'], ('lbl_en_30', 'lbl_fr_30'))


class FilesIndexTestCase(unittest.TestCase):
    def test_create(self):
        values = loader.FilesIndex(index_filename="../testOutput/Test_Files_Index")._index
        expected = [('26', 'N'), ('27', 'N'), ('22', 'H'), ('46', 'N'), ('43', 'N'), ('1', 'N'), ('8', 'N'),
                    ('47', 'N'), ('38', 'N'), ('15', 'N'), ('18', 'N'), ('31', 'N'), ('37', 'N'), ('36', 'N'),
                    ('48', 'H')]
        self.assertEquals(expected, values['JT01.xml'])

    def test_get_topics_for_files(self):
        target_file = 'JT03.xml'
        expected = ['14', '18', '24', '3', '30', '31', '35', '38', '42', '45', '46', '5', '6', '7', '9']
        actual = loader.FilesIndex(index_filename="../testOutput/Test_Files_Index").get_topics_for_files(target_file)
        self.assertEqual(expected, actual)

    def test_get_enrichment_for_files(self):
        target_file = 'JT03.xml'
        expected = [('24', 'N'), ('46', 'N'), ('45', 'N'), ('42', 'N'), ('3', 'N'), ('5', 'H'), ('7', 'N'), ('6', 'N'),
                    ('9', 'H'), ('38', 'N'), ('14', 'N'), ('18', 'N'), ('31', 'N'), ('30', 'N'), ('35', 'N')]
        actual = loader.FilesIndex(index_filename="../testOutput/Test_Files_Index").get_enrichment_for_files(target_file)
        self.assertEqual(expected, actual)


class TopicsIndexTestCase(unittest.TestCase):
    def test_create(self):
        values = loader.TopicsIndex(index_filename="../testOutput/Test_Topics_Index")._index
        expected = ('lbl_en_30', 'lbl_fr_30')
        self.assertEquals(expected, values['30'])


class TopicsOccurrencesTestCase(unittest.TestCase):
    def test_create(self):
        values = loader.TopicsOccurrencesIndex(index_filename="../testOutput/Test_Topics_Occurrences_Index")._index
        expected = [('JT02.xml', 'N'), ('JT03.xml', 'N'), ('JT09.xml', 'N')]
        self.assertEquals(expected, values['30'])

    def test_get_files_for_topic(self):
        expected = [('JT02.xml', 'N'), ('JT03.xml', 'N'), ('JT09.xml', 'N')]
        target_topic = '30'
        actual = loader.TopicsOccurrencesIndex(index_filename="../testOutput/Test_Topics_Occurrences_Index").get_files_for_topic(target_topic)
        self.assertEqual(expected, actual)

class TopicsLabelsIndexTestCase(unittest.TestCase):
    def test_create(self):
        values = loader.TopicsLabelsIndex(index_filename="../testOutput/Test_Topics_Labels_Index")._index
        self.assertEquals('31', values['lbl_fr_31'])


if __name__ == '__main__':
    unittest.main()
