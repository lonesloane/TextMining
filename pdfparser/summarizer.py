# -*- coding: utf8 -*-
import ConfigParser
import logging
import os

from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.text_rank import TextRankSummarizer as Summarizer
from sumy.utils import get_stop_words

import indexfiles.loader as loader
import text_extractor


# Get configuration parameters
basedir = os.path.abspath(os.path.dirname(__file__))
config = ConfigParser.SafeConfigParser()
config.read(os.path.join(basedir, 'pdfparser.conf'))

PROJECT_FOLDER = config.get('MAIN', 'project_folder')
PDF_ROOT_FOLDER = os.path.join(PROJECT_FOLDER, 'pdfs')
LANGUAGE = "english"
SENTENCES_COUNT = 10
# Logging
LOG_LEVEL = logging.DEBUG
_log_level = 3  # verbosity of log. 1:normal - 2:verbose - 3:visual


class PDFSummarizer:

    def __init__(self, semantic=False):
        if semantic:
            self.file_index, self.topic_index = load_indexes()
        self.logger = logging_setup()

    def generate_summary(self, pdf_sentences):
        pdf_string = '\n'.join([sentence.encode('utf-8') for sentence in pdf_sentences])
        parser = PlaintextParser.from_string(pdf_string, Tokenizer(LANGUAGE))
        stemmer = Stemmer(LANGUAGE)

        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(LANGUAGE)

        for sentence in summarizer(parser.document, SENTENCES_COUNT):
            self.logger.info(sentence._text.encode('utf-8'))
        self.logger.info("*"*40+"\n")


def extract_relevant_sentences(pdf_sentences, topics):
    logger.info("-"*40)
    logger.info("Extracting relevant sentences")
    logger.info("-"*40)
    relevant_sentences = []
    idx = 0
    for sentence in pdf_sentences:
        logger.info("."*40+"\n")
        logger.info('Sentence {idx}: {sentence}\n'.format(idx=idx, sentence=sentence.encode('utf-8')))
        match = False
        score = 0
        for label in topics.keys():
            if label in sentence:
                relevance = topics[label]
                score += get_score(relevance)
                logger.debug("Found: [{label}] - relevance: [{relevance}]".format(label=label,
                                                                                  relevance=relevance))
                match = True
        if match:
            logger.debug("{idx} - Score: {score} - {sentence}\n".format(idx=idx,
                                                                        score=score,
                                                                        sentence=sentence.encode('utf-8')))
            relevant_sentences.append((idx, sentence, score))
        else:
            logger.debug('\nNo match...')
        logger.info("."*40+"\n")
        idx += 1
        relevant_sentences = sorted(relevant_sentences, key=lambda item: int(item[0]))
    logger.info("*"*40+"\n")
    return relevant_sentences


def get_topics_for_file(enrichment_file, file_index, topic_index):
    enrichment = file_index.get_enrichment_for_files(enrichment_file)
    topics = {}
    for topic_id, relevance in enrichment:
        topic_labels = topic_index.get_labels_for_topic_id(topic_id)
        logger.info("Topic: {topic} - Relevance: {relevance}".format(topic=topic_labels[0],
                                                                     relevance=relevance))
        topics[topic_labels[0]] = relevance
    logger.info("*"*40+"\n")
    return topics


def load_indexes():
    files_index_filename = os.path.join(PROJECT_FOLDER, 'output/Files_Index')
    file_index = loader.FilesIndex(files_index_filename)
    topics_index_filename = os.path.join(PROJECT_FOLDER, 'output/Topics_Index')
    topic_index = loader.TopicsIndex(topics_index_filename)
    return file_index, topic_index


def get_score(relevance):
    if relevance == 'N':
        return 1
    if relevance == 'H':
        return 10


def report(relevant_sentences):
    _report = {}
    for elem in relevant_sentences:
        score = elem[2]
        if score in _report:
            _report[score] += 1
        else:
            _report[score] = 1

    for score, nb in _report.iteritems():
        logger.info("Score %s - Nb occurrences: %s", score, nb)
    logger.info("-"*40)


def logging_setup():
    logging.basicConfig(level=LOG_LEVEL, format='%(message)s')
    _logger = logging.getLogger('summarizer')
    # create file handler which logs even debug messages
    fh = logging.FileHandler('summarizer.log', mode='w')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    _logger.addHandler(fh)
    _logger.addHandler(ch)

    return _logger


def main():
    logger = logging_setup()

    while True:
        file_name = raw_input("File name: (press enter to exit)")
        if not file_name or len(file_name) == 0:
            break

        # Parse pdf content
        extractor = text_extractor.PDFTextExtractor()
        if _log_level > 2:
            logger.info("Parsing PDF content\n")
        # pdf_long_filename = '2014/11/07/'+file_name+'.pdf'
        pdf_long_filename = '2014/11/07/JT03365818.pdf'
        pdf_file_path = os.path.join(PDF_ROOT_FOLDER, pdf_long_filename)
        pdf_sentences = extractor.extract_sentences(pdf_file_path)

        logger.debug("\n"+"*"*40+"\n")
        logger.debug("EXTRACTED PDF TEXT:\n")
        logger.debug("*"*40+"\n")
        isentence = 0
        for sentence in pdf_sentences:
            isentence += 1
            sentence = sentence.strip()
            logger.debug("\n[sentence {isentence}]:\n{sentence}".format(isentence=isentence,
                                                                      sentence=sentence.encode('utf-8')))
        logger.debug("*"*40+"\n")

        # Extract 'default' summary
        logger.debug("*"*40+"\n")
        logger.info("Raw summary:")
        logger.debug("*"*40+"\n")
        generate_summary(pdf_sentences)

        # INTERRUPT EXECUTION FOR DEBUG PURPOSES
        continue  # <== Un-comment to exit early
        # INTERRUPT EXECUTION FOR DEBUG PURPOSES

        # retrieve semantic enrichment result for given file
        enrichment_file = file_name+'.xml'
        # topics = get_topics_for_file(enrichment_file, file_index, topic_index)
        # Identify 'most relevant sentences'
        relevant_sentences = extract_relevant_sentences(pdf_sentences, topics)
        report(relevant_sentences)

        # Extract 'semantically oriented' summary
        logger.debug("*"*40+"\n")
        logger.info("Semantic based summary:\n")
        logger.debug("*"*40+"\n")
        # TODO: add logic to figure out optimal score threshold
        pdf_string = "\n".join([s for _, s, score in relevant_sentences if score > 0])
        generate_summary(pdf_string)

if __name__ == '__main__':
    main()
