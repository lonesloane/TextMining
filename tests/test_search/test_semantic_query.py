import logging
import unittest

import search.semantic_query as search
from index.loader import FilesIndex, TopicsOccurrencesIndex, TopicsLabelsIndex


class QueryProcessorTestCase(unittest.TestCase):

    _files_index_filename = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Files_Index"
    _topics_occurrences_index_filename = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Occurrences_Index"
    _topics_labels_index_filename = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Labels_Index"

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
        self._files_index = FilesIndex(self._files_index_filename)
        self._topics_occurrences_index = TopicsOccurrencesIndex(self._topics_occurrences_index_filename)
        self._topics_labels_index = TopicsLabelsIndex(self._topics_labels_index_filename)

        self.processor = search.QueryProcessor(files_index=self._files_index,
                                               topics_occurrences_index=self._topics_occurrences_index,
                                               topics_labels_index=self._topics_labels_index)

    def test_init(self):
        self.assertIsNotNone(self.processor._files_index)
        self.assertIsNotNone(self.processor._topics_occurrences_index)
        self.assertIsNotNone(self.processor._topics_labels_index)

    def test_load_files_index(self):
        self.assertTrue('JT01.xml'in self.processor._files_index._index)
        expected = [('18', 'N'), ('36', 'N'), ('31', 'N'), ('26', 'N'), ('15', 'N'), ('46', 'N'), ('38', 'N'),
                    ('27', 'N'), ('43', 'N'), ('37', 'N'), ('1', 'N'), ('47', 'N'), ('48', 'H'), ('8', 'N'),
                    ('22', 'H')]
        actual = self.processor._files_index._index['JT01.xml']
        print actual

        self.assertEqual(expected, actual)

    def test_load_topics_occurrences_index(self):
        self.assertTrue('1' in self.processor._topics_occurrences_index._index)
        expected = [('JT02.xml', 'N'), ('JT08.xml', 'N'), ('JT01.xml', 'N'), ('JT07.xml', 'N')]
        actual = self.processor._topics_occurrences_index._index['1']

        self.assertEqual(expected, actual)

    def test_load_topics_labels_index(self):
        self.assertTrue('lbl_en_1' in self.processor._topics_labels_index._index)
        expected = '1'
        actual = self.processor._topics_labels_index._index['lbl_en_1']
        print actual

        self.assertEqual(expected, actual)

    def test_get_files_for_single_topic(self):
        topic = "1"
        expected_len = 4
        expected_files = ['JT02.xml', 'JT08.xml', 'JT01.xml', 'JT07.xml']

        actual = self.processor._get_files_for_topic(topic)

        self.assertEqual(expected_len, len(actual))
        self.assertEqual(expected_files, actual)

    def test_get_topics_for_files(self):
        topic = ['1']
        files = ['JT02.xml', 'JT08.xml', 'JT01.xml', 'JT07.xml']
        expected_len = 35
        expected_topics = [2, 3, 5, 6, 8, 9, 10, 11, 14, 15, 16, 18, 20, 22, 24, 25, 26, 27, 28, 30, 31, 33, 35,
                           36, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48]

        actual = self.processor._get_topics_for_files(files, ignored_topic=topic)

        self.assertEqual(expected_len, len(actual))
        self.assertEqual(expected_topics, actual)

        topic = ['1', '2']
        files = ['JT02.xml', 'JT08.xml', 'JT01.xml', 'JT07.xml']
        expected_len = 34
        expected_topics = [3, 5, 6, 8, 9, 10, 11, 14, 15, 16, 18, 20, 22, 24, 25, 26, 27, 28, 30, 31, 33, 35,
                           36, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48]

        actual = self.processor._get_topics_for_files(files, ignored_topic=topic)

        self.assertEqual(expected_len, len(actual))
        self.assertEqual(expected_topics, actual)

    def test_get_topic_id_from_label(self):
        logging.getLogger(__name__).info('begin test: test_get_topic_id_from_label')

        topic_label = "lbl_en_1"
        expected = '1'
        actual = self.processor.get_topic_id_from_label(topic_label)
        self.assertEqual(expected, actual)

        topic_label = "lbl_fr_1"
        expected = '1'
        actual = self.processor.get_topic_id_from_label(topic_label)
        self.assertEqual(expected, actual)

        topic_label = "lbl_en_2"
        expected = '2'
        actual = self.processor.get_topic_id_from_label(topic_label)
        self.assertEqual(expected, actual)

        topic_label = "lbl_en_xxx"
        expected = None
        actual = self.processor.get_topic_id_from_label(topic_label)
        self.assertEqual(expected, actual)

    def test_execute_by_topic_id(self):
        topic = ["1"]
        expected_files = ['JT02.xml', 'JT08.xml', 'JT01.xml', 'JT07.xml']
        expected_topics = [2, 3, 5, 6, 8, 9, 10, 11, 14, 15, 16, 18, 20, 22, 24, 25, 26, 27, 28, 30, 31, 33, 35,
                           36, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48]
        actual_files, actual_topics = self.processor.execute(topic)

        self.assertListEqual(sorted(expected_files), sorted(actual_files))
        self.assertListEqual(expected_topics, actual_topics)

        topic = ["1", "31"]
        expected_files = ['JT01.xml', 'JT02.xml', 'JT08.xml']
        expected_topics = [2, 3, 6, 8, 9, 10, 14, 15, 18, 20, 22, 24, 25, 26, 27, 28, 30, 33, 35, 36, 37, 38, 40,
                           42, 43, 44, 46, 47, 48]
        actual_files, actual_topics = self.processor.execute(topic)

        self.assertListEqual(sorted(expected_files), sorted(actual_files))
        self.assertListEqual(expected_topics, actual_topics)

        topic = ["31", "1"]
        expected_files = ['JT01.xml', 'JT02.xml', 'JT08.xml']
        expected_topics = [2, 3, 6, 8, 9, 10, 14, 15, 18, 20, 22, 24, 25, 26, 27, 28, 30, 33, 35, 36, 37, 38, 40,
                           42, 43, 44, 46, 47, 48]
        actual_files, actual_topics = self.processor.execute(topic)

        self.assertListEqual(sorted(expected_files), sorted(actual_files))
        self.assertListEqual(expected_topics, actual_topics)

        topic = ["1", "31", "42"]
        expected_files = ['JT02.xml']
        expected_topics = [2, 3, 6, 9, 20, 22, 24, 25, 27, 30, 35, 37]
        actual_files, actual_topics = self.processor.execute(topic)

        self.assertListEqual(sorted(expected_files), sorted(actual_files))
        self.assertListEqual(expected_topics, actual_topics)

        topic = ["31", "42", "1"]
        expected_files = ['JT02.xml']
        expected_topics = [2, 3, 6, 9, 20, 22, 24, 25, 27, 30, 35, 37]
        actual_files, actual_topics = self.processor.execute(topic)

        self.assertListEqual(sorted(expected_files), sorted(actual_files))
        self.assertListEqual(expected_topics, actual_topics)

    def test_execute_ordered(self):
        # Validates results are ordered according to topics relevance
        topic = ['22', '31']
        expected_files = ['JT04.xml', 'JT01.xml', 'JT02.xml']
        actual_files, actual_topics = self.processor.execute(topic, order_by_relevance=True)
        print actual_files
        self.assertListEqual(sorted(expected_files), sorted(actual_files))  # check same elements
        self.assertEqual('JT04.xml', actual_files[0])  # check actual order
        self.assertEqual('JT01.xml', actual_files[1])  # check actual order

if __name__ == '__main__':
    unittest.main()
