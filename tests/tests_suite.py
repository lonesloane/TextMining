import unittest
import test_analysis.test_cooccurrence_extractor as extractor
import test_analysis.test_corpus_analyzer as analyzer
import test_index.test_loader as loader
import test_search.test_proximity_finder as proximity_finder
import test_search.test_semantic_query as semantic_query
import test_index.test_validator as validator
import test_analysis.test_typeahead_index_builder as typeahead

suite_extractor = unittest.TestLoader().loadTestsFromModule(extractor)
suite_analyzer = unittest.TestLoader().loadTestsFromModule(analyzer)
suite_loader = unittest.TestLoader().loadTestsFromModule(loader)
suite_proximity = unittest.TestLoader().loadTestsFromModule(proximity_finder)
suite_semantic = unittest.TestLoader().loadTestsFromModule(semantic_query)
suite_validator = unittest.TestLoader().loadTestsFromModule(validator)
suite_typeahead = unittest.TestLoader().loadTestsFromModule(typeahead)

all_tests = unittest.TestSuite([suite_extractor, suite_analyzer, suite_loader, suite_proximity, suite_semantic,
                                suite_validator, suite_typeahead])

if __name__ == '__main__':
    unittest.TextTestRunner().run(all_tests)
