import unittest

import search.semantic_search as search


class QueryProcessorTestCase(unittest.TestCase):
    def setUp(self):
        files_index = "../testOutput/Test_Files_Index"
        topics_index = "../testOutput/Test_Topics_Occurrences_Index"
        self.processor = search.QueryProcessor(files_index_filename=files_index,
                                               topics_occurrences_index_filename=topics_index)

    def test_init(self):
        self.assertRaises(Exception, search.QueryProcessor)

        files_index = "../testOutput/Test_Files_Index"
        topics_index = "../testOutput/Test_Topics_Occurrences_Index"
        processor = search.QueryProcessor(files_index_filename=files_index,
                                          topics_occurrences_index_filename=topics_index)
        self.assertIsNotNone(processor._files_index_filename, "Files index should not be None")
        self.assertIsNotNone(processor._topics_occurrences_index_filename, "Topics index should not be None")
        self.assertEqual("../testOutput/Test_Files_Index", processor._files_index_filename)
        self.assertEqual("../testOutput/Test_Topics_Occurrences_Index", processor._topics_occurrences_index_filename)

        self.assertIsNotNone(processor._files_index)
        self.assertIsNotNone(processor._topics_occurrences_index)

    def test_load_files_index(self):
        self.processor.load_files_index()
        self.assertTrue(self.processor._files_index.has_key('JT01.xml'))
        expected = [('26', 'N'), ('27', 'N'), ('22', 'H'), ('46', 'N'), ('43', 'N'), ('1', 'N'), ('8', 'N'),
                    ('47', 'N'), ('38', 'N'), ('15', 'N'), ('18', 'N'), ('31', 'N'),
                    ('37', 'N'), ('36', 'N'), ('48', 'H')]
        actual = self.processor._files_index['JT01.xml']

        self.assertEqual(expected, actual)

    def test_load_topics_occurrences_index(self):
        self.processor.load_topics_occurrences_index()
        self.assertTrue(self.processor._topics_occurrences_index.has_key('1'))
        expected = [('JT02.xml', 'N'), ('JT08.xml', 'N'), ('JT01.xml', 'N'), ('JT07.xml', 'N')]
        actual = self.processor._topics_occurrences_index['1']

        self.assertEqual(expected, actual)

    def test_get_files_for_single_topic(self):
        topic = "1"
        expected_len = 4
        expected_files = ['JT02.xml', 'JT08.xml', 'JT01.xml', 'JT07.xml']

        actual = self.processor._get_files(topic)

        self.assertEqual(expected_len, len(actual))
        self.assertEqual(expected_files, actual)

    def test_get_topics_for_files(self):
        topic = ['1']
        files = ['JT02.xml', 'JT08.xml', 'JT01.xml', 'JT07.xml']
        expected_len = 35
        expected_topics = [2, 3, 5, 6, 8, 9, 10, 11, 14, 15, 16, 18, 20, 22, 24, 25, 26, 27, 28, 30, 31, 33, 35,
                           36, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48]

        actual = self.processor._get_topics(files, ignored_topic=topic)

        self.assertEqual(expected_len, len(actual))
        self.assertEqual(expected_topics, actual)

        topic = ['1', '2']
        files = ['JT02.xml', 'JT08.xml', 'JT01.xml', 'JT07.xml']
        expected_len = 34
        expected_topics = [3, 5, 6, 8, 9, 10, 11, 14, 15, 16, 18, 20, 22, 24, 25, 26, 27, 28, 30, 31, 33, 35,
                           36, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48]

        actual = self.processor._get_topics(files, ignored_topic=topic)

        self.assertEqual(expected_len, len(actual))
        self.assertEqual(expected_topics, actual)

    def test_execute(self):
        topic = "1"
        expected_files = ['JT02.xml', 'JT08.xml', 'JT01.xml', 'JT07.xml']
        expected_topics = [2, 3, 5, 6, 8, 9, 10, 11, 14, 15, 16, 18, 20, 22, 24, 25, 26, 27, 28, 30, 31, 33, 35,
                           36, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48]
        actual_files, actual_topics = self.processor.execute(topic)

        self.assertListEqual(sorted(expected_files), sorted(actual_files))
        self.assertListEqual(expected_topics, actual_topics)

        topic = "1-31"
        expected_files = ['JT01.xml', 'JT02.xml', 'JT08.xml']
        expected_topics = [2, 3, 6, 8, 9, 10, 14, 15, 18, 20, 22, 24, 25, 26, 27, 28, 30, 33, 35, 36, 37, 38, 40,
                           42, 43, 44, 46, 47, 48]
        actual_files, actual_topics = self.processor.execute(topic)

        self.assertListEqual(sorted(expected_files), sorted(actual_files))
        self.assertListEqual(expected_topics, actual_topics)

        topic = "31-1"
        expected_files = ['JT01.xml', 'JT02.xml', 'JT08.xml']
        expected_topics = [2, 3, 6, 8, 9, 10, 14, 15, 18, 20, 22, 24, 25, 26, 27, 28, 30, 33, 35, 36, 37, 38, 40,
                           42, 43, 44, 46, 47, 48]
        actual_files, actual_topics = self.processor.execute(topic)

        self.assertListEqual(sorted(expected_files), sorted(actual_files))
        self.assertListEqual(expected_topics, actual_topics)

        topic = "1-31-42"
        expected_files = ['JT02.xml']
        expected_topics = [2, 3, 6, 9, 20, 22, 24, 25, 27, 30, 35, 37]
        actual_files, actual_topics = self.processor.execute(topic)

        self.assertListEqual(sorted(expected_files), sorted(actual_files))
        self.assertListEqual(expected_topics, actual_topics)

        topic = "31-42-1"
        expected_files = ['JT02.xml']
        expected_topics = [2, 3, 6, 9, 20, 22, 24, 25, 27, 30, 35, 37]
        actual_files, actual_topics = self.processor.execute(topic)

        self.assertListEqual(sorted(expected_files), sorted(actual_files))
        self.assertListEqual(expected_topics, actual_topics)


if __name__ == '__main__':
    unittest.main()
