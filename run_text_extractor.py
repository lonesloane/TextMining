#!local_py_env/bin/python2.7
import os
import re

import sys

import pdfparser.report
import pdfparser.text_extractor as text_extractor

PDF_ROOT_FOLDER = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testPDF/pdfs'


def main():

    file_name = raw_input('File name: (press enter to exit) ')
    page_number = raw_input('Single page number: (press enter to ignore) ')
    mode = input('Extraction mode: (1: LAYOUT | 2: TEXT) ')
    format = input('Output format: (1: JSON | 2: XML | 3: Text) ')

    extract_mode = text_extractor.ExtractMode.LAYOUT
    if mode:
        if mode == 1:
            extract_mode = text_extractor.ExtractMode.LAYOUT
        elif mode == 2:
            extract_mode = text_extractor.ExtractMode.TEXT
        else:
            print 'incorrect value for mode {v}. Using LAYOUT as default'.format(v=mode)

    output_format = text_extractor.OutputFormat.JSON
    if format:
        if format == 1:
            output_format = text_extractor.OutputFormat.JSON
        elif format == 2:
            output_format = text_extractor.OutputFormat.XML
        elif format == 3:
            output_format = text_extractor.OutputFormat.TEXT
        else:
            print 'incorrect value for format {v}. Using JSON as default'.format(v=format)

    if page_number:
        pdfparser._log_level = 2

    report = pdfparser.report.Report()
    extractor = text_extractor.PDFTextExtractor(report=report, single_page=page_number)
    for root, dirs, files_list in os.walk(PDF_ROOT_FOLDER):
        for pdf_file in files_list:
            if os.path.isfile(os.path.join(root, pdf_file)):
                if re.findall('\.summary$', pdf_file, re.IGNORECASE):
                    continue
                if re.findall('\.json$', pdf_file, re.IGNORECASE):
                    continue
                jt = pdf_file.split('.')[0]
                if jt != file_name:
                    continue
                print 'File {jt} found.'.format(jt=jt)
                pdf_path = os.path.join(root, pdf_file)
                print 'Path: {pdf_path}'.format(pdf_path=pdf_path)
                print 'Processing: {root}/{pdf_file}'.format(root=root, pdf_file=pdf_file)
                extract_text(extractor, pdf_path, mode=extract_mode, format=output_format)

    for item, nb in report.__dict__.iteritems():
        print '{nb} {item} found in pdf'.format(nb=nb, item=item)
    # extract_sentences(pdf_text)

    return 0


def extract_text(extractor, pdf_long_filename, mode, format):
    pdf_file_path = os.path.join(PDF_ROOT_FOLDER, pdf_long_filename)
    pdf_text = extractor.extract_text(pdf_file_path, mode=mode, format=format)

    with open('pdf_text.json', 'wb') as json_file:
        json_file.write(pdf_text)
    print("\n" + "*" * 40)
    print("PDF TEXT EXTRACTED SUCCESSFULLY")
    print("*" * 40 + "\n")


def extract_sentences(pdf_text):
    # TODO: take only text section from json!!!
    pdf_sentences = text_extractor.extract_sentences(pdf_text)
    print("\n" + "*" * 40 + "\n")
    print("EXTRACTED SENTENCES:\n")
    print("*" * 40 + "\n")
    isentence = 0
    for isentence, sentence in enumerate(pdf_sentences):
        #isentence += 1
        sentence = sentence.strip()
        print("\n[sentence {isentence}]:\n{sentence}".format(isentence=isentence,
                                                             sentence=sentence.encode('utf-8')))
    print("*" * 40 + "\n")


if __name__ == '__main__':
    sys.exit(main())


