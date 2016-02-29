import logging
import os
import unittest

import search.semantic_query as search
from indexfiles.loader import FilesIndex, TopicsOccurrencesIndex, TopicsLabelsIndex, TopicsIndex

project_folder = os.path.abspath('/home/stephane/Playground/PycharmProjects/TextMining')


class QueryProcessorTestCase(unittest.TestCase):

    _files_index_filename = os.path.join(project_folder, 'tests/testOutput/Test_Files_Index')
    _topics_occurrences_index_filename = os.path.join(project_folder, 'tests/testOutput/Test_Topics_Occurrences_Index')
    _topics_labels_index_filename = os.path.join(project_folder, 'tests/testOutput/Test_Topics_Labels_Index')
    _topics_index_filename = os.path.join(project_folder, 'tests/testOutput/Test_Topics_Index')

    def setUp(self):
        logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
        self._files_index = FilesIndex(self._files_index_filename)
        self._topics_occurrences_index = TopicsOccurrencesIndex(self._topics_occurrences_index_filename)
        self._topics_labels_index = TopicsLabelsIndex(self._topics_labels_index_filename)
        self._topics_index = TopicsIndex(self._topics_index_filename)

        self.processor = search.QueryProcessor(files_index=self._files_index,
                                               topics_occurrences_index=self._topics_occurrences_index,
                                               topics_labels_index=self._topics_labels_index,
                                               topics_index=self._topics_index)

    def test_init(self):
        self.assertIsNotNone(self.processor._files_index)
        self.assertIsNotNone(self.processor._topics_occurrences_index)
        self.assertIsNotNone(self.processor._topics_labels_index)
        self.assertIsNotNone(self.processor._topics_index)

    def test_load_files_index(self):
        self.assertTrue('JT01.xml'in self.processor._files_index._index)
        expected = [('18', 'N'), ('36', 'N'), ('31', 'N'), ('26', 'N'), ('15', 'N'), ('46', 'N'), ('38', 'N'),
                    ('27', 'N'), ('43', 'N'), ('37', 'N'), ('1', 'N'), ('47', 'N'), ('48', 'H'), ('8', 'N'),
                    ('22', 'H')]
        actual = self.processor._files_index._index['JT01.xml']

        self.assertEqual(expected, actual)

    def test_load_topics_occurrences_index(self):
        self.assertTrue('1' in self.processor._topics_occurrences_index._index)
        expected = [('JT02.xml', 'N'), ('JT08.xml', 'N'), ('JT01.xml', 'N'), ('JT07.xml', 'N')]
        actual = self.processor._topics_occurrences_index._index['1']

        self.assertEqual(expected, actual)

    def test_load_topics_labels_index(self):
        self.assertTrue('lbl_en_1' in self.processor._topics_labels_index._index)
        expected = '1'
        actual = self.processor._topics_labels_index._index['lbl_en_1']

        self.assertEqual(expected, actual)

    def test_load_topics_index(self):
        self.assertTrue('1' in self.processor._topics_index.index)
        expected = ('lbl_en_1', 'lbl_fr_1')
