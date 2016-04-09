import os
import logging

import pdfparser.summarizer as pdfsummarizer
import pdfparser.text_extractor as text_extractor

PDF_ROOT_FOLDER = '/home/stephane/Playground/PycharmProjects/TextMining/pdfs'
LOG_LEVEL = logging.DEBUG
_log_level = 3  # verbosity of log. 1:normal - 2:verbose - 3:visual


def main():

    summarizer = pdfsummarizer.PDFSummarizer()

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
        n_s = 0
        for sentence in pdf_sentences:
            n_s += 1
            sentence = sentence.strip()
            logger.debug("\n[sentence {isentence}]:\n{sentence}".format(isentence=n_s,
                                                                        sentence=sentence.encode('utf-8')))
        logger.debug("*"*40+"\n")

        # Extract 'default' summary
        logger.debug("*"*40+"\n")
        logger.info("Raw summary:")
        logger.debug("*"*40+"\n")
        summarizer.generate_summary(pdf_sentences)

        # INTERRUPT EXECUTION FOR DEBUG PURPOSES
        continue  # <== Un-comment to exit early
        # INTERRUPT EXECUTION FOR DEBUG PURPOSES

        # retrieve semantic enrichment result for given file
        enrichment_file = file_name+'.xml'
        topics = get_topics_for_file(enrichment_file, file_index, topic_index)
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

if __name__ == '__main__':
    logger = logging_setup()
    main()
