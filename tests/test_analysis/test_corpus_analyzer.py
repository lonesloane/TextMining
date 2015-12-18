# coding=utf-8
import os
import shelve
import shutil
import unittest
import analysis.corpus_analyzer as analyzer

TEST_CORPUS_ROOT_FOLDER = "../testCorpus/"
TEST_TOPICS_OCCURRENCES_INDEX_FILENAME = "../testOutput/Test_Topics_Occurrences_Index"
TEST_TOPICS_LABELS_INDEX_FILENAME = "../testOutput/Test_Topics_Labels_Index"
TEST_TOPICS_INDEX_FILENAME = "../testOutput/Test_Topics_Index"


class CorpusAnalyzerTestCase(unittest.TestCase):

    def setUp(self):
        self.analyzer = analyzer.CorpusAnalyzer(corpus_root_folder=TEST_CORPUS_ROOT_FOLDER)

    def tearDown(self):
        if os.path.isfile(TEST_TOPICS_OCCURRENCES_INDEX_FILENAME):
            os.remove(TEST_TOPICS_OCCURRENCES_INDEX_FILENAME)
        if os.path.isfile(TEST_TOPICS_LABELS_INDEX_FILENAME):
            os.remove(TEST_TOPICS_LABELS_INDEX_FILENAME)

    def test_create_corpus_analyzer(self):
        self.assertIsNotNone(self.analyzer.topics_occurrences_hash)
        self.assertEqual(TEST_CORPUS_ROOT_FOLDER, self.analyzer.corpus_root_folder)

    def test_extract_topics_labels_index(self):
        self.assertFalse(os.path.isfile(TEST_TOPICS_LABELS_INDEX_FILENAME))

        analyzer.CorpusAnalyzer.extract_topics_labels_index(topics_index_filename=TEST_TOPICS_INDEX_FILENAME,
                                                            topics_labels_index_filename=TEST_TOPICS_LABELS_INDEX_FILENAME)

        self.assertTrue(os.path.isfile(TEST_TOPICS_LABELS_INDEX_FILENAME))

        d = shelve.open(TEST_TOPICS_LABELS_INDEX_FILENAME)
        topics_labels_index = d["Corpus"]
        d.close()

        self.assertEqual(94, len(topics_labels_index))
        self.assertTrue("1", topics_labels_index["lbl_en_1"])
        self.assertTrue("1", topics_labels_index["lbl_fr_1"])
        self.assertTrue("30", topics_labels_index["lbl_en_30"])
        self.assertTrue("30", topics_labels_index["lbl_fr_30"])

    def test_process_enrichment_result(self):
        result_file = "JT03.xml"

        self.analyzer._process_enrichment_result(folder=TEST_CORPUS_ROOT_FOLDER, result_file=result_file)
        self.assertEqual(self.analyzer.topics_occurrences_hash["45"], [("JT03.xml", "N")])

    def test_process_topics_occurrences(self):
        result_file = 'JT04.xml'
        uri = "38"
        relevance = "N"
        self.analyzer._process_topics_occurrences(result_file=result_file, uri=uri, relevance=relevance)
        self.assertEqual(self.analyzer.topics_occurrences_hash["38"], [("JT04.xml", "N")])

        uri = "47"
        relevance = "H"
        self.analyzer._process_topics_occurrences(result_file=result_file, uri=uri, relevance=relevance)
        self.assertEqual(self.analyzer.topics_occurrences_hash["38"], [("JT04.xml", "N")])
        self.assertEqual(self.analyzer.topics_occurrences_hash["47"], [("JT04.xml", "H")])

        result_file = 'JT05.xml'
        uri = "38"
        relevance = "H"
        self.analyzer._process_topics_occurrences(result_file=result_file, uri=uri, relevance=relevance)
        self.assertEqual(self.analyzer.topics_occurrences_hash["38"], [("JT04.xml", "N"), ("JT05.xml", "H")])
        self.assertEqual(self.analyzer.topics_occurrences_hash["47"], [("JT04.xml", "H")])

    def test_strip_uri(self):
        uri = "http://kim.oecd.org/Taxonomy/Topics#T187"
        result = analyzer.CorpusAnalyzer._strip_uri(uri)
        self.assertEqual("187", result)

    def test_shelve_index(self):
        expected = {"testTopic": [("JT00", "N"), ("JT01", "H")]}
        analyzer.CorpusAnalyzer.shelve_index(index_filename=TEST_TOPICS_OCCURRENCES_INDEX_FILENAME,
                                             index_data=expected)

        import shelve
        d = shelve.open(TEST_TOPICS_OCCURRENCES_INDEX_FILENAME)
        actual = d["Corpus"]
        d.close()
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