#        actual = self.processor._topics_index.index['1']
        actual = self.processor.get_topic_labels_from_id('1')

        self.assertEqual(expected, actual)

    def test_get_files_for_single_topic(self):
        topic = "1"
        expected_len = 4
        expected_files = ['JT02.xml', 'JT08.xml', 'JT01.xml', 'JT07.xml']

        actual = self.processor._get_files_for_topic(topic)

        self.assertEqual(expected_len, len(actual))
        self.assertEqual(expected_files, actual)

    def test_get_topics_for_files(self):
        topic = ['1']
        files = ['JT02.xml', 'JT08.xml', 'JT01.xml', 'JT07.xml']
        expected_len = 35
        expected_topics = [2, 3, 5, 6, 8, 9, 10, 11, 14, 15, 16, 18, 20, 22, 24, 25, 26, 27, 28, 30, 31, 33, 35,
                           36, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48]

        actual = self.processor._get_topics_for_files(files, ignored_topic=topic)

        self.assertEqual(expected_len, len(actual))
        self.assertEqual(expected_topics, actual)

        topic = ['1', '2']
        files = ['JT02.xml', 'JT08.xml', 'JT01.xml', 'JT07.xml']
        expected_len = 34
        expected_topics = [3, 5, 6, 8, 9, 10, 11, 14, 15, 16, 18, 20, 22, 24, 25, 26, 27, 28, 30, 31, 33, 35,
                           36, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48]

        actual = self.processor._get_topics_for_files(files, ignored_topic=topic)

        self.assertEqual(expected_len, len(actual))
        self.assertEqual(expected_topics, actual)

    def test_get_topic_id_from_label(self):
        logging.getLogger(__name__).info('begin test: test_get_topic_id_from_label')

        topic_label = "lbl_en_1"
        expected = '1'
        actual = self.processor.get_topic_id_from_label(topic_label)
        self.assertEqual(expected, actual)

        topic_label = "lbl_fr_1"
        expected = '1'
        actual = self.processor.get_topic_id_from_label(topic_label)
        self.assertEqual(expected, actual)

        topic_label = "lbl_en_2"
        expected = '2'
        actual = self.processor.get_topic_id_from_label(topic_label)
        self.assertEqual(expected, actual)

        topic_label = "lbl_en_xxx"
        expected = None
        actual = self.processor.get_topic_id_from_label(topic_label)
        self.assertEqual(expected, actual)

    def test_get_topic_labels_from_id(self):
        topic_id = '1'
        expected = ('lbl_en_1', 'lbl_fr_1')
        actual = self.processor.get_topic_labels_from_id(topic_id)
        self.assertEqual(expected, actual)

    def test_execute_by_topic_id(self):
        topic = ["1"]
        expected_files = ['JT02.xml', 'JT08.xml', 'JT01.xml', 'JT07.xml']
        expected_topics = [2, 3, 5, 6, 8, 9, 10, 11, 14, 15, 16, 18, 20, 22, 24, 25, 26, 27, 28, 30, 31, 33, 35,
                           36, 37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48]
        actual_files, actual_topics = self.processor.execute(topic)

        self.assertListEqual(sorted(expected_files), sorted(actual_files))
        self.assertListEqual(expected_topics, actual_topics)

        topic = ["1", "31"]
        expected_files = ['JT01.xml', 'JT02.xml', 'JT08.xml']
        expected_topics = [2, 3, 6, 8, 9, 10, 14, 15, 18, 20, 22, 24, 25, 26, 27, 28, 30, 33, 35, 36, 37, 38, 40,
                           42, 43, 44, 46, 47, 48]
        actual_files, actual_topics = self.processor.execute(topic)

        self.assertListEqual(sorted(expected_files), sorted(actual_files))
        self.assertListEqual(expected_topics, actual_topics)

        topic = ["31", "1"]
        expected_files = ['JT01.xml', 'JT02.xml', 'JT08.xml']
        expected_topics = [2, 3, 6, 8, 9, 10, 14, 15, 18, 20, 22, 24, 25, 26, 27, 28, 30, 33, 35, 36, 37, 38, 40,
                           42, 43, 44, 46, 47, 48]
        actual_files, actual_topics = self.processor.execute(topic)

        self.assertListEqual(sorted(expected_files), sorted(actual_files))
        self.assertListEqual(expected_topics, actual_topics)

        topic = ["1", "31", "42"]
        expected_files = ['JT02.xml']
        expected_topics = [2, 3, 6, 9, 20, 22, 24, 25, 27, 30, 35, 37]
        actual_files, actual_topics = self.processor.execute(topic)

        self.assertListEqual(sorted(expected_files), sorted(actual_files))
        self.assertListEqual(expected_topics, actual_topics)

        topic = ["31", "42", "1"]
        expected_files = ['JT02.xml']
        expected_topics = [2, 3, 6, 9, 20, 22, 24, 25, 27, 30, 35, 37]
        actual_files, actual_topics = self.processor.execute(topic)

        self.assertListEqual(sorted(expected_files), sorted(actual_files))
        self.assertListEqual(expected_topics, actual_topics)

    def test_execute_ordered(self):
        # Validates results are ordered according to topics relevance
        topic = ['22', '31']
        expected_files = ['JT04.xml', 'JT01.xml', 'JT02.xml']
        actual_files, actual_topics = self.processor.execute(topic, order_by_relevance=True)
        self.assertListEqual(sorted(expected_files), sorted(actual_files))  # check same elements
        self.assertEqual('JT04.xml', actual_files[0])  # check actual order
        self.assertEqual('JT01.xml', actual_files[1])  # check actual order

    def test_build_semantic_signature(self):
        enrichment_result = [('2', 'H'), ('3', 'N')]
        expected_result = [
            {'relevance': 'H', 'id': '2', 'label': {'fr': 'lbl_fr_2', 'en': 'lbl_en_2'}},
            {'relevance': 'N', 'id': '3', 'label': {'fr': 'lbl_fr_3', 'en': 'lbl_en_3'}}
        ]

        actual_result = self.processor.build_semantic_signature(enrichment_result)

        self.assertEqual(expected_result, actual_result)

    def test_get_topics_from_topic_ids(self):
        topic_ids = ['1', '2', '3']
        expected = [
            {'id': '1', 'label': {'fr': 'lbl_fr_1', 'en': 'lbl_en_1'}},
            {'id': '2', 'label': {'fr': 'lbl_fr_2', 'en': 'lbl_en_2'}},
            {'id': '3', 'label': {'fr': 'lbl_fr_3', 'en': 'lbl_en_3'}}]
        actual = self.processor._get_topics_from_topic_ids(topic_ids)

        self.assertEqual(expected, actual)

    def test_search_documents_by_topics(self):
        topic_list = ['1']
        expected_result = {'search_terms': [{'id': '1', 'label': {'fr': 'lbl_fr_1', 'en': 'lbl_en_1'}}],
                           'topics': [
                               2, 3, 5, 6, 8, 9, 10, 11, 14, 15, 16, 18, 20, 22, 24, 25, 26, 27, 28, 30, 31, 33,35, 36,
                               37, 38, 40, 41, 42, 43, 44, 45, 46, 47, 48],
                           'documents': [
                               {'semantic_signature': [
                                   {'relevance': 'H', 'id': '5', 'label': {'fr': 'lbl_fr_5', 'en': 'lbl_en_5'}},
                                   {'relevance': 'N', 'id': '14', 'label': {'fr': 'lbl_fr_14', 'en': 'lbl_en_14'}},
                                   {'relevance': 'N', 'id': '40', 'label': {'fr': 'lbl_fr_40', 'en': 'lbl_en_40'}},
                                   {'relevance': 'N', 'id': '16', 'label': {'fr': 'lbl_fr_16', 'en': 'lbl_en_16'}},
                                   {'relevance': 'N', 'id': '8', 'label': {'fr': 'lbl_fr_8', 'en': 'lbl_en_8'}},
                                   {'relevance': 'N', 'id': '9', 'label': {'fr': 'lbl_fr_9', 'en': 'lbl_en_9'}},
                                   {'relevance': 'N', 'id': '41', 'label': {'fr': 'lbl_fr_41', 'en': 'lbl_en_41'}},
                                   {'relevance': 'N', 'id': '45', 'label': {'fr': 'lbl_fr_45', 'en': 'lbl_en_45'}},
                                   {'relevance': 'H', 'id': '44', 'label': {'fr': 'lbl_fr_44', 'en': 'lbl_en_44'}},
                                   {'relevance': 'N', 'id': '18', 'label': {'fr': 'lbl_fr_18', 'en': 'lbl_en_18'}},
                                   {'relevance': 'N', 'id': '46', 'label': {'fr': 'lbl_fr_46', 'en': 'lbl_en_46'}},
                                   {'relevance': 'N', 'id': '42', 'label': {'fr': 'lbl_fr_42', 'en': 'lbl_en_42'}},
                                   {'relevance': 'N', 'id': '11', 'label': {'fr': 'lbl_fr_11', 'en': 'lbl_en_11'}},
                                   {'relevance': 'N', 'id': '1', 'label': {'fr': 'lbl_fr_1', 'en': 'lbl_en_1'}},
                                   {'relevance': 'N', 'id': '10', 'label': {'fr': 'lbl_fr_10', 'en': 'lbl_en_10'}}],
                                   'name': 'JT07.xml'},
                               {'semantic_signature': [
                                   {'relevance': 'N', 'id': '18', 'label': {'fr': 'lbl_fr_18', 'en': 'lbl_en_18'}},
                                   {'relevance': 'N', 'id': '36', 'label': {'fr': 'lbl_fr_36', 'en': 'lbl_en_36'}},
                                   {'relevance': 'N', 'id': '31', 'label': {'fr': 'lbl_fr_31', 'en': 'lbl_en_31'}},
                                   {'relevance': 'N', 'id': '26', 'label': {'fr': 'lbl_fr_26', 'en': 'lbl_en_26'}},
                                   {'relevance': 'N', 'id': '15', 'label': {'fr': 'lbl_fr_15', 'en': 'lbl_en_15'}},
                                   {'relevance': 'N', 'id': '46', 'label': {'fr': 'lbl_fr_46', 'en': 'lbl_en_46'}},
                                   {'relevance': 'N', 'id': '38', 'label': {'fr': 'lbl_fr_38', 'en': 'lbl_en_38'}},
                                   {'relevance': 'N', 'id': '27', 'label': {'fr': 'lbl_fr_27', 'en': 'lbl_en_27'}},
                                   {'relevance': 'N', 'id': '43', 'label': {'fr': 'lbl_fr_43', 'en': 'lbl_en_43'}},
                                   {'relevance': 'N', 'id': '37', 'label': {'fr': 'lbl_fr_37', 'en': 'lbl_en_37'}},
                                   {'relevance': 'N', 'id': '1', 'label': {'fr': 'lbl_fr_1', 'en': 'lbl_en_1'}},
                                   {'relevance': 'N', 'id': '47', 'label': {'fr': 'lbl_fr_47', 'en': 'lbl_en_47'}},
                                   {'relevance': 'H', 'id': '48', 'label': {'fr': 'lbl_fr_48', 'en': 'lbl_en_48'}},
                                   {'relevance': 'N', 'id': '8', 'label': {'fr': 'lbl_fr_8', 'en': 'lbl_en_8'}},
                                   {'relevance': 'H', 'id': '22', 'label': {'fr': 'lbl_fr_22', 'en': 'lbl_en_22'}}],
                                   'name': 'JT01.xml'},
                               {'semantic_signature': [
                                   {'relevance': 'N', 'id': '36', 'label': {'fr': 'lbl_fr_36', 'en': 'lbl_en_36'}},
                                   {'relevance': 'N', 'id': '28', 'label': {'fr': 'lbl_fr_28', 'en': 'lbl_en_28'}},
                                   {'relevance': 'N', 'id': '8', 'label': {'fr': 'lbl_fr_8', 'en': 'lbl_en_8'}},
                                   {'relevance': 'H', 'id': '35', 'label': {'fr': 'lbl_fr_35', 'en': 'lbl_en_35'}},
                                   {'relevance': 'N', 'id': '43', 'label': {'fr': 'lbl_fr_43', 'en': 'lbl_en_43'}},
                                   {'relevance': 'N', 'id': '37', 'label': {'fr': 'lbl_fr_37', 'en': 'lbl_en_37'}},
                                   {'relevance': 'N', 'id': '26', 'label': {'fr': 'lbl_fr_26', 'en': 'lbl_en_26'}},
                                   {'relevance': 'N', 'id': '1', 'label': {'fr': 'lbl_fr_1', 'en': 'lbl_en_1'}},
                                   {'relevance': 'N', 'id': '10', 'label': {'fr': 'lbl_fr_10', 'en': 'lbl_en_10'}},
                                   {'relevance': 'N', 'id': '33', 'label': {'fr': 'lbl_fr_33', 'en': 'lbl_en_33'}},
                                   {'relevance': 'N', 'id': '31', 'label': {'fr': 'lbl_fr_31', 'en': 'lbl_en_31'}},
                                   {'relevance': 'N', 'id': '18', 'label': {'fr': 'lbl_fr_18', 'en': 'lbl_en_18'}},
                                   {'relevance': 'N', 'id': '40', 'label': {'fr': 'lbl_fr_40', 'en': 'lbl_en_40'}},
                                   {'relevance': 'N', 'id': '14', 'label': {'fr': 'lbl_fr_14', 'en': 'lbl_en_14'}},
                                   {'relevance': 'N', 'id': '44', 'label': {'fr': 'lbl_fr_44', 'en': 'lbl_en_44'}}],
                                   'name': 'JT08.xml'},
                               {'semantic_signature': [
                                   {'relevance': 'N', 'id': '25', 'label': {'fr': 'lbl_fr_25', 'en': 'lbl_en_25'}},
                                   {'relevance': 'H', 'id': '24', 'label': {'fr': 'lbl_fr_24', 'en': 'lbl_en_24'}},
                                   {'relevance': 'N', 'id': '31', 'label': {'fr': 'lbl_fr_31', 'en': 'lbl_en_31'}},
                                   {'relevance': 'N', 'id': '27', 'label': {'fr': 'lbl_fr_27', 'en': 'lbl_en_27'}},
                                   {'relevance': 'N', 'id': '1', 'label': {'fr': 'lbl_fr_1', 'en': 'lbl_en_1'}},
                                   {'relevance': 'N', 'id': '30', 'label': {'fr': 'lbl_fr_30', 'en': 'lbl_en_30'}},
                                   {'relevance': 'H', 'id': '37', 'label': {'fr': 'lbl_fr_37', 'en': 'lbl_en_37'}},
                                   {'relevance': 'N', 'id': '9', 'label': {'fr': 'lbl_fr_9', 'en': 'lbl_en_9'}},
                                   {'relevance': 'H', 'id': '20', 'label': {'fr': 'lbl_fr_20', 'en': 'lbl_en_20'}},
                                   {'relevance': 'N', 'id': '6', 'label': {'fr': 'lbl_fr_6', 'en': 'lbl_en_6'}},
                                   {'relevance': 'N', 'id': '22', 'label': {'fr': 'lbl_fr_22', 'en': 'lbl_en_22'}},
                                   {'relevance': 'N', 'id': '42', 'label': {'fr': 'lbl_fr_42', 'en': 'lbl_en_42'}},
                                   {'relevance': 'H', 'id': '3', 'label': {'fr': 'lbl_fr_3', 'en': 'lbl_en_3'}},
                                   {'relevance': 'N', 'id': '35', 'label': {'fr': 'lbl_fr_35', 'en': 'lbl_en_35'}},
                                   {'relevance': 'H', 'id': '2', 'label': {'fr': 'lbl_fr_2', 'en': 'lbl_en_2'}}],
                                   'name': 'JT02.xml'}]}
        actual_result = self.processor.search_documents_by_topics(topic_list)
        logging.getLogger(__name__).info('test_search_documents_by_topics: %s', actual_result)
        self.assertEqual(ordered(expected_result), ordered(actual_result))

    def test_search_documents_by_topics_paginated(self):
        topic_list = ['9']
        actual_result = self.processor.search_documents_by_topics(topic_list)
        self.assertEqual(5, len(actual_result['documents']))
        actual_result = self.processor.search_documents_by_topics(topics=topic_list, hf=3, b=0)
        self.assertEqual(3, len(actual_result['documents']))
        actual_result = self.processor.search_documents_by_topics(topics=topic_list, hf=3, b=3)
        self.assertEqual(2, len(actual_result['documents']))


def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
    unittest.main()
