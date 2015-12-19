import unittest

import search.proximity_finder as finder


class ProximityFinderTestCase(unittest.TestCase):

    def setUp(self):
        self.finder = finder.ProximityFinder(hash_table_filename="../testOutput/Test_Topics_Occurrences_Index")

    def test_create(self):
        self.assertEqual(None, self.finder.corpus_table)
        self.assertEqual("../testOutput/Test_Topics_Occurrences_Index", self.finder.hash_table_filename)

    def test_load_corpus_table(self):
        self.finder.load_corpus_table()
        expected = [('JT02.xml', 'N'), ('JT04.xml', 'N'), ('JT01.xml', 'H'), ('JT06.xml', 'N')]
        actual = self.finder.corpus_table['22']

        self.assertEqual(expected, actual)

    def test_build_proximity_results(self):
        signature = ["44", "39", "11", "7", "47", "30", "18", "43", "10", "9", "20", "29", "40", "25", "27"]
        results = self.finder.build_proximity_results(semantic_signature=signature).proximity_results
        expected_1 = ('JT01.xml', [{'normal_match': 4, 'total_match': 4, 'high_match': 0},
                                   [('47', 'N'), ('18', 'N'), ('43', 'N'), ('27', 'N')]])
        expected_2 = ('JT04.xml', [{'normal_match': 4, 'total_match': 5, 'high_match': 1},
                                   [('44', 'N'), ('39', 'N'), ('47', 'H'), ('20', 'N'), ('29', 'N')]])
        expected_3 = ('JT02.xml', [{'normal_match': 4, 'total_match': 5, 'high_match': 1},
                                   [('30', 'N'), ('9', 'N'), ('20', 'H'), ('25', 'N'), ('27', 'N')]])
        actual_1 = results[0]
        actual_2 = results[1]
        actual_3 = results[-1]
        self.assertEqual(expected_1, actual_1)
        self.assertEqual(expected_2, actual_2)
        self.assertEqual(expected_3, actual_3)

    def test_build_results_by_number_match(self):
        signature = ["44", "39", "11", "7", "47", "30", "18", "43", "10", "9", "20", "29", "40", "25", "27"]
        sorted_results = self.finder.build_proximity_results(semantic_signature=signature,
                                                             sort_criteria=finder.ProximityFinder.TOTAL_MATCHES).proximity_results
        expected = ('JT07.xml', [{'normal_match': 5, 'total_match': 6, 'high_match': 1},
                                 [('44', 'H'), ('11', 'N'), ('18', 'N'), ('10', 'N'), ('9', 'N'), ('40', 'N')]])
        actual = sorted_results[0]
        self.assertEqual(expected, actual)

    def test_build_results_by_number_high(self):
        signature = ["44", "39", "11", "7", "47", "30", "18", "43", "10", "9", "20", "29", "40", "25", "27"]
        sorted_results = self.finder.build_proximity_results(semantic_signature=signature,
                                                             sort_criteria=finder.ProximityFinder.NB_HIGH_MATCHES).proximity_results
        expected = ('JT10.xml', [{'normal_match': 4, 'total_match': 6, 'high_match': 2},
                                 [('44', 'N'), ('39', 'H'), ('7', 'N'), ('47', 'H'), ('25', 'N'), ('27', 'N')]])
        actual = sorted_results[0]
        self.assertEqual(expected, actual)

    def test_build_results_minimum_matches(self):
        signature = ["44", "39", "11", "7", "47", "30", "18", "43", "10", "9", "20", "29", "40", "25", "27"]
        sorted_results_1 = self.finder.build_proximity_results(semantic_signature=signature,
                                                               sort_criteria=finder.ProximityFinder.TOTAL_MATCHES,
                                                               minimum_match_number=1).proximity_results
        sorted_results_2 = self.finder.build_proximity_results(semantic_signature=signature,
                                                               sort_criteria=finder.ProximityFinder.TOTAL_MATCHES,
                                                               minimum_match_number=2).proximity_results
        sorted_results_3 = self.finder.build_proximity_results(semantic_signature=signature,
                                                               sort_criteria=finder.ProximityFinder.TOTAL_MATCHES,
                                                               minimum_match_number=3).proximity_results
        sorted_results_4 = self.finder.build_proximity_results(semantic_signature=signature,
                                                               sort_criteria=finder.ProximityFinder.TOTAL_MATCHES,
                                                               minimum_match_number=4).proximity_results
        sorted_results_5 = self.finder.build_proximity_results(semantic_signature=signature,
                                                               sort_criteria=finder.ProximityFinder.TOTAL_MATCHES,
                                                               minimum_match_number=5).proximity_results
        sorted_results_6 = self.finder.build_proximity_results(semantic_signature=signature,
                                                               sort_criteria=finder.ProximityFinder.TOTAL_MATCHES,
                                                               minimum_match_number=6).proximity_results
        sorted_results_7 = self.finder.build_proximity_results(semantic_signature=signature,
                                                               sort_criteria=finder.ProximityFinder.TOTAL_MATCHES,
                                                               minimum_match_number=7).proximity_results
        actual_1 = len(sorted_results_1)
        actual_2 = len(sorted_results_2)
        actual_3 = len(sorted_results_3)
        actual_4 = len(sorted_results_4)
        actual_5 = len(sorted_results_5)
        actual_6 = len(sorted_results_6)
        actual_7 = len(sorted_results_7)

        self.assertEqual(actual_1, 10)
        self.assertEqual(actual_2, 10)
        self.assertEqual(actual_3, 9)
        self.assertEqual(actual_4, 9)
        self.assertEqual(actual_5, 6)
        self.assertEqual(actual_6, 2)
        self.assertEqual(actual_7, 0)

if __name__ == '__main__':
    unittest.main()
