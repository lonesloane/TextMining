import unittest

import index.loader as loader


class IndexTestCase(unittest.TestCase):
    index_filename = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Index"

    def test_create(self):
        self.assertRaises(Exception, loader.Index, "")
        values = loader.Index(index_filename=IndexTestCase.index_filename)._index
        self.assertEquals(values['30'], ('lbl_en_30', 'lbl_fr_30'))


class FilesIndexTestCase(unittest.TestCase):
    index_filename = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Files_Index"

    def test_create(self):
        values = loader.FilesIndex(index_filename=FilesIndexTestCase.index_filename)._index
        expected = [('26', 'N'), ('27', 'N'), ('22', 'H'), ('46', 'N'), ('43', 'N'), ('1', 'N'), ('8', 'N'),
                    ('47', 'N'), ('38', 'N'), ('15', 'N'), ('18', 'N'), ('31', 'N'), ('37', 'N'), ('36', 'N'),
                    ('48', 'H')]
        self.assertEquals(expected, values['JT01.xml'])

    def test_get_topics_for_files(self):
        target_file = 'JT03.xml'
        expected = ['14', '18', '24', '3', '30', '31', '35', '38', '42', '45', '46', '5', '6', '7', '9']
        actual = loader.FilesIndex(index_filename=FilesIndexTestCase.index_filename).get_topics_for_files(target_file)
        self.assertEqual(expected, actual)

    def test_get_enrichment_for_files(self):
        target_file = 'JT03.xml'
        expected = [('24', 'N'), ('46', 'N'), ('45', 'N'), ('42', 'N'), ('3', 'N'), ('5', 'H'), ('7', 'N'), ('6', 'N'),
                    ('9', 'H'), ('38', 'N'), ('14', 'N'), ('18', 'N'), ('31', 'N'), ('30', 'N'), ('35', 'N')]
        actual = loader.FilesIndex(index_filename=FilesIndexTestCase.index_filename).get_enrichment_for_files(target_file)
        self.assertEqual(expected, actual)


class TopicsIndexTestCase(unittest.TestCase):
    index_filename = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Index"

    def test_create(self):
        values = loader.TopicsIndex(index_filename=TopicsIndexTestCase.index_filename)._index
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
        values = loader.TopicsOccurrencesIndex(index_filename=TopicsOccurrencesTestCase.index_filename)._index
        expected = [('JT02.xml', 'N'), ('JT03.xml', 'N'), ('JT09.xml', 'N')]
        self.assertEquals(expected, values['30'])

    def test_get_files_for_topic(self):
        expected = [('JT02.xml', 'N'), ('JT03.xml', 'N'), ('JT09.xml', 'N')]
        target_topic = '30'
        actual = loader.TopicsOccurrencesIndex(index_filename=TopicsOccurrencesTestCase.index_filename).get_files_for_topic(target_topic)
        self.assertEqual(expected, actual)


class TopicsLabelsIndexTestCase(unittest.TestCase):
    index_filename = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Labels_Index"

    def test_create(self):
        values = loader.TopicsLabelsIndex(index_filename=TopicsLabelsIndexTestCase.index_filename)._index
        self.assertEquals('31', values['lbl_fr_31'])

    def test_get_topic_id_for_labels(self):
        target_topic = 'lbl_en_1'
        expected = '1'
        actual = loader.TopicsLabelsIndex(TopicsLabelsIndexTestCase.index_filename).get_topic_id_for_label(target_topic)
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()