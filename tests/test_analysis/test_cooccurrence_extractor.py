import logging
import os
import unittest
import analysis.cooccurrence_extractor as extractor


class CoOccurrenceExtractorTestCase(unittest.TestCase):

    def setUp(self):
        topics_occurrences_index_filename = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Cooccurrence_Topics_Occurrences_Index"
        files_index_filename = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Cooccurrence_Files_Index"
        self.extractor = extractor.CoOccurrenceExtractor(topics_occurrences_index_filename=topics_occurrences_index_filename,
                                                         files_index_filename=files_index_filename,
                                                         depth=5)
        # self.extractor = extractor.CoOccurrenceExtractor(topics_occurrences_index_filename="../testOutput/Test_Topics_Occurrences_Index",
        #                                            files_index_filename="../testOutput/Test_Files_Index")
        # self.extractor = extractor.CoOccurrenceExtractor(topics_occurrences_index_filename="../../output/2015_Topics_Occurrences_Index",
        #                                                  files_index_filename="../../output/2015_Files_Index", depth=5)
        # self.extractor = extractor.CoOccurrenceExtractor(topics_occurrences_index_filename="../../output/Topics_Occurrences_Index",
        #                                            files_index_filename="../../output/Files_Index")

    def tearDown(self):
        if os.path.isfile("Full_Cooccurrences_Index"):
            os.remove("Full_Cooccurrences_Index")

    def test_create(self):
        expected = 10
        actual = len(self.extractor.topics_occurrences_table)

        self.assertEqual(expected, actual)

    def test_extract_topics_for_file(self):
        target_file = "JT03.xml"
        target_topic = "3"
        expected = sorted(['11', '10', '6', '9'])
        actual = self.extractor._extract_topics_for_file(target_file, target_topic)
        self.assertEqual(expected, sorted(actual))

        target_topic = "3-9"
        expected = sorted(['11', '10', '6'])
        actual = self.extractor._extract_topics_for_file(target_file, target_topic)
        self.assertEqual(expected, sorted(actual))

        target_topic = "3-6-9"
        expected = sorted(['11', '10'])
        actual = self.extractor._extract_topics_for_file(target_file, target_topic)
        self.assertEqual(expected, sorted(actual))

        target_topic = "3-6-9-11"
        expected = ['10']
        actual = self.extractor._extract_topics_for_file(target_file, target_topic)
        self.assertEqual(expected, actual)

        target_topic = "3-6-9-10-11"
        expected = []
        actual = self.extractor._extract_topics_for_file(target_file, target_topic)
        self.assertEqual(expected, actual)

        target_topic = "3-6-9-10-33"
        self.assertRaises(AssertionError, self.extractor._extract_topics_for_file, target_file, target_topic)

    def test_find_unary_cooccurrences(self):
        target = "3"
        co_occurrences = self.extractor.find_cooccurrences(target)

        expected = 2
        self.assertEqual(expected, co_occurrences['6'])
        expected = 1
        self.assertEqual(expected, co_occurrences['7'])
        expected = 9
        self.assertEqual(expected, len(co_occurrences))

    def test_extract_topic_cooccurrences(self):
        target_topic = "3"
        target_file = self.extractor._topics_occurrences_table[target_topic][0][0]
        actual_co_occurrences = self.extractor._extract_topic_cooccurrences(target_topic=target_topic,
                                                                            target_file=target_file)

        expected_co_occurrences = ['1', '5', '6', '7']
        self.assertEqual(sorted(expected_co_occurrences), sorted(actual_co_occurrences))

    def test_build_index_key(self):
        root_topic = "1-3"
        cooccurrence_topic = "2"
        expected = "1-2-3"
        actual = extractor.CoOccurrenceExtractor.build_composite_key(root_topic, cooccurrence_topic)
        self.assertEqual(expected, actual)

        root_topic = "2047"
        cooccurrence_topic = "999"
        expected = "999-2047"
        actual = extractor.CoOccurrenceExtractor.build_composite_key(root_topic, cooccurrence_topic)
        self.assertEqual(expected, actual)

        root_topic = "999-2047"
        cooccurrence_topic = "333"
        expected = "333-999-2047"
        actual = extractor.CoOccurrenceExtractor.build_composite_key(root_topic, cooccurrence_topic)
        self.assertEqual(expected, actual)

    def test_fill_topic_occurrences(self):
        self.extractor._fill_topic_occurrences("1001", "2432", "JT123456.xml")
        expected = [("JT123456.xml", -1)]
        actual = self.extractor._topics_occurrences_table["1001-2432"]
        self.assertEqual(expected, actual)

        self.extractor._fill_topic_occurrences("1001", "2432", "JT67890.xml")
        expected = [("JT123456.xml", -1), ("JT67890.xml", -1)]
        actual = self.extractor._topics_occurrences_table["1001-2432"]
        self.assertEqual(expected, actual)

        self.assertNotIn("2432-1001", self.extractor._topics_occurrences_table)

    def test_is_used_topic(self):
        target_topic = "2432-1001"
        topic = "2432"
        self.assertTrue(extractor.CoOccurrenceExtractor.is_used_topic(target_topic, topic))
        target_topic = "2432-1001"
        topic = "1001"
        self.assertTrue(extractor.CoOccurrenceExtractor.is_used_topic(target_topic, topic))
        target_topic = "2432-1001"
        topic = "9999"
        self.assertFalse(extractor.CoOccurrenceExtractor.is_used_topic(target_topic, topic))

    def test_is_final_leaf(self):
        topic = "1-2-3-4"
        self.assertFalse(self.extractor._is_final_leaf(topic))
        topic = "1-2-3-4-5"
        self.assertTrue(self.extractor._is_final_leaf(topic))

    def test_max_topic_from_root(self):
        topic = "1-2"
        actual = extractor.CoOccurrenceExtractor._max_topic_from_root(topic)
        self.assertEqual(2, actual)
        topic = "1-5-9"
        actual = extractor.CoOccurrenceExtractor._max_topic_from_root(topic)
        self.assertEqual(9, actual)
        topic = "1-10-123"
        actual = extractor.CoOccurrenceExtractor._max_topic_from_root(topic)
        self.assertEqual(123, actual)

    def test_save_cooccurrences_table(self):
        expected = ["1", "2", "3", "4"]
        self.extractor._topics_cooccurrences_table = expected

        self.extractor._save_cooccurrences_table()
        self.assertTrue(os.path.isfile("Full_Cooccurrences_Index"))
        import shelve
        d = shelve.open("Full_Cooccurrences_Index")
        actual = d["Corpus"]
        d.close()
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
    unittest.main()
