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


if __name__ == '__main__':
    unittest.main()
