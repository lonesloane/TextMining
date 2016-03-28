# -*- coding: utf8 -*-
import logging
import os
from cStringIO import StringIO

from nltk import PunktSentenceTokenizer
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from sumy.nlp.stemmers import Stemmer
from sumy.nlp.tokenizers import Tokenizer
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.text_rank import TextRankSummarizer as Summarizer
from sumy.utils import get_stop_words

import indexfiles.loader as loader
from pdfparser.pdf_page_filter import PDFPageFilter

PROJECT_FOLDER = os.path.abspath('/home/stephane/Playground/PycharmProjects/TextMining')
PDF_ROOT_FOLDER = os.path.join(PROJECT_FOLDER, 'pdfs')

LOG_LEVEL = logging.DEBUG
LANGUAGE = "english"
SENTENCES_COUNT = 10


def convert_pdf_to_txt(path):
    rsrcmgr = PDFResourceManager()
    codec = 'utf-8'
    laparams = LAParams()
    fp = file(path, 'rb')
    password = ""
    maxpages = 0
    caching = True
    pagenos = set()
    pdf_txt = ''
    page_no = 0
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,
                                  caching=caching, check_extractable=True):
        retstr = StringIO()
        page_no += 1

        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
        PDFPageInterpreter(rsrcmgr, device).process_page(page)

        page_txt = retstr.getvalue()
        device.close()
        retstr.close()

        validated_txt, _continue = validate(page_txt)
        if not _continue:
            break

        if len(validated_txt) > 0:
            logger.info("-"*40)
            logger.info("page {page_no} processed".format(page_no=page_no))
            logger.debug("Page content: %s", validated_txt)
            logger.info("-"*40)

        pdf_txt += '\n'+validated_txt

    fp.close()
    return pdf_txt


def validate(page_txt):
    if PDFPageFilter.is_cover(page_txt):
        logger.info('\n{Cover Page} found. Page ignored.')
        return '', True
    elif PDFPageFilter.is_toc(page_txt):
        logger.info('\n{Table Of Contents} found. Page ignored.')
        return '', True
    elif PDFPageFilter.is_list_of_abbreviations(page_txt):
        logger.info('\n{List of abbreviations} found. Page ignored.')
        return '', True
    elif PDFPageFilter.is_bibliography(page_txt):
        logger.info('\n{Bibliography} found. Remaining pages ignored.')
        return '', False
    elif PDFPageFilter.is_participants_list(page_txt):
        logger.info('\n{Participants List} found. Remaining pages ignored.')
        return '', False
    elif PDFPageFilter.is_annex(page_txt):
        logger.info('\n{Annex} found. Remaining pages ignored.')
        return '', False
    elif PDFPageFilter.contains_table(page_txt):
        logger.info('\n{Table} found. Page ignored.')
        return '', True

    return page_txt, True


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


def extract_sentences(pdf_long_filename):
    pdf_file = os.path.join(PDF_ROOT_FOLDER, pdf_long_filename)
    pdf_string = convert_pdf_to_txt(pdf_file)
    pdf_sentences = PunktSentenceTokenizer().tokenize(pdf_string.decode('utf-8'))
    return pdf_sentences


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


def generate_summary(pdf_sentences):
    # pdf_string = '\n'.join([sentence.encode('utf-8') for sentence in pdf_sentences])
    parser = PlaintextParser.from_string(pdf_sentences, Tokenizer(LANGUAGE))
    stemmer = Stemmer(LANGUAGE)

    summarizer = Summarizer(stemmer)
    # summarizer.bonus_words = frozenset([''])
    # summarizer.stigma_words = frozenset([''])
    # summarizer.null_words = frozenset([''])
    # summarizer.bonus_words = frozenset([''])
    # summarizer.stigma_words = frozenset([''])
    # summarizer.null_words = frozenset([''])
    summarizer.stop_words = get_stop_words(LANGUAGE)

    for sentence in summarizer(parser.document, SENTENCES_COUNT):
        logger.info(sentence._text.encode('utf-8'))
    logger.info("*"*40+"\n")


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

    # Get semantic enrichment indexes
    file_index, topic_index = load_indexes()

    while True:
        file_name = raw_input("File name: (press enter to exit)")
        if not file_name or len(file_name) == 0:
            break
        # retrieve semantic enrichment result for given file
        enrichment_file = file_name+'.xml'
        topics = get_topics_for_file(enrichment_file, file_index, topic_index)

        # Parse pdf content
        logger.info("Parsing PDF content\n")
        pdf_long_filename = '2014/11/07/'+file_name+'.pdf'
        pdf_sentences = extract_sentences(pdf_long_filename)
        logger.debug("*"*40+"\n")
        for sentence in pdf_sentences:
            logger.debug(sentence)
        logger.debug("*"*40+"\n")

        # Extract 'default' summary
        logger.debug("*"*40+"\n")
        logger.info("Raw summary:")
        logger.debug("*"*40+"\n")
        generate_summary(pdf_sentences)
        # continue  # <== Comment out to exit early
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
    logger = logging_setup()
    main()
