# coding=utf-8
import logging
import os
import shelve
import unittest
import datetime

from analysis.corpus import Analyzer, get_date_from_folder

TEST_CORPUS_ROOT_FOLDER = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testCorpus"
TEST_TOPICS_OCCURRENCES_INDEX_FILENAME = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Occurrences_Index"
TEST_TOPICS_LABELS_INDEX_FILENAME = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Labels_Index"
TEST_TOPICS_INDEX_FILENAME = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Index"
TST_TOPICS_OCCURRENCES_INDEX_FILENAME = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Tst_Topics_Occurrences_Index"
TST_TOPICS_LABELS_INDEX_FILENAME = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Tst_Topics_Labels_Index"
TST_TOPICS_INDEX_FILENAME = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Tst_Topics_Index"


class AnalyzerTestCase(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
        self.analyzer = Analyzer(corpus_root_folder=TEST_CORPUS_ROOT_FOLDER)
        self.analyzer.process_topics_occurrences_index = True
        self.analyzer.process_topics_index = True
        self.analyzer.process_files_index = True


    def tearDown(self):
        if os.path.isfile(TST_TOPICS_OCCURRENCES_INDEX_FILENAME):
            os.remove(TST_TOPICS_OCCURRENCES_INDEX_FILENAME)
        if os.path.isfile(TST_TOPICS_LABELS_INDEX_FILENAME):
            os.remove(TST_TOPICS_LABELS_INDEX_FILENAME)

    def test_create_corpus_analyzer(self):
        self.assertIsNotNone(self.analyzer.topics_occurrences_index)
        self.assertEqual(TEST_CORPUS_ROOT_FOLDER, self.analyzer.corpus_root_folder)

    def test_extract_topics_labels_index(self):
        self.assertFalse(os.path.isfile(TST_TOPICS_LABELS_INDEX_FILENAME))

        Analyzer.extract_topics_labels_index(topics_index_filename=TEST_TOPICS_INDEX_FILENAME,
                                             topics_labels_index_filename=TST_TOPICS_LABELS_INDEX_FILENAME)

        self.assertTrue(os.path.isfile(TST_TOPICS_LABELS_INDEX_FILENAME))

        d = shelve.open(TST_TOPICS_LABELS_INDEX_FILENAME)
        topics_labels_index = d["Corpus"]
        d.close()

        self.assertEqual(94, len(topics_labels_index))
        self.assertTrue("1", topics_labels_index["lbl_en_1"])
        self.assertTrue("1", topics_labels_index["lbl_fr_1"])
        self.assertTrue("30", topics_labels_index["lbl_en_30"])
        self.assertTrue("30", topics_labels_index["lbl_fr_30"])

    def test_process_enrichment_result_only_highly_relevant(self):
        result_file = "JT03.xml"
        self.analyzer._process_enrichment_result(folder=TEST_CORPUS_ROOT_FOLDER, result_file=result_file,
                                                 only_highly_relevant=True)
        self.assertEqual(self.analyzer.topics_occurrences_index["45"], [("JT03.xml", "N")])
        self.assertTrue('5' in self.analyzer.topics_index)
        self.assertFalse('30' in self.analyzer.topics_index)

    def test_process_enrichment_result(self):
        result_file = "JT03.xml"
        self.analyzer._process_enrichment_result(folder=TEST_CORPUS_ROOT_FOLDER, result_file=result_file)
        print self.analyzer.topics_occurrences_index
        self.assertEqual(self.analyzer.topics_occurrences_index["45"], [("JT03.xml", "N")])
        self.assertTrue('5' in self.analyzer.topics_index)
        self.assertTrue('30' in self.analyzer.topics_index)
        self.assertEqual(self.analyzer.topics_index["45"], ('lbl_en_45', 'lbl_fr_45'))
        self.assertEqual(self.analyzer.files_index['JT03.xml'], [('30', 'N'), ('24', 'N'), ('42', 'N'), ('3', 'N'),
                                                                 ('35', 'N'), ('5', 'H'), ('18', 'N'), ('31', 'N'),
                                                                 ('14', 'N'), ('45', 'N'), ('9', 'H'), ('46', 'N'),
                                                                 ('38', 'N'), ('6', 'N'), ('7', 'N')])

        result_file = "JT06.xml"
        self.analyzer._process_enrichment_result(folder=TEST_CORPUS_ROOT_FOLDER, result_file=result_file)
        self.assertTrue('45' in self.analyzer.topics_index)
        self.assertEqual(self.analyzer.topics_occurrences_index["45"], [('JT03.xml', 'N'), ('JT06.xml', 'N')])
        self.assertEqual(self.analyzer.topics_index["45"], ('lbl_en_45', 'lbl_fr_45'))
        self.assertEqual(self.analyzer.files_index['JT03.xml'], [('30', 'N'), ('24', 'N'), ('42', 'N'), ('3', 'N'),
                                                                 ('35', 'N'), ('5', 'H'), ('18', 'N'), ('31', 'N'),
                                                                 ('14', 'N'), ('45', 'N'), ('9', 'H'), ('46', 'N'),
                                                                 ('38', 'N'), ('6', 'N'), ('7', 'N')])

    def test_remove_file_from_files_hash(self):
        self.analyzer.files_index['JT01.xml'] = [('1', 'N'), ('2', 'H')]
        self.analyzer.files_index['JT02.xml'] = [('3', 'N'), ('4', 'H')]
        self.analyzer.files_index['JT03.xml'] = [('5', 'N'), ('6', 'H')]

        self.assertEqual(3, len(self.analyzer.files_index))
        self.assertTrue('JT01.xml' in self.analyzer.files_index)
        self.assertTrue('JT02.xml' in self.analyzer.files_index)
        self.assertTrue('JT03.xml' in self.analyzer.files_index)
        self.analyzer._remove_file_from_files_index('JT01.xml')
        self.assertEqual(2, len(self.analyzer.files_index))
        self.assertFalse('JT01.xml' in self.analyzer.files_index)
        self.assertTrue('JT02.xml' in self.analyzer.files_index)
        self.assertTrue('JT03.xml' in self.analyzer.files_index)

    def test_remove_file_from_topics_occurrences_hash(self):
        self.analyzer.files_index['JT01.xml'] = [('1', 'N'), ('2', 'H')]
        self.analyzer.files_index['JT02.xml'] = [('3', 'N'), ('4', 'H')]
        self.analyzer.files_index['JT03.xml'] = [('5', 'N'), ('6', 'H')]
        result_file = 'JT01.xml'
        uri = "1"
        relevance = "N"
        self.analyzer._process_topics_occurrences(result_file=result_file, uri=uri, relevance=relevance)
        result_file = 'JT01.xml'
        uri = "2"
        relevance = "H"
        self.analyzer._process_topics_occurrences(result_file=result_file, uri=uri, relevance=relevance)
        result_file = 'JT02.xml'
        uri = "3"
        relevance = "N"
        self.analyzer._process_topics_occurrences(result_file=result_file, uri=uri, relevance=relevance)
        result_file = 'JT02.xml'
        uri = "4"
        relevance = "H"
        self.analyzer._process_topics_occurrences(result_file=result_file, uri=uri, relevance=relevance)
        result_file = 'JT03.xml'
        uri = "1"
        relevance = "H"
        self.analyzer._process_topics_occurrences(result_file=result_file, uri=uri, relevance=relevance)
        result_file = 'JT03.xml'
        uri = "2"
        relevance = "N"
        self.analyzer._process_topics_occurrences(result_file=result_file, uri=uri, relevance=relevance)
        result_file = 'JT04.xml'
        uri = "3"
        relevance = "H"
        self.analyzer._process_topics_occurrences(result_file=result_file, uri=uri, relevance=relevance)
        result_file = 'JT04.xml'
        uri = "4"
        relevance = "N"
        self.analyzer._process_topics_occurrences(result_file=result_file, uri=uri, relevance=relevance)

        self.assertEqual(4, len(self.analyzer.topics_occurrences_index))
        self.assertEqual([('JT01.xml', 'N'), ('JT03.xml', 'H')], self.analyzer.topics_occurrences_index['1'])
        self.assertEqual([('JT01.xml', 'H'), ('JT03.xml', 'N')], self.analyzer.topics_occurrences_index['2'])
        self.assertEqual([('JT02.xml', 'N'), ('JT04.xml', 'H')], self.analyzer.topics_occurrences_index['3'])
        self.assertEqual([('JT02.xml', 'H'), ('JT04.xml', 'N')], self.analyzer.topics_occurrences_index['4'])
        self.analyzer._remove_file_from_topics_occurrences_index('JT01.xml')
        self.assertEqual(4, len(self.analyzer.topics_occurrences_index))
        self.assertEqual([('JT03.xml', 'H')], self.analyzer.topics_occurrences_index['1'])
        self.assertEqual([('JT03.xml', 'N')], self.analyzer.topics_occurrences_index['2'])
        self.assertEqual([('JT02.xml', 'N'), ('JT04.xml', 'H')], self.analyzer.topics_occurrences_index['3'])
        self.assertEqual([('JT02.xml', 'H'), ('JT04.xml', 'N')], self.analyzer.topics_occurrences_index['4'])

    def test_dismiss_duplicates(self):
        _21_June = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testDuplicates/2015/06/21'
        _23_June = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testDuplicates/2015/06/23'

        result_file = "JT03.xml"
        self.analyzer._process_enrichment_result(folder=_21_June, result_file=result_file)
        result_file = "JT06.xml"
        self.analyzer._process_enrichment_result(folder=_21_June, result_file=result_file)
        self.assertEqual(self.analyzer.topics_occurrences_index["45"], [("JT03.xml", "N"), ("JT06.xml", "N")])
        self.assertEqual(self.analyzer.topics_index["45"], ('lbl_en_45', 'lbl_fr_45'))
        self.assertEqual(self.analyzer.files_index['JT03.xml'], [('30', 'N'), ('24', 'N'), ('42', 'N'), ('3', 'N'),
                                                                 ('35', 'N'), ('5', 'H'), ('18', 'N'), ('31', 'N'),
                                                                 ('14', 'N'), ('45', 'N'), ('9', 'H'), ('46', 'N'),
                                                                 ('38', 'N'), ('6', 'N'), ('7', 'N')])
        result_file = "JT03.xml"
        self.analyzer._process_enrichment_result(folder=_23_June, result_file=result_file)
        self.assertEqual(self.analyzer.topics_occurrences_index["45"], [("JT06.xml", "N"), ("JT03.xml", "N")])
        self.assertEqual(self.analyzer.topics_index["45"], ('lbl_en_45', 'lbl_fr_45'))
        self.assertEqual(self.analyzer.files_index['JT03.xml'], [('30', 'N'), ('24', 'N'), ('42', 'N'), ('3', 'N'),
                                                                 ('35', 'N'), ('5', 'H'), ('18', 'N'), ('31', 'N'),
                                                                 ('14', 'N'), ('45', 'N'), ('9', 'H'), ('46', 'N'),
                                                                 ('38', 'N'), ('6', 'N'), ('7', 'N')])

    def test_debug_duplicates(self):
        topic_occurrences = [('JT00103895.xml', 'N'), ('JT00103933.xml', 'N'), ('00088280.xml', 'H'), ('00088281.xml', 'H'), ('JT00103937.xml', 'H'), ('JT00103941.xml', 'H'), ('JT00103982.xml', 'N'), ('00088282.xml', 'N'), ('JT00104010.xml', 'N'), ('JT00104098.xml', 'N'), ('JT00104139.xml', 'N'), ('JT00104141.xml', 'N'), ('JT00104179.xml', 'N'), ('00088288.xml', 'H'), ('JT00104190.xml', 'H'), ('JT00104192.xml', 'H'), ('JT00104213.xml', 'N'), ('JT00104214.xml', 'N'), ('JT00104250.xml', 'H'), ('JT00104267.xml', 'N'), ('JT00104268.xml', 'N'), ('JTT1072203.xml', 'H'), ('IMP20007623ENG.xml', 'N'), ('JT00104293.xml', 'H'), ('JT00104300.xml', 'H'), ('JT00104302.xml', 'N'), ('JT00104327.xml', 'N'), ('JT00104330.xml', 'H'), ('JT00021334.xml', 'N'), ('JT00104348.xml', 'H'), ('JT00104357.xml', 'N'), ('JT00104367.xml', 'N'), ('JT00104368.xml', 'N'), ('JT00104374.xml', 'N'), ('JT00104380.xml', 'N'), ('JT00104382.xml', 'N'), ('JT00104386.xml', 'N'), ('JT00104406.xml', 'N'), ('JT00104408.xml', 'H'), ('JT00104412.xml', 'H'), ('JT00104414.xml', 'N'), ('JT00104462.xml', 'N'), ('JT00104466.xml', 'H'), ('JT00104467.xml', 'H'), ('00088298.xml', 'N'), ('00088299.xml', 'N'), ('JT00104479.xml', 'H'), ('JT00104507.xml', 'N'), ('JT00104509.xml', 'N'), ('JT00104514.xml', 'H'), ('JT00104535.xml', 'N'), ('JT00104543.xml', 'N'), ('JT00104551.xml', 'H'), ('JT00104553.xml', 'N'), ('IMP20006700ENG.xml', 'N'), ('IMP20006701ENG.xml', 'N'), ('JT00104566.xml', 'N'), ('JT00104574.xml', 'N'), ('JT00104611.xml', 'N'), ('JT00104612.xml', 'N'), ('JT00104624.xml', 'N'), ('JT00104636.xml', 'N'), ('JT00104685.xml', 'H'), ('00088304.xml', 'H'), ('00088305.xml', 'H'), ('JT00104677.xml', 'N'), ('JT00104686.xml', 'H'), ('JT00104688.xml', 'H'), ('JT00104694.xml', 'N'), ('JT00104718.xml', 'N'), ('00088306.xml', 'H'), ('00088307.xml', 'H'), ('JT00021337.xml', 'H'), ('JT00104811.xml', 'N'), ('JT00104818.xml', 'N'), ('JT00104846.xml', 'N'), ('JT00104878.xml', 'N'), ('JT00104882.xml', 'N'), ('JT00104886.xml', 'N'), ('JT00104894.xml', 'N'), ('00088318.xml', 'H'), ('JT00104944.xml', 'N'), ('JT00104950.xml', 'N'), ('00088331.xml', 'N'), ('JT00104999.xml', 'N'), ('JT00105004.xml', 'H'), ('JT00105009.xml', 'N'), ('JT00105023.xml', 'N'), ('JT00105026.xml', 'N'), ('JTT1086225.xml', 'N'), ('JT00105066.xml', 'H'), ('JT00105083.xml', 'N'), ('JT00105092.xml', 'H'), ('JT00105106.xml', 'N'), ('JT00105109.xml', 'N'), ('JT00105125.xml', 'H'), ('JT00105131.xml', 'H'), ('JT00105143.xml', 'N'), ('JT00105158.xml', 'N'), ('JT00105164.xml', 'N'), ('JT00105248.xml', 'N'), ('JT00105221.xml', 'N'), ('JT00105226.xml', 'H'), ('JT00105241.xml', 'H'), ('JT00105249.xml', 'N'), ('JT00105270.xml', 'N'), ('JT00105271.xml', 'N'), ('JT00105279.xml', 'N'), ('00088349.xml', 'H'), ('00088350.xml', 'H'), ('JT00105324.xml', 'H'), ('JT00105334.xml', 'N'), ('JT00105337.xml', 'N'), ('JT00105346.xml', 'N'), ('JT00105356.xml', 'N'), ('00088352.xml', 'H'), ('00088353.xml', 'N'), ('JT00020924.xml', 'N'), ('JT00105384.xml', 'H'), ('JT00105416.xml', 'N'), ('00088355.xml', 'H'), ('00088356.xml', 'H'), ('JT00105459.xml', 'H'), ('JT00105469.xml', 'N'), ('JT00105492.xml', 'N'), ('JT00105493.xml', 'N'), ('JT00105522.xml', 'H'), ('JT00105529.xml', 'H'), ('00088357.xml', 'H'), ('00088358.xml', 'H'), ('JT00105550.xml', 'H'), ('JT00105594.xml', 'N'), ('JT00105602.xml', 'H'), ('JT00105603.xml', 'H'), ('JT00105624.xml', 'N'), ('JT00105692.xml', 'H'), ('JT00105698.xml', 'N'), ('JT00105705.xml', 'H'), ('00088361.xml', 'N'), ('00088362.xml', 'N'), ('JT00105746.xml', 'N'), ('JT00105795.xml', 'H'), ('JT00105800.xml', 'N'), ('JT00105803.xml', 'N'), ('00088365.xml', 'H'), ('00088366.xml', 'N'), ('00088367.xml', 'N'), ('IMP20007623FRE.xml', 'N'), ('JT00021217.xml', 'H'), ('JT00105833.xml', 'H'), ('JT00105854.xml', 'H'), ('JT00105860.xml', 'H'), ('JT00105883.xml', 'N'), ('JT00105887.xml', 'H'), ('JT00105905.xml', 'N'), ('JT00105908.xml', 'H'), ('JT00105942.xml', 'N'), ('JT00106014.xml', 'N'), ('00088370.xml', 'H'), ('00088371.xml', 'H'), ('JT00021343.xml', 'N'), ('JT00021344.xml', 'N'), ('JT00105965.xml', 'H'), ('JT00105995.xml', 'N'), ('JT00105999.xml', 'H'), ('JT00106001.xml', 'H'), ('JT00106015.xml', 'N'), ('JT00106020.xml', 'N'), ('JT00106023.xml', 'H'), ('JT00106049.xml', 'N')]
        self.analyzer.files_index['JT00104374.xml'] = [('1', 'N')]
        self.analyzer.topics_occurrences_index["1"] = topic_occurrences
        self.assertTrue(('JT00104374.xml', 'N') in self.analyzer.topics_occurrences_index["1"])
        self.analyzer._remove_file_from_topics_occurrences_index('JT00104374.xml')
        self.assertFalse(('JT00104374.xml', 'N') in self.analyzer.topics_occurrences_index["1"])

    def test_is_posterior(self):
        _21_June = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testDuplicates/2015/06/21'
        _23_June = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testDuplicates/2015/06/23'
        _25_June = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testDuplicates/2015/06/25'
        self.analyzer.processed_files['JT03.xml'] = _23_June
        self.assertFalse(self.analyzer._is_posterior(result_file='JT03.xml', current_folder=_21_June))
        self.assertTrue(self.analyzer._is_posterior(result_file='JT03.xml', current_folder=_25_June))

    def test_get_date_from_folder(self):
        _21_June = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testDuplicates/2015/06/21'
        _23_June = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testDuplicates/2015/06/23'
        expected_date = datetime.date(2015, 6, 21)
        actual_date = get_date_from_folder(_21_June)
        print actual_date
        self.assertEqual(expected_date, actual_date)

        expected_date = datetime.date(2015, 6, 23)
        actual_date = get_date_from_folder(_23_June)
        self.assertEqual(expected_date, actual_date)

    def test_process_file_topics(self):
        result_file = 'JT01.xml'
        uri1 = '1'
        relevance1 = 'N'
        self.analyzer._process_file_topics(result_file, uri1, relevance1)
        expected = [('1', 'N')]
        actual = self.analyzer.files_index[result_file]
        self.assertEqual(expected, actual)

        uri1 = '2'
        relevance1 = 'H'
        self.analyzer._process_file_topics(result_file, uri1, relevance1)
        expected = [('1', 'N'), ('2', 'H')]
        actual = self.analyzer.files_index[result_file]
        self.assertEqual(expected, actual)

    def test_process_topics_occurrences(self):
        result_file = 'JT04.xml'
        uri = "38"
        relevance = "N"
        self.analyzer._process_topics_occurrences(result_file=result_file, uri=uri, relevance=relevance)
        self.assertEqual(self.analyzer.topics_occurrences_index["38"], [("JT04.xml", "N")])

        uri = "47"
        relevance = "H"
        self.analyzer._process_topics_occurrences(result_file=result_file, uri=uri, relevance=relevance)
        self.assertEqual(self.analyzer.topics_occurrences_index["38"], [("JT04.xml", "N")])
        self.assertEqual(self.analyzer.topics_occurrences_index["47"], [("JT04.xml", "H")])

        result_file = 'JT05.xml'
        uri = "38"
        relevance = "H"
        self.analyzer._process_topics_occurrences(result_file=result_file, uri=uri, relevance=relevance)
        self.assertEqual(self.analyzer.topics_occurrences_index["38"], [("JT04.xml", "N"), ("JT05.xml", "H")])
        self.assertEqual(self.analyzer.topics_occurrences_index["47"], [("JT04.xml", "H")])

        # try to add same file to topic, should raise an exception
        self.assertRaises(Exception, self.analyzer._process_topics_occurrences, result_file, uri, relevance)

    def test_strip_uri(self):
        uri = "http://kim.oecd.org/Taxonomy/Topics#T187"
        result = Analyzer._strip_uri(uri)
        self.assertEqual("187", result)

    def test_shelve_index(self):
        expected = {"testTopic": [("JT00", "N"), ("JT01", "H")]}
        Analyzer.shelve_index(index_filename=TST_TOPICS_OCCURRENCES_INDEX_FILENAME,
                              index_data=expected)

        import shelve
        d = shelve.open(TST_TOPICS_OCCURRENCES_INDEX_FILENAME)
        actual = d["Corpus"]
        d.close()
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()
