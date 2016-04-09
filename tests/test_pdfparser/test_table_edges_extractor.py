import logging
import unittest
import pdfparser.table_edges_extractor as extractor


class EdgesExtractorTestCase(unittest.TestCase):

    def test_adjacent(self):
        # TODO: fix this! The test depends on the hard coded value of ADJ_DISTANCE!!!
        self.assertTrue(extractor.adjacent(25.0, 24.1))
        self.assertTrue(extractor.adjacent(25.0, 25.9))
        self.assertFalse(extractor.adjacent(25.0, 24.0))
        self.assertFalse(extractor.adjacent(25.0, 26.0))

    def test_same_cell(self):
        cell1 = [1.0, 2.0, 3.5, 4.5]
        cell2 = [1.0, 2.0, 3.5, 4.5]
        self.assertTrue(extractor.same_cell(cell1, cell2))
        cell3 = [1.0, 2.0, 3.5, 4.0]
        self.assertFalse(extractor.same_cell(cell1, cell3))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
    unittest.main()
