import logging
import unittest
import test_analysis.test_cooccurrence_extractor as extractor
import test_analysis.test_corpus as analyzer
import test_analysis.test_temporal as temporal
import test_index.test_loader as loader
import test_search.test_proximity_finder as proximity_finder
import test_search.test_semantic_query as semantic_query
import test_index.test_validator as validator
import test_analysis.test_typeahead as typeahead
import test_gui.test_searchclient as gui
import test_pdfparser.test_table_edges_extractor as table_extractor
import test_pdfparser.test_text_extractor as text_extractor
import test_pdfparser.test_pdf_page_filter as pdf_page_filter
import test_pdfparser.test_summarizer as summarizer
import test_pdfparser.test_text_table_extractor as text_table_extractor

suite_extractor = unittest.TestLoader().loadTestsFromModule(extractor)
suite_analyzer = unittest.TestLoader().loadTestsFromModule(analyzer)
suite_temporal = unittest.TestLoader().loadTestsFromModule(temporal)
suite_loader = unittest.TestLoader().loadTestsFromModule(loader)
suite_proximity = unittest.TestLoader().loadTestsFromModule(proximity_finder)
suite_semantic = unittest.TestLoader().loadTestsFromModule(semantic_query)
suite_validator = unittest.TestLoader().loadTestsFromModule(validator)
suite_typeahead = unittest.TestLoader().loadTestsFromModule(typeahead)
suite_gui = unittest.TestLoader().loadTestsFromModule(gui)
suite_table_extractor = unittest.TestLoader().loadTestsFromModule(table_extractor)
suite_text_extractor = unittest.TestLoader().loadTestsFromModule(text_extractor)

suite_pdf_page_filter = unittest.TestLoader().loadTestsFromModule(pdf_page_filter)
suite_summarizer = unittest.TestLoader().loadTestsFromModule(summarizer)
suite_text_table_extractor = unittest.TestLoader().loadTestsFromModule(text_table_extractor)

all_tests = unittest.TestSuite([suite_extractor, suite_analyzer, suite_temporal, suite_loader, suite_proximity,
                                suite_semantic, suite_validator, suite_typeahead, suite_gui, suite_table_extractor,
                                suite_text_extractor, suite_pdf_page_filter, suite_summarizer,
                                suite_text_table_extractor])

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
    unittest.TextTestRunner().run(all_tests)
