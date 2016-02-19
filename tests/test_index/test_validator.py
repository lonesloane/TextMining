import logging
import unittest
import indexfiles.validator as validator


class IndexValidatorTestCase(unittest.TestCase):
    def test_validate_files_index(self):
        files_index = dict()
        files_index['JT01.xml'] = [('1', 'N'), ('2', 'H'), ('3', 'N')]
        files_index['JT02.xml'] = [('1', 'H'), ('4', 'N'), ('5', 'N')]
        files_index['JT03.xml'] = [('4', 'N'), ('6', 'H'), ('7', 'N'), ('6', 'N')]
        files_index['JT01.xml'] = [('1', 'N'), ('2', 'H'), ('3', 'N')]
        duplicate_topics = validator.validate_files_index(files_index)
        self.assertEqual([('6', 'JT03.xml')], duplicate_topics)

    def test_validate_topics_occurrences_index(self):
        topics_occurrences_index = dict()
        topics_occurrences_index['1'] = [('JT01.xml', 'N'), ('JT02.xml', 'H'), ('JT03.xml', 'N'), ('JT04.xml', 'H')]
        topics_occurrences_index['2'] = [('JT01.xml', 'H'), ('JT05.xml', 'N'), ('JT06.xml', 'H'), ('JT07.xml', 'N'),
                                         ('JT01.xml', 'N')]
        topics_occurrences_index['3'] = [('JT01.xml', 'N'), ('JT02.xml', 'H'), ('JT09.xml', 'H')]

        duplicate_files = validator.validate_topics_occurrences_index(topics_occurrences_index)
        self.assertEqual([('2', 'JT01.xml')], duplicate_files)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
    unittest.main()
