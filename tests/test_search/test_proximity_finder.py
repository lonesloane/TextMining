import unittest
import search.proximity_finder as finder


class ProximityFinderTestCase(unittest.TestCase):
    topics_occurrences_index_filename="/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Occurrences_Index"
    topics_index_filename="/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Index"

    def setUp(self):
        self.finder = finder.ProximityFinder(
            topics_index_filename=ProximityFinderTestCase.topics_index_filename,
            topics_occurrences_index_filename=ProximityFinderTestCase.topics_occurrences_index_filename)

    def test_create(self):
        expected = [('JT02.xml', 'N'), ('JT04.xml', 'N'), ('JT01.xml', 'H'), ('JT06.xml', 'N')]
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
        self.finder.proximity_results = {'JT01.xml': [('47', 100), ('18', 100), ('43', 100), ('27', 100)],
                                         'JT04.xml': [('44', 100), ('39', 100), ('47', 1), ('20', 1)],
                                         'JT06.xml': [('10', 100), ('16', 100), ('25', 1)],
                                         'JT09.xml': [('39', 100), ('7', 100), ('30', 100), ('9', 100)],
                                         'JT05.xml': [('44', 100), ('43', 100), ('10', 100), ('9', 100), ('16', 100)],
                                         'JT07.xml': [('44', 1), ('11', 100), ('18', 100), ('10', 100), ('9', 100),
                                                      ('16', 100), ('40', 100)],
                                         'JT08.xml': [('44', 100), ('18', 100), ('43', 100), ('10', 100), ('40', 100)],
                                         'JT10.xml': [('44', 100), ('39', 1), ('7', 100), ('47', 1), ('25', 1),
                                                      ('27', 100)],
                                         'JT03.xml': [('7', 100), ('30', 100), ('18', 100), ('9', 1)],
                                         'JT02.xml': [('30', 100), ('9', 100), ('20', 10000), ('25', 1), ('27', 100)]}

        actual = self.finder._trim_results(['JT01.xml'])

        expected = {'JT04.xml': [('44', 100), ('39', 100), ('47', 1), ('20', 1)],
                    'JT06.xml': [('10', 100), ('16', 100), ('25', 1)],
                    'JT09.xml': [('39', 100), ('7', 100), ('30', 100), ('9', 100)],
                    'JT05.xml': [('44', 100), ('43', 100), ('10', 100), ('9', 100), ('16', 100)],
                    'JT07.xml': [('44', 1), ('11', 100), ('18', 100), ('10', 100), ('9', 100), ('16', 100), ('40', 100)],
                    'JT08.xml': [('44', 100), ('18', 100), ('43', 100), ('10', 100), ('40', 100)],
                    'JT10.xml': [('44', 100), ('39', 1), ('7', 100), ('47', 1), ('25', 1), ('27', 100)],
                    'JT03.xml': [('7', 100), ('30', 100), ('18', 100), ('9', 1)],
                    'JT02.xml': [('30', 100), ('9', 100), ('20', 10000), ('25', 1), ('27', 100)]}

        self.assertItemsEqual(expected, actual)

    def test_build_proximity_results(self):
        signature = [('44', 'N'), ('39', 'N'), ('11', 'N'), ('7', 'N'), ('47', 'N'), ('30', 'N'), ('18', 'N'),
                     ('43', 'N'), ('10', 'N'), ('9', 'N'), ('20', 'H'), ('16', 'N'), ('40', 'N'), ('25', 'H'),
                     ('27', 'N')]
        results = self.finder.build_proximity_results(semantic_signature=signature).proximity_results
        expected_1 = ('JT01.xml', [('47', 'lbl_en_47', 'lbl_fr_47', 100), ('18', 'lbl_en_18', 'lbl_fr_18', 100),
                                   ('43', 'lbl_en_43', 'lbl_fr_43', 100), ('27', 'lbl_en_27', 'lbl_fr_27', 100)])
        expected_2 = ('JT04.xml', [('44', 'lbl_en_44', 'lbl_fr_44', 100), ('39', 'lbl_en_39', 'lbl_fr_39', 100),
                                   ('47', 'lbl_en_47', 'lbl_fr_47', 1), ('20', 'lbl_en_20', 'lbl_fr_20', 1)])
        expected_3 = ('JT02.xml', [('30', 'lbl_en_30', 'lbl_fr_30', 100), ('9', 'lbl_en_9', 'lbl_fr_9', 100),
                                   ('20', 'lbl_en_20', 'lbl_fr_20', 10000), ('25', 'lbl_en_25', 'lbl_fr_25', 1),
                                   ('27', 'lbl_en_27', 'lbl_fr_27', 100)])
        actual_1 = results[0]
        actual_2 = results[1]
        actual_3 = results[-1]
        self.assertEqual(expected_1, actual_1)
        self.assertEqual(expected_2, actual_2)
        self.assertEqual(expected_3, actual_3)

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
        signature = [('44', 'N'), ('39', 'N'), ('11', 'N'), ('7', 'N'), ('47', 'N'), ('30', 'N'), ('18', 'N'),
                     ('43', 'N'), ('10', 'N'), ('9', 'N'), ('20', 'H'), ('16', 'N'), ('40', 'N'), ('25', 'H'),
                     ('27', 'N')]

        sorted_results_1 = self.finder.build_proximity_results(semantic_signature=signature,
                                                               sort_criteria=finder.SortBy.TOTAL_MATCHES,
                                                               minimum_match_number=1).proximity_results
        actual_1 = len(sorted_results_1)
        self.assertEqual(actual_1, 10)

        sorted_results_2 = self.finder.build_proximity_results(semantic_signature=signature,
                                                               sort_criteria=finder.SortBy.TOTAL_MATCHES,
                                                               minimum_match_number=2).proximity_results
        actual_2 = len(sorted_results_2)
        self.assertEqual(actual_2, 10)

        sorted_results_3 = self.finder.build_proximity_results(semantic_signature=signature,
                                                               sort_criteria=finder.SortBy.TOTAL_MATCHES,
                                                               minimum_match_number=3).proximity_results
        actual_3 = len(sorted_results_3)
        self.assertEqual(actual_3, 10)

        sorted_results_4 = self.finder.build_proximity_results(semantic_signature=signature,
                                                               sort_criteria=finder.SortBy.TOTAL_MATCHES,
                                                               minimum_match_number=4).proximity_results
        actual_4 = len(sorted_results_4)
        self.assertEqual(actual_4, 9)

        sorted_results_5 = self.finder.build_proximity_results(semantic_signature=signature,
                                                               sort_criteria=finder.SortBy.TOTAL_MATCHES,
                                                               minimum_match_number=5).proximity_results
        actual_5 = len(sorted_results_5)
        self.assertEqual(actual_5, 5)

        sorted_results_6 = self.finder.build_proximity_results(semantic_signature=signature,
                                                               sort_criteria=finder.SortBy.TOTAL_MATCHES,
                                                               minimum_match_number=6).proximity_results
        actual_6 = len(sorted_results_6)
        self.assertEqual(actual_6, 2)

        sorted_results_7 = self.finder.build_proximity_results(semantic_signature=signature,
                                                               sort_criteria=finder.SortBy.TOTAL_MATCHES,
                                                               minimum_match_number=7).proximity_results
        actual_7 = len(sorted_results_7)
        self.assertEqual(actual_7, 1)

        sorted_results_8 = self.finder.build_proximity_results(semantic_signature=signature,
                                                               sort_criteria=finder.SortBy.TOTAL_MATCHES,
                                                               minimum_match_number=8).proximity_results
        actual_8 = len(sorted_results_8)
        self.assertEqual(actual_8, 0)

if __name__ == '__main__':
    unittest.main()
