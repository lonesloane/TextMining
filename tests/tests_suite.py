import logging
import unittest
import test_analysis.test_cooccurrence_extractor as extractor
import test_analysis.test_corpus as analyzer
import test_index.test_loader as loader
import test_search.test_proximity_finder as proximity_finder
import test_search.test_semantic_query as semantic_query
import test_index.test_validator as validator
import test_analysis.test_typeahead as typeahead
import test_gui as gui

suite_extractor = unittest.TestLoader().loadTestsFromModule(extractor)
suite_analyzer = unittest.TestLoader().loadTestsFromModule(analyzer)
suite_loader = unittest.TestLoader().loadTestsFromModule(loader)
suite_proximity = unittest.TestLoader().loadTestsFromModule(proximity_finder)
suite_semantic = unittest.TestLoader().loadTestsFromModule(semantic_query)
suite_validator = unittest.TestLoader().loadTestsFromModule(validator)
suite_typeahead = unittest.TestLoader().loadTestsFromModule(typeahead)
suite_gui = unittest.TestLoader().loadTestsFromModule(gui)

all_tests = unittest.TestSuite([suite_extractor, suite_analyzer, suite_loader, suite_proximity, suite_semantic,
                                suite_validator, suite_typeahead, suite_gui])

if __name__ == '__main__':
    '''
    logger = logging.getLogger(__name__)
    # create file handler which logs even debug messages
    fh = logging.FileHandler('tests_suite.log', mode='w')
    fh.setLevel(logging.DEBUG)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    '''
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
    unittest.TextTestRunner().run(all_tests)
