import logging
import unittest
import search.proximity_finder as finder
from index.loader import TopicsOccurrencesIndex, TopicsIndex, FilesIndex


class ProximityFinderTestCase(unittest.TestCase):
    _topics_occurrences_index_filename = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Occurrences_Index"
    _topics_index_filename = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Index"
    _files_index_filename = "/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Files_Index"

    def setUp(self):
        self._topics_index = TopicsIndex(self._topics_index_filename)
        self._topics_occurrences_index = TopicsOccurrencesIndex(self._topics_occurrences_index_filename)
        self._files_index = FilesIndex(self._files_index_filename)

        self.finder = finder.ProximityFinder(
            topics_index=self._topics_index,
            topics_occurrences_index=self._topics_occurrences_index,
            files_index=self._files_index)

    def test_create(self):
        expected = [('JT02.xml', 'N'), ('JT04.xml', 'H'), ('JT01.xml', 'H'), ('JT06.xml', 'N')]
        actual = self.finder.topics_occurrences_index.get_files_for_topic('22')

        self.assertEqual(expected, actual)

    def test_compute_proximity_score(self):
        target_relevance = 'N'
        relevance = 'N'
        expected = 100
        actual = finder.ProximityFinder.compute_proximity_score(target_relevance, relevance)
        self.assertEqual(expected, actual)

        target_relevance = 'H'
        relevance = 'N'
        expected = 1
        actual = finder.ProximityFinder.compute_proximity_score(target_relevance, relevance)
        self.assertEqual(expected, actual)

        target_relevance = 'N'
        relevance = 'H'
        expected = 1
        actual = finder.ProximityFinder.compute_proximity_score(target_relevance, relevance)
        self.assertEqual(expected, actual)

        target_relevance = 'H'
        relevance = 'H'
        expected = 10000
        actual = finder.ProximityFinder.compute_proximity_score(target_relevance, relevance)
        self.assertEqual(expected, actual)

    def test_trim_results(self):
        self.finder.proximity_results = {'JT01.xml': [('47', "", "", 100), ('18', "", "", 100), ('43', "", "", 100),
                                                      ('27', "", "", 100)],
                                         'JT04.xml': [('44', "", "", 100), ('39', "", "", 100), ('47', "", "", 1),
                                                      ('20', "", "", 1)],
                                         'JT06.xml': [('10', "", "", 100), ('16', "", "", 100), ('25', "", "", 1)],
                                         'JT09.xml': [('39', "", "", 100), ('7', "", "", 100), ('30', "", "", 100),
                                                      ('9', "", "", 100)],
                                         'JT05.xml': [('44', "", "", 100), ('43', "", "", 100), ('10', "", "", 100),
                                                      ('9', "", "", 100), ('16', "", "", 100)],
                                         'JT07.xml': [('44', "", "", 1), ('11', "", "", 100), ('18', "", "", 10000),
                                                      ('10', "", "", 10000), ('9', "", "", 100), ('16', "", "", 100),
                                                      ('40', "", "", 10000)],
                                         'JT08.xml': [('44', "", "", 100), ('18', "", "", 100), ('43', "", "", 100),
                                                      ('10', "", "", 100), ('40', "", "", 100)],
                                         'JT10.xml': [('44', "", "", 100), ('39', "", "", 1), ('7', "", "", 100),
                                                      ('47', "", "", 1), ('25', "", "", 1), ('27', "", "", 100)],
                                         'JT03.xml': [('7', "", "", 100), ('30', "", "", 100), ('18', "", "", 100),
                                                      ('9', "", "", 1)],
                                         'JT02.xml': [('30', "", "", 100), ('9', "", "", 100), ('20', "", "", 10000),
                                                      ('25', "", "", 1), ('27', "", "", 100)]}

        expected = {'JT04.xml': [('44', '', '', 100), ('39', '', '', 100), ('47', '', '', 1), ('20', '', '', 1)],
                    'JT06.xml': [('10', '', '', 100), ('16', '', '', 100), ('25', '', '', 1)],
                    'JT09.xml': [('39', '', '', 100), ('7', '', '', 100), ('30', '', '', 100), ('9', '', '', 100)],
                    'JT05.xml': [('44', '', '', 100), ('43', '', '', 100), ('10', '', '', 100), ('9', '', '', 100),
                                 ('16', '', '', 100)],
                    'JT07.xml': [('44', '', '', 1), ('11', '', '', 100), ('18', '', '', 10000), ('10', '', '', 10000),
                                 ('9', '', '', 100), ('16', '', '', 100), ('40', '', '', 10000)],
                    'JT08.xml': [('44', '', '', 100), ('18', '', '', 100), ('43', '', '', 100), ('10', '', '', 100),
                                 ('40', '', '', 100)],
                    'JT10.xml': [('44', '', '', 100), ('39', '', '', 1), ('7', '', '', 100), ('47', '', '', 1),
                                 ('25', '', '', 1), ('27', '', '', 100)],
                    'JT03.xml': [('7', '', '', 100), ('30', '', '', 100), ('18', '', '', 100), ('9', '', '', 1)],
                    'JT02.xml': [('30', '', '', 100), ('9', '', '', 100), ('20', '', '', 10000), ('25', '', '', 1),
                                 ('27', '', '', 100)]}
        actual = self.finder._trim_results(['JT01.xml'], 0).proximity_results

        self.assertItemsEqual(expected, actual)

        expected = {'JT07.xml': [('44', '', '', 1), ('11', '', '', 100), ('18', '', '', 10000), ('10', '', '', 10000),
                                 ('9', '', '', 100), ('16', '', '', 100), ('40', '', '', 10000)]}
        actual = self.finder._trim_results(['JT01.xml'], 2).proximity_results

        self.assertEqual(1, len(actual))
        self.assertFalse('JT04.xml' in actual)
        self.assertItemsEqual(expected, actual)

    def test_has_minimum_hrt_matches(self):
        scored_topic = [('44', 'lbl_en_44', 'lbl_fr_44', 100), ('39', 'lbl_en_39', 'lbl_fr_39', 100),
                        ('47', 'lbl_en_47', 'lbl_fr_47', 1), ('20', 'lbl_en_20', 'lbl_fr_20', 1)]
        minimum_hrt_match_number = 1
        actual = self.finder._has_minimum_hrt_matches(scored_topic, minimum_hrt_match_number)
        self.assertFalse(actual)
        scored_topic = [('44', 'lbl_en_44', 'lbl_fr_44', 1), ('11', 'lbl_en_11', 'lbl_fr_11', 100),
                        ('18', 'lbl_en_18', 'lbl_fr_18', 10000), ('10', 'lbl_en_10', 'lbl_fr_10', 10000),
                        ('9', 'lbl_en_9', 'lbl_fr_9', 100), ('16', 'lbl_en_16', 'lbl_fr_16', 100),
                        ('40', 'lbl_en_40', 'lbl_fr_40', 10000)]
        actual = self.finder._has_minimum_hrt_matches(scored_topic, minimum_hrt_match_number)
        self.assertTrue(actual)
        minimum_hrt_match_number = 4
        actual = self.finder._has_minimum_hrt_matches(scored_topic, minimum_hrt_match_number)
        self.assertFalse(actual)

    def test_build_proximity_results(self):
        signature = [('44', 'N'), ('39', 'N'), ('11', 'N'), ('7', 'N'), ('47', 'N'), ('30', 'N'), ('18', 'N'),
                     ('43', 'N'), ('10', 'N'), ('9', 'N'), ('20', 'H'), ('16', 'N'), ('40', 'N'), ('25', 'H'),
                     ('27', 'N')]
        results = self.finder.build_proximity_results(semantic_signature=signature).proximity_results
        expected_1 = [('47', 'lbl_en_47', 'lbl_fr_47', 100), ('18', 'lbl_en_18', 'lbl_fr_18', 100),
                                   ('43', 'lbl_en_43', 'lbl_fr_43', 100), ('27', 'lbl_en_27', 'lbl_fr_27', 100)]
        expected_2 = [('44', 'lbl_en_44', 'lbl_fr_44', 100), ('39', 'lbl_en_39', 'lbl_fr_39', 100),
                                   ('47', 'lbl_en_47', 'lbl_fr_47', 1), ('20', 'lbl_en_20', 'lbl_fr_20', 1)]
        expected_3 = [('30', 'lbl_en_30', 'lbl_fr_30', 100), ('9', 'lbl_en_9', 'lbl_fr_9', 100),
                                   ('20', 'lbl_en_20', 'lbl_fr_20', 10000), ('25', 'lbl_en_25', 'lbl_fr_25', 1),
                                   ('27', 'lbl_en_27', 'lbl_fr_27', 100)]
        actual_1 = results['JT01.xml']
        actual_2 = results['JT04.xml']
        actual_3 = results['JT02.xml']
        self.assertEqual(expected_1, actual_1)
        self.assertEqual(expected_2, actual_2)
        self.assertEqual(expected_3, actual_3)

    def test_build_proximity_results_with_required_topics(self):
        signature = [('44', 'N'), ('39', 'N'), ('11', 'N'), ('7', 'N'), ('47', 'N'), ('30', 'N'), ('18', 'N'),
                     ('43', 'N'), ('10', 'N'), ('9', 'N'), ('20', 'H'), ('16', 'N'), ('40', 'N'), ('25', 'H'),
                     ('27', 'N')]
        required_topics = ['20']
        results = self.finder.build_proximity_results(semantic_signature=signature,
                                                      required_topics=required_topics).proximity_results
        self.assertEqual(2, len(results))
        expected_2 = [('44', 'lbl_en_44', 'lbl_fr_44', 100), ('39', 'lbl_en_39', 'lbl_fr_39', 100),
                                   ('47', 'lbl_en_47', 'lbl_fr_47', 1), ('20', 'lbl_en_20', 'lbl_fr_20', 1)]
        expected_3 = [('30', 'lbl_en_30', 'lbl_fr_30', 100), ('9', 'lbl_en_9', 'lbl_fr_9', 100),
                                   ('20', 'lbl_en_20', 'lbl_fr_20', 10000), ('25', 'lbl_en_25', 'lbl_fr_25', 1),
                                   ('27', 'lbl_en_27', 'lbl_fr_27', 100)]
        actual_2 = results['JT04.xml']
        actual_3 = results['JT02.xml']
        self.assertEqual(expected_2, actual_2)
        self.assertEqual(expected_3, actual_3)

        required_topics = ['20', '25']
        results = self.finder.build_proximity_results(semantic_signature=signature,
                                                      required_topics=required_topics).proximity_results
        self.assertEqual(1, len(results))
        expected_3 = [('30', 'lbl_en_30', 'lbl_fr_30', 100), ('9', 'lbl_en_9', 'lbl_fr_9', 100),
                                   ('20', 'lbl_en_20', 'lbl_fr_20', 10000), ('25', 'lbl_en_25', 'lbl_fr_25', 1),
                                   ('27', 'lbl_en_27', 'lbl_fr_27', 100)]
        actual_3 = results['JT02.xml']
        self.assertEqual(expected_3, actual_3)

    def test_contains_topic(self):
        f = ('JT04.xml', 'N')
        topic = '44'
        self.assertTrue(self.finder._contains_topic(f, topic))

        topic = '33'
        self.assertFalse(self.finder._contains_topic(f, topic))

    def test_trim_matching_files(self):
        actual_relevant_files = self._topics_occurrences_index.get_files_for_topic('44')
        expected_relevant_files = [('JT08.xml', 'N'), ('JT05.xml', 'N'), ('JT04.xml', 'N'), ('JT07.xml', 'H'),
                                   ('JT10.xml', 'N')]
        self.assertListEqual(expected_relevant_files, actual_relevant_files)

        trimmed_relevant_files = self.finder._trim_matching_files(actual_relevant_files, ['20'])
        expected_trimmed = [('JT04.xml', 'N')]
        self.assertListEqual(expected_trimmed, trimmed_relevant_files)

        trimmed_relevant_files = self.finder._trim_matching_files(actual_relevant_files, ['44'])
        expected_trimmed = [('JT08.xml', 'N'), ('JT05.xml', 'N'), ('JT04.xml', 'N'), ('JT07.xml', 'H'),
                            ('JT10.xml', 'N')]
        self.assertListEqual(expected_trimmed, trimmed_relevant_files)

        trimmed_relevant_files = self.finder._trim_matching_files(actual_relevant_files, ['44', '20'])
        expected_trimmed = [('JT04.xml', 'N')]
        self.assertListEqual(expected_trimmed, trimmed_relevant_files)

    def test_sort_by_proximity_score(self):
        signature = [('44', 'N'), ('39', 'N'), ('11', 'N'), ('7', 'N'), ('47', 'N'), ('30', 'N'), ('18', 'N'),
                     ('43', 'N'), ('10', 'N'), ('9', 'N'), ('20', 'H'), ('16', 'N'), ('40', 'N'), ('25', 'H'),
                     ('27', 'N')]
        sorted_results = self.finder.build_proximity_results(semantic_signature=signature,
                                                             sort_criteria=finder.SortBy.PROXIMITY_SCORE).proximity_results
        expected = ('JT02.xml', [('30', 'lbl_en_30', 'lbl_fr_30', 100), ('9', 'lbl_en_9', 'lbl_fr_9', 100),
                                 ('20', 'lbl_en_20', 'lbl_fr_20', 10000), ('25', 'lbl_en_25', 'lbl_fr_25', 1),
                                 ('27', 'lbl_en_27', 'lbl_fr_27', 100)])
        actual = sorted_results[0]
        self.assertEqual(expected, actual)

    def test_sort_by_number_match(self):
        signature = [('44', 'N'), ('39', 'N'), ('11', 'N'), ('7', 'N'), ('47', 'N'), ('30', 'N'), ('18', 'N'),
                     ('43', 'N'), ('10', 'N'), ('9', 'N'), ('20', 'H'), ('16', 'N'), ('40', 'N'), ('25', 'H'),
                     ('27', 'N')]
        sorted_results = self.finder.build_proximity_results(semantic_signature=signature,
                                                             sort_criteria=finder.SortBy.TOTAL_MATCHES).proximity_results
        expected = ('JT07.xml', [('44', 'lbl_en_44', 'lbl_fr_44', 1), ('11', 'lbl_en_11', 'lbl_fr_11', 100),
                                 ('18', 'lbl_en_18', 'lbl_fr_18', 100), ('10', 'lbl_en_10', 'lbl_fr_10', 100),
                                 ('9', 'lbl_en_9', 'lbl_fr_9', 100), ('16', 'lbl_en_16', 'lbl_fr_16', 100),
                                 ('40', 'lbl_en_40', 'lbl_fr_40', 100)])
        actual = sorted_results[0]
        self.assertEqual(expected, actual)

    def test_sort_by_number_high(self):
        signature = [('44', 'N'), ('39', 'H'), ('11', 'N'), ('7', 'N'), ('47', 'H'), ('30', 'N'), ('18', 'N'),
                     ('43', 'N'), ('10', 'N'), ('9', 'N'), ('20', 'H'), ('16', 'N'), ('40', 'N'), ('25', 'H'),
                     ('27', 'N')]
        sorted_results = self.finder.build_proximity_results(semantic_signature=signature,
                                                             sort_criteria=finder.SortBy.NB_HIGH_MATCHES).proximity_results
        expected = ('JT10.xml', [('44', 'lbl_en_44', 'lbl_fr_44', 100), ('39', 'lbl_en_39', 'lbl_fr_39', 10000),
                                 ('7', 'lbl_en_7', 'lbl_fr_7', 100), ('47', 'lbl_en_47', 'lbl_fr_47', 10000),
                                 ('25', 'lbl_en_25', 'lbl_fr_25', 1), ('27', 'lbl_en_27', 'lbl_fr_27', 100)])
        actual = sorted_results[0]
        self.assertEqual(expected, actual)

    def test_minimum_matches(self):
        signature = [('44', 'N'), ('39', 'N'), ('11', 'H'), ('7', 'N'), ('47', 'N'), ('30', 'N'), ('18', 'N'),
                     ('43', 'N'), ('10', 'N'), ('9', 'N'), ('20', 'H'), ('16', 'N'), ('40', 'N'), ('25', 'H'),
                     ('27', 'N')]

        sorted_results_1 = self.finder.build_proximity_results(semantic_signature=signature,
                                                               sort_criteria=finder.SortBy.TOTAL_MATCHES,
                                                               minimum_hrt_match_number=0).proximity_results
        actual_1 = len(sorted_results_1)
        self.assertEqual(actual_1, 10)

        sorted_results_2 = self.finder.build_proximity_results(semantic_signature=signature,
                                                               sort_criteria=finder.SortBy.TOTAL_MATCHES,
                                                               minimum_hrt_match_number=1).proximity_results
        actual_2 = len(sorted_results_2)
        self.assertEqual(actual_2, 1)

        sorted_results_3 = self.finder.build_proximity_results(semantic_signature=signature,
                                                               sort_criteria=finder.SortBy.TOTAL_MATCHES,
                                                               minimum_hrt_match_number=2).proximity_results
        actual_3 = len(sorted_results_3)
        self.assertEqual(actual_3, 0)

        sorted_results_4 = self.finder.build_proximity_results(semantic_signature=signature,
                                                               sort_criteria=finder.SortBy.TOTAL_MATCHES,
                                                               minimum_hrt_match_number=3).proximity_results
        actual_4 = len(sorted_results_4)
        self.assertEqual(actual_4, 0)

        sorted_results_5 = self.finder.build_proximity_results(semantic_signature=signature,
                                                               sort_criteria=finder.SortBy.TOTAL_MATCHES,
                                                               minimum_hrt_match_number=4).proximity_results
        actual_5 = len(sorted_results_5)
        self.assertEqual(actual_5, 0)

    def test_get_total_proximity_score(self):
        signature = [('44', 'N'), ('39', 'N'), ('11', 'H'), ('7', 'N'), ('47', 'N'), ('30', 'N'), ('18', 'N'),
                     ('43', 'N'), ('10', 'N'), ('9', 'N'), ('20', 'H'), ('16', 'N'), ('40', 'N'), ('25', 'H'),
                     ('27', 'N')]
        scored_topics = [('44', 'lbl_44', 'lbl_44', 100),('39', 'lbl_44', 'lbl_44', 100),
                         ('11', 'lbl_44', 'lbl_44', 10000), ('7', 'lbl_44', 'lbl_44', 1),
                         ('47', 'lbl_44', 'lbl_44', 100), ('30', 'lbl_44', 'lbl_44', 100),
                         ('18', 'lbl_44', 'lbl_44', 1), ('43', 'lbl_44', 'lbl_44', 100),
                         ('10', 'lbl_44', 'lbl_44', 10000)]
        expected = 20502
        actual = finder.get_total_proximity_score(scored_topics)
        self.assertEqual(expected, actual)

        expected = 65
        actual = finder.get_total_proximity_score(scored_topics, signature)
        self.assertEqual(expected, actual)

    def test_get_max_score(self):
        signature = [('44', 'N'), ('39', 'N'), ('11', 'H'), ('7', 'N'), ('47', 'N'), ('30', 'N'), ('18', 'N'),
                     ('43', 'N'), ('10', 'N'), ('9', 'N'), ('20', 'H'), ('16', 'N'), ('40', 'N'), ('25', 'H'),
                     ('27', 'N')]
        actual = finder.get_max_score(signature)
        expected = 31200
        self.assertEqual(expected, actual)

    def test_jsonify(self):
        proximity_results = list()
        proximity_results.append(('JT01.xml', [('47', 'lbl_en_47', 'lbl_fr_47', 100),
                                               ('18', 'lbl_en_18', 'lbl_fr_18', 100),
                                               ('43', 'lbl_en_43', 'lbl_fr_43', 100),
                                               ('27', 'lbl_en_27', 'lbl_fr_27', 100)]))
        proximity_results.append(('JT02.xml', [('44', 'lbl_en_44', 'lbl_fr_44', 100),
                                               ('39', 'lbl_en_39', 'lbl_fr_39', 100),
                                               ('47', 'lbl_en_47', 'lbl_fr_47', 1),
                                               ('20', 'lbl_en_20', 'lbl_fr_20', 1)]))
        proximity_results.append(('JT03.xml', [('30', 'lbl_en_30', 'lbl_fr_30', 100),
                                               ('9', 'lbl_en_9', 'lbl_fr_9', 100),
                                               ('20', 'lbl_en_20', 'lbl_fr_20', 10000),
                                               ('25', 'lbl_en_25', 'lbl_fr_25', 1),
                                               ('27', 'lbl_en_27', 'lbl_fr_27', 100)]))
        expected = {'JT01.xml': [{'topic': '47', 'score': 100, 'lbl_en': 'lbl_en_47', 'lbl_fr': 'lbl_fr_47'},
                                 {'topic': '18', 'score': 100, 'lbl_en': 'lbl_en_18', 'lbl_fr': 'lbl_fr_18'},
                                 {'topic': '43', 'score': 100, 'lbl_en': 'lbl_en_43', 'lbl_fr': 'lbl_fr_43'},
                                 {'topic': '27', 'score': 100, 'lbl_en': 'lbl_en_27', 'lbl_fr': 'lbl_fr_27'}],
                    'JT03.xml': [{'topic': '30', 'score': 100, 'lbl_en': 'lbl_en_30', 'lbl_fr': 'lbl_fr_30'},
                                 {'topic': '9', 'score': 100, 'lbl_en': 'lbl_en_9', 'lbl_fr': 'lbl_fr_9'},
                                 {'topic': '20', 'score': 10000, 'lbl_en': 'lbl_en_20', 'lbl_fr': 'lbl_fr_20'},
                                 {'topic': '25', 'score': 1, 'lbl_en': 'lbl_en_25', 'lbl_fr': 'lbl_fr_25'},
                                 {'topic': '27', 'score': 100, 'lbl_en': 'lbl_en_27', 'lbl_fr': 'lbl_fr_27'}],
                    'JT02.xml': [{'topic': '44', 'score': 100, 'lbl_en': 'lbl_en_44', 'lbl_fr': 'lbl_fr_44'},
                                 {'topic': '39', 'score': 100, 'lbl_en': 'lbl_en_39', 'lbl_fr': 'lbl_fr_39'},
                                 {'topic': '47', 'score': 1, 'lbl_en': 'lbl_en_47', 'lbl_fr': 'lbl_fr_47'},
                                 {'topic': '20', 'score': 1, 'lbl_en': 'lbl_en_20', 'lbl_fr': 'lbl_fr_20'}]}

        actual = finder.jsonify(proximity_results)
        print actual

        self.assertEqual(expected, actual)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
    unittest.main()
