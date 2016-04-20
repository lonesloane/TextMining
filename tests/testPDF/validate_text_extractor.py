import logging
import os

import pdfparser.text_extractor as pdfextractor
from pdfparser import logger

PDF_ROOT_FOLDER = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testPDF/pdfs'


def main():

    # file_name = raw_input("File name: (press enter to exit)")

    # Parse pdf content
    extractor = pdfextractor.PDFTextExtractor()
    # pdf_long_filename = '2014/11/07/'+file_name+'.pdf'
    pdf_long_filename = '2014/11/02/JT03365425.pdf'
    pdf_file_path = os.path.join(PDF_ROOT_FOLDER, pdf_long_filename)
    pdf_text = extractor.extract_text(pdf_file_path)
    logger.debug("\n"+"*"*40+"\n")
    logger.debug("EXTRACTED PDF TEXT:\n")
    logger.debug("*"*40+"\n")
    logger.debug(pdf_text)
    logger.debug("*"*40+"\n")
    return
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
