#!/usr/bin/python2.7
import ConfigParser
import logging
import os

import sys
from flask import Flask, jsonify, abort, request

import index.loader
import search.semantic_query as semantic
import search.proximity_finder as proximity

# Get configuration parameters
basedir = os.path.abspath(os.path.dirname(__file__))
config = ConfigParser.SafeConfigParser()
# config.read(os.path.join(basedir, 'rest_api.conf'))
config.read(os.path.join(basedir, 'rest_api_test.conf'))

# Set appropriate logging level
numeric_level = getattr(logging, config.get('LOGGING', 'level').upper(), None)
if not isinstance(numeric_level, int):
    raise ValueError('Invalid log level: %s' % config.get('LOGGING', 'level'))
logging.basicConfig(level=numeric_level, format='%(name)s - %(levelname)s - %(message)s')

# Load all various indexes used throughout the application
index_folder = config.get('INDEX', 'index_dir')
files_index_filename = config.get('INDEX', 'files_index_filename')
files_dates_index_filename = config.get('INDEX', 'files_dates_index_filename')
topics_index_filename = config.get('INDEX', 'topics_index_filename')
topics_occurrences_index_filename = config.get('INDEX', 'topics_occurrences_index_filename')
topics_labels_index_filename = config.get('INDEX', 'topics_labels_index_filename')
typeahead_index_filename = config.get('INDEX', 'typeahead_index_filename')

files_index = index.loader.FilesIndex(os.path.join(index_folder, files_index_filename))
# files_dates_index = index.loader.FilesDatesIndex(os.path.join(index_folder, files_dates_index_filename))
topics_index = index.loader.TopicsIndex(os.path.join(index_folder, topics_index_filename))
typeahead_index = index.loader.TopicsTypeAheadIndex(os.path.join(index_folder, typeahead_index_filename)).index
typeahead_index_full = typeahead_index  # keep this version since the typeahead index is dynamically re-calculated
topics_occurrences_index = index.loader.TopicsOccurrencesIndex(os.path.join(index_folder,
                                                                            topics_occurrences_index_filename))
topics_labels_index = index.loader.TopicsLabelsIndex(os.path.join(index_folder, topics_labels_index_filename))

# Initialize the main business components
query_processor = semantic.QueryProcessor(files_index=files_index,
                                          topics_occurrences_index=topics_occurrences_index,
                                          topics_labels_index=topics_labels_index,
                                          topics_index=topics_index)
proximity_finder = proximity.ProximityFinder(topics_index=topics_index,
                                             topics_occurrences_index=topics_occurrences_index,
                                             files_index=files_index)

app = Flask(__name__, static_url_path='', static_folder=config.get('INDEX', 'static_folder'))


@app.route('/')
def root():
    """
    Serve root HTML file for single page application
    :return:
    """
    return app.send_static_file('index.html')


@app.route('/topics')
def get_full_list_topics():
    """
    Serve the 'index' file with all topics labels used to build the typeahead index
    :return:
    """
    return app.send_static_file('topics.json')


# noinspection PyBroadException
@app.route('/semantic-search/api/1.0/topic/<topic_label>', methods=['GET'])
def get_list_topics(topic_label):
    """

    :param topic_label:
    :return:
    """
    logging.info('Looking for topic %s', topic_label)
    try:
        topic = topics_labels_index.index[topic_label]
        return jsonify({'topic': topic})
    except:
        abort(404)


# noinspection PyBroadException
@app.route('/semantic-search/api/1.0/documents/<topic_id_list>', methods=['GET'])
def get_documents(topic_id_list):
    """

    :param topic_id_list:
    :return:
    """
    logging.info('Looking for documents matching topic: %s', topic_id_list)
    if '[' in topic_id_list and ']' in topic_id_list:
        try:
            topics = topic_id_list[1:-1].split(',')
            logging.info("topics: " + " ".join(topics))
            return jsonify({'search_results': query_processor.search_documents_by_topics(topics,
                                                                                         order_by_relevance=True,
                                                                                         hf=20)})
        except TypeError as e:
            logging.error("query_processor.execute failed: %s", e.message)
            abort(404)
        except:
            logging.error("query_processor.execute failed: %s", sys.exc_info()[0])
            abort(404)
    else:
        logging.error("Invalid topics list: " + topic_id_list)
        abort(404)


@app.route('/semantic-search/api/1.0/documents/topic/label/<topic_label>', methods=['GET'])
def get_documents_for_topic_label(topic_label):
    """

    :param topic_label:
    :return:
    """
    logging.info('Looking for documents matching topic: %s', topic_label)
    if '[' in topic_label and ']' in topic_label:
        topic_label = topic_label[1:-1]  # discard '[' and ']' if present
    topic_id = topics_labels_index.get_topic_id_for_label(target_topic=topic_label)
    if topic_id is not None:
        try:
            return jsonify({'search_results': query_processor.search_documents_by_topics([topic_id],
                                                                                         order_by_relevance=True,
                                                                                         hf=20)})
        except TypeError as e:
            logging.error("query_processor.execute failed: %s", e.message)
            abort(404)
        except:
            logging.error("query_processor.execute failed: %s", sys.exc_info()[0])
            abort(404)
    else:
        logging.error("Invalid topics list: " + topic_label)
        abort(404)


@app.route('/semantic-search/api/1.0/document-details', methods=['POST'])
def get_document_details():
    """

    :return:
    """
    if not request.json or 'documentId' not in request.json:
        abort(400)
    logging.info('get_document_details for: ' + request.json['documentId'])
    document_id = request.json['documentId']
    enrichment_result = query_processor.get_enrichment_for_files(target_file=document_id)
    semantic_signature = query_processor.build_semantic_signature(enrichment_result=enrichment_result)
    proximity_results = proximity_finder.build_proximity_results(semantic_signature=enrichment_result,
                                                                 sort_criteria=proximity.SortBy.PROXIMITY_SCORE,
                                                                 ignored_files=[document_id],
                                                                 hf=20).proximity_results
    proximity_results = proximity.jsonify(proximity_results)
    return jsonify({'details': {'semantic_signature': semantic_signature,
                                'proximity_results': proximity_results}})


if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get("PORT", 3000)))
