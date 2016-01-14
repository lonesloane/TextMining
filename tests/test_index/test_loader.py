import unittest
import datetime

import index.loader as loader


class IndexTestCase(unittest.TestCase):
    index_filename = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Index"

    def test_create(self):
        self.assertRaises(Exception, loader.Index, "")
        values = loader.Index(IndexTestCase.index_filename).index
        self.assertEquals(values['30'], ('lbl_en_30', 'lbl_fr_30'))


class FilesIndexTestCase(unittest.TestCase):
    index_filename = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Files_Index"

    def test_create(self):
        values = loader.FilesIndex(FilesIndexTestCase.index_filename).index
        print values['JT01.xml']
        expected = [('18', 'N'), ('36', 'N'), ('30', 'N'), ('26', 'N'), ('15', 'N'), ('46', 'N'), ('38', 'N'),
                    ('27', 'N'), ('43', 'N'), ('37', 'N'), ('1', 'N'), ('47', 'N'), ('48', 'H'), ('8', 'N'),
                    ('22', 'H')]
        self.assertEquals(expected, values['JT01.xml'])

    def test_get_topics_for_files(self):
        target_file = 'JT03.xml'
        expected = ['14', '18', '24', '3', '30', '30', '35', '38', '42', '45', '46', '5', '6', '7', '9']
        actual = loader.FilesIndex(FilesIndexTestCase.index_filename).get_topics_for_files(target_file)
        self.assertEqual(expected, actual)

    def test_get_enrichment_for_files(self):
        target_file = 'JT03.xml'
        expected = [('30', 'N'), ('24', 'N'), ('42', 'N'), ('3', 'N'), ('35', 'N'), ('5', 'H'), ('18', 'N'),
                    ('30', 'N'), ('14', 'N'), ('45', 'N'), ('9', 'H'), ('46', 'N'), ('38', 'N'), ('6', 'N'), ('7', 'N')]
        actual = loader.FilesIndex(FilesIndexTestCase.index_filename).get_enrichment_for_files(target_file)
        print actual
        self.assertEqual(expected, actual)


class FilesDatesIndexTestCase(unittest.TestCase):
    index_filename = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Files_Dates_Index"

    def test_create(self):
        values = loader.FilesDatesIndex(FilesDatesIndexTestCase.index_filename).index
        expected = datetime.date(2015, 2, 5)
        self.assertEquals(expected, values['JT01.xml'])

    def test_get_date_for_file(self):
        target_file = 'JT03.xml'
        actual = loader.FilesDatesIndex(FilesDatesIndexTestCase.index_filename).get_date_for_file(target_file)
        expected = datetime.date(2014, 6, 15)
        self.assertEquals(expected, actual)


class TopicsIndexTestCase(unittest.TestCase):
    index_filename = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Index"

    def test_create(self):
        values = loader.TopicsIndex(TopicsIndexTestCase.index_filename).index
        expected = ('lbl_en_30', 'lbl_fr_30')
        self.assertEquals(expected, values['30'])

    def test_get_labels_for_topic_id(self):
        topic_id = '1'
        expected = ('lbl_en_1', 'lbl_fr_1')
        actual = loader.TopicsIndex(TopicsIndexTestCase.index_filename).get_labels_for_topic_id(topic_id)
        self.assertEqual(expected, actual)


class TopicsOccurrencesTestCase(unittest.TestCase):
    index_filename = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Occurrences_Index"

    def test_create(self):
        values = loader.TopicsOccurrencesIndex(TopicsOccurrencesTestCase.index_filename).index
        expected = [('JT02.xml', 'N'), ('JT03.xml', 'N'), ('JT09.xml', 'N')]
        self.assertEquals(expected, values['30'])

    def test_get_files_for_topic(self):
        expected = [('JT02.xml', 'N'), ('JT03.xml', 'N'), ('JT09.xml', 'N')]
        target_topic = '30'
        actual = loader.TopicsOccurrencesIndex(TopicsOccurrencesTestCase.index_filename).get_files_for_topic(target_topic)
        self.assertEqual(expected, actual)


class TopicsLabelsIndexTestCase(unittest.TestCase):
    index_filename = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Labels_Index"

    def test_create(self):
        values = loader.TopicsLabelsIndex(TopicsLabelsIndexTestCase.index_filename).index
        self.assertEquals('30', values['lbl_fr_31'])

    def test_get_topic_id_for_labels(self):
        target_topic = 'lbl_en_1'
        expected = '1'
        actual = loader.TopicsLabelsIndex(TopicsLabelsIndexTestCase.index_filename).get_topic_id_for_label(target_topic)
        self.assertEqual(expected, actual)


class TopicsTypeAheadIndexTestCase(unittest.TestCase):
    index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Topics_Typeahead_Index'

    def test_create(self):
        self.assertIsNotNone(loader.TopicsTypeAheadIndex(TopicsTypeAheadIndexTestCase.index_filename).index)

    def test_auto_complete(self):
        type_ahead_index = loader.TopicsTypeAheadIndex(TopicsTypeAheadIndexTestCase.index_filename)
        expected = ['genetic resources', 'genetic improvement', 'plant genetics', 'human genetics', 'animal genetics',
                    'genetic engineering', 'genetics', 'genetically modified organisms']
        actual = type_ahead_index.auto_complete('genet')
        print actual
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    unittest.main()
