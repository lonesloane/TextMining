import logging
import os

import pdfparser.text_extractor as pdfextractor

PDF_ROOT_FOLDER = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testPDF/pdfs'


def logging_setup():
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
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

    # file_name = raw_input("File name: (press enter to exit)")

    # Parse pdf content
    extractor = pdfextractor.PDFTextExtractor()
    # pdf_long_filename = '2014/11/07/'+file_name+'.pdf'
    pdf_long_filename = '2014/11/07/JT03365818.pdf'
    pdf_file_path = os.path.join(PDF_ROOT_FOLDER, pdf_long_filename)
    pdf_text = extractor.extract_text(pdf_file_path)

    pdf_sentences = extractor.extract_sentences(pdf_text)
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


if __name__ == '__main__':
    main()
