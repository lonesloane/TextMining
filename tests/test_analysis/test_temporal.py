import logging
import os
import unittest

import datetime

from analysis.temporal import TopicsFrequencyExtractor


class TopicsFrequencyExtractorTestCase(unittest.TestCase):

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
        logging.info('in setup')

        project_folder = os.path.abspath('/home/stephane/Playground/PycharmProjects/TextMining')
        self.output_tests_dir = os.path.join(project_folder, 'tests/testOutput')

        topics_occurrences_index_filename = os.path.join(self.output_tests_dir, 'Test_Topics_Occurrences_Index')
        files_dates_index_filename = os.path.join(self.output_tests_dir, 'Test_Files_Dates_Index')
        self.test_frequency_extractor = TopicsFrequencyExtractor(topics_occurrences_index_filename,
                                                                 files_dates_index_filename=files_dates_index_filename)

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

    def test_build(self):
        self.test_frequency_extractor.build()
        expected = [datetime.date(2014, 6, 15), datetime.date(2014, 6, 21), datetime.date(2015, 2, 5),
                    datetime.date(2015, 6, 15), datetime.date(2015, 6, 22)]
        actual = self.test_frequency_extractor._topics_frequency_index['44']
        self.assertEqual(expected, actual)

    def test_shelve_index(self):
        tmp_index_name = 'Test_Topics_Frequency_Index'
        output_index_filename = os.path.join(self.output_tests_dir, tmp_index_name)

        self.assertFalse(os.path.isfile(output_index_filename))
        self.test_frequency_extractor.shelve_index(output_index_filename)
        self.assertTrue(os.path.isfile(output_index_filename))

    def test_export_as_csv(self):
        self.test_frequency_extractor.build()
        csv_filename = 'Test_Topics_Frequency_CSV'
        output_csv_filename = os.path.join(self.output_tests_dir, csv_filename)
        self.assertFalse(os.path.isfile(output_csv_filename))
        self.test_frequency_extractor.export_as_csv(output_csv_filename)
        self.assertTrue(os.path.isfile(output_csv_filename), msg="No CSV file found...")
        with open(output_csv_filename) as f:
            l = f.readline()
            self.assertEqual('28,2015-02-05\n', l)
            l = f.readline()
            self.assertEqual('29,2014-06-21,2015-06-15\n', l)


if __name__ == '__main__':
    unittest.main()
