import logging
import os
import unittest

import datetime

from analysis.temporal import TopicsFrequencyExtractor, Frequency


class TopicsFrequencyExtractorTestCase(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
        logging.info('in setup')

        project_folder = os.path.abspath('/home/stephane/Playground/PycharmProjects/TextMining')
        self.output_tests_dir = os.path.join(project_folder, 'tests/testOutput')

        topics_occurrences_index_filename = os.path.join(self.output_tests_dir, 'Test_Topics_Occurrences_Index')
        topics_index_filename = os.path.join(self.output_tests_dir, 'Test_Topics_Index')
        files_dates_index_filename = os.path.join(self.output_tests_dir, 'Test_Files_Dates_Index')
        self.test_frequency_extractor = TopicsFrequencyExtractor(topics_occurrences_index_filename,
                                                                 files_dates_index_filename=files_dates_index_filename,
                                                                 topics_index_filename=topics_index_filename,
                                                                 highly_relevant_only=True)

    def tearDown(self):
        tmp_index_name = 'Test_Topics_Frequency_Index'
        if os.path.exists(os.path.join(self.output_tests_dir, tmp_index_name)):
            os.remove(os.path.join(self.output_tests_dir, tmp_index_name))
        csv_filename = 'Test_Topics_Frequency_CSV'
        if os.path.exists(os.path.join(self.output_tests_dir, csv_filename)):
            os.remove(os.path.join(self.output_tests_dir, csv_filename))

    def test_create(self):
        self.assertIsNotNone(self.test_frequency_extractor)
        self.assertIsNotNone(self.test_frequency_extractor._topics_frequency_index)
        self.assertIsNotNone(self.test_frequency_extractor._topics_occurrences_index)
        self.assertIsNotNone(self.test_frequency_extractor._files_dates_index)

    def test_extract_dates_for_topics(self):
        self.test_frequency_extractor.build_index(Frequency.ANNUAL)
        expected = [datetime.date(2015, 6, 22)]
        actual = self.test_frequency_extractor._topics_frequency_index['44']
        print actual
        self.assertEqual(expected, actual)

    def test_fill_annual_frequencies(self):
        t_f_i = dict()
        t_f_i['1'] = [datetime.date(2013, 06, 01), datetime.date(2013, 07, 01), datetime.date(2013, 07, 20),
                      datetime.date(2014, 01, 01), datetime.date(2014, 10, 10), datetime.date(2015, 01, 22),
                      datetime.date(2015, 03, 21), datetime.date(2015, 05, 15), datetime.date(2015, 12, 24)]
        t_f_i['2'] = [datetime.date(2005, 06, 01), datetime.date(2005, 07, 01), datetime.date(2005, 07, 20),
                      datetime.date(2005, 01, 01), datetime.date(2006, 10, 10), datetime.date(2006, 01, 22),
                      datetime.date(2006, 03, 21), datetime.date(2007, 05, 15), datetime.date(2007, 12, 24)]

        self.test_frequency_extractor._max_year = 2015
        self.test_frequency_extractor._min_year = 2005
        self.test_frequency_extractor._topics_frequency_index = t_f_i
        self.test_frequency_extractor.fill_annual_frequencies()

        annual_frequencies = self.test_frequency_extractor._topics_annual_frequencies
        expected = {2005: 0, 2006: 0, 2007: 0, 2008: 0, 2009: 0, 2010: 0, 2011: 0, 2012: 0, 2013: 3, 2014: 2, 2015: 4}
        actual = annual_frequencies['1']
        self.assertEqual(expected, actual)
        expected = {2005: 4, 2006: 3, 2007: 2, 2008: 0, 2009: 0, 2010: 0, 2011: 0, 2012: 0, 2013: 0, 2014: 0, 2015: 0}
        actual = annual_frequencies['2']
        self.assertEqual(expected, actual)

    @unittest.skip('Not yet implemented')
    def test_fill_monthly_frequencies(self):
        self.fail('not yet implemented')

    def test_update_min_max_year(self):
        self.assertEqual(self.test_frequency_extractor._max_year, 0)
        self.assertEqual(self.test_frequency_extractor._min_year, 0)
        self.test_frequency_extractor.update_min_max_year(datetime.date(2010, 01, 01))
        self.assertEqual(self.test_frequency_extractor._max_year, 2010)
        self.assertEqual(self.test_frequency_extractor._min_year, 2010)
        self.test_frequency_extractor.update_min_max_year(datetime.date(2001, 01, 01))
        self.assertEqual(self.test_frequency_extractor._max_year, 2010)
        self.assertEqual(self.test_frequency_extractor._min_year, 2001)
        self.test_frequency_extractor.update_min_max_year(datetime.date(2015, 01, 01))
        self.assertEqual(self.test_frequency_extractor._max_year, 2015)
        self.assertEqual(self.test_frequency_extractor._min_year, 2001)

    def test_shelve_index(self):
        tmp_index_name = 'Test_Topics_Frequency_Index'
        output_index_filename = os.path.join(self.output_tests_dir, tmp_index_name)

        self.assertFalse(os.path.isfile(output_index_filename))
        self.test_frequency_extractor.shelve_index(output_index_filename)
        self.assertTrue(os.path.isfile(output_index_filename))

    def test_export_as_csv(self):
        self.test_frequency_extractor.build_index(Frequency.ANNUAL)
        csv_filename = 'Test_Topics_Frequency_CSV'
        output_csv_filename = os.path.join(self.output_tests_dir, csv_filename)
        self.assertFalse(os.path.isfile(output_csv_filename))
        self.test_frequency_extractor.export_as_csv(output_csv_filename)
        self.assertTrue(os.path.isfile(output_csv_filename), msg="No CSV file found...")
        with open(output_csv_filename) as f:
            l = f.readline()
            self.assertEqual('topic_id,topic_label,2014,2015\n', l)
            l = f.readline()
            self.assertEqual('24,lbl_en_24,0,1\n', l)
            l = f.readline()
            self.assertEqual('39,lbl_en_39,1,0\n', l)


if __name__ == '__main__':
    unittest.main()
