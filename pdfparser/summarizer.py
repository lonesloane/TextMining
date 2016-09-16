# -*- coding: utf8 -*-
import os
from nltk import PunktSentenceTokenizer

from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
# from sumy.summarizers.text_rank import TextRankSummarizer as Summarizer
from sumy.summarizers.lsa import LsaSummarizer as Summarizer
from sumy.utils import get_stop_words

from pdfparser import logger, _config
import indexfiles.loader as loader


PROJECT_FOLDER = _config.get('MAIN', 'project_folder')
PDF_ROOT_FOLDER = os.path.join(PROJECT_FOLDER, 'pdfs')
LANGUAGE = "english"  # TODO: identify pdf language
# TODO: make parameter based on length of submitted text
SENTENCES_COUNT = _config.getfloat('MAIN', 'SENTENCES_COUNT')


class PDFSummarizer:

    def __init__(self, semantic=False):
        if semantic:
            self.file_index, self.topic_index = load_indexes()

    def generate_summary(self, pdf_sentences):
        pdf_string = '\n'.join([sentence.encode('utf-8') for sentence in pdf_sentences])
        parser = PlaintextParser.from_string(pdf_string, Tokenizer(LANGUAGE))
        stemmer = Stemmer(LANGUAGE)

        summarizer = Summarizer(stemmer)
        summarizer.stop_words = get_stop_words(LANGUAGE)

        summary = summarizer(parser.document, SENTENCES_COUNT)
        summary = remove_repetition(summary)
        return summary


def remove_repetition(summary):
    results = set(summary)
    return results


def load_indexes():
    files_index_filename = os.path.join(PROJECT_FOLDER, 'output/Files_Index')
    file_index = loader.FilesIndex(files_index_filename)
    topics_index_filename = os.path.join(PROJECT_FOLDER, 'output/Topics_Index')
    topic_index = loader.TopicsIndex(topics_index_filename)
    return file_index, topic_index


def extract_sentences(pdf_text):
    pdf_sentences = PunktSentenceTokenizer().tokenize(pdf_text)
    return pdf_sentences


'''
def extract_relevant_sentences(pdf_sentences, topics):
    logger.info("-"*40)
    logger.info("Extracting relevant sentences")
    logger.info("-"*40)
    relevant_sentences = []
    # idx = 0
    for idx, sentence in enumerate(pdf_sentences):
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
        # idx += 1
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
'''

if __name__ == '__main__':
    pass
