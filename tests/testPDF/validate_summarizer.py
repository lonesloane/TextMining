import os
import logging
from json.decoder import JSONDecoder

import sys

import pdfparser
import pdfparser.summarizer as pdfsummarizer
import pdfparser.text_extractor as text_extractor
#from pdfparser.text_extractor import ExtractMode

PDF_ROOT_FOLDER = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testPDF/pdfs'
LOG_LEVEL = logging.DEBUG
_log_level = 3  # verbosity of log. 1:normal - 2:verbose - 3:visual


def main():
    file_name = raw_input("File name: (press enter to exit)")
    if not file_name or len(file_name) == 0:
        return

    pdf_path = None
    jt = None
    # find pdf on file system
    for root, dirs, files_list in os.walk(PDF_ROOT_FOLDER):
        if 'Summaries' in root.split('/'):
            continue
        if jt: break
        for pdf_file in files_list:
            if os.path.isfile(os.path.join(root, pdf_file)):
                jt = pdf_file.split('.')[0]
                if jt != file_name:
                    jt = None
                    continue
                else:
                    pdf_path = os.path.join(root, pdf_file)
                    break

    print 'pdf_path: '+pdf_path
    print 'filename: '+file_name
    print 'pdf: '+pdf_file
    print 'jt: '+jt

    if not pdf_path or not jt:
        print ('File {f} not found'.format(f=file_name))
        return

    with open(PDF_ROOT_FOLDER + '/Summaries/' + jt + '.pdf.summary', mode='wb') as out_file:
        out_file.write('File {jt} found.\n'.format(jt=file_name))
        out_file.write('Path: {pdf_path}\n'.format(pdf_path=pdf_path))

        generate_raw_summary(out_file, pdf_path)

        json_pdf_text = generate_summary(out_file, pdf_path)

        print_pdf_summary(json_pdf_text, out_file)

        return

        '''
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
        '''


def print_pdf_summary(json_pdf_text, out_file):
    # If the pdf does indeed contain a summary
    pdf_summary = get_summary_or_toc(json_pdf_text)
    if pdf_summary and len(pdf_summary) > 0:
        out_file.write("*" * 40 + "\n")
        out_file.write('\nSummary found in pdf\n')
        out_file.write("*" * 40 + "\n")
        out_file.write(pdf_summary.encode('utf-8'))


def generate_summary(out_file, pdf_path):
    # Extract 'JSON based' summary
    extract_mode = text_extractor.ExtractMode.LAYOUT
    extractor = text_extractor.PDFTextExtractor()
    json_pdf_text = extract_text(extractor, pdf_path, extract_mode)
    pdf_txt = get_text_from_json(json_pdf_text)
    out_file.write("*" * 40 + "\n")
    out_file.write("JSON based summary:\n")
    out_file.write("*" * 40 + "\n")
    sentences = extract_sentences(pdf_txt)
    summarizer = pdfsummarizer.PDFSummarizer()
    results = summarizer.generate_summary(sentences)
    for sentence in results:
        out_file.write(sentence._text.encode('utf-8') + '\n')
    out_file.write("*" * 40 + "\n")
    return json_pdf_text


def generate_raw_summary(out_file, pdf_path):
    # Extract 'Raw' summary
    extract_mode = text_extractor.ExtractMode.TEXT
    extractor = text_extractor.PDFTextExtractor()
    raw_json_pdf_text = extract_text(extractor, pdf_path, extract_mode)
    raw_pdf_text = get_text_from_json(raw_json_pdf_text)
    out_file.write("*" * 40 + "\n")
    out_file.write("Raw text summary:\n")
    out_file.write("*" * 40 + "\n")
    sentences = extract_sentences(raw_pdf_text)
    summarizer = pdfsummarizer.PDFSummarizer()
    results = summarizer.generate_summary(sentences)
    for sentence in results:
        out_file.write(sentence._text.encode('utf-8') + '\n')
    out_file.write("*" * 40 + "\n")


def get_summary_or_toc(json_content):
    decoder = JSONDecoder()
    json_pdf = decoder.decode(json_content)
    pdf_txt = ''
    key = None

    if 'Summary' in json_pdf.keys():
        key = 'Summary'
    elif 'Toc' in json_pdf.keys():
        key = 'Toc'

    if key:
        for frag in json_pdf[key]:
            pdf_txt += frag + '\n'

    return pdf_txt


def get_text_from_json(json_content):
    decoder = JSONDecoder()
    json_pdf = decoder.decode(json_content)
    print("\n" + "*" * 40 + "\n")
    print("EXTRACTED PDF TEXT:\n")
    print("*" * 40 + "\n")
    pdf_txt = ''

    if 'Summary' in json_pdf.keys():
        for frag in json_pdf['Text']:
            pdf_txt += frag + '\n'

    if 'Text' in json_pdf.keys():
        for frag in json_pdf['Text']:
            pdf_txt += frag + '\n'
    return pdf_txt


def extract_text(extractor, pdf_long_filename, extract_mode):
    pdf_file_path = os.path.join(PDF_ROOT_FOLDER, pdf_long_filename)
    pdf_text = extractor.extract_text(pdf_file_path, mode=extract_mode)
    return pdf_text


def extract_sentences(pdf_text):
    pdf_sentences = pdfparser.summarizer.extract_sentences(pdf_text)
    print("\n" + "*" * 40 + "\n")
    print("EXTRACTED SENTENCES:\n")
    print("*" * 40 + "\n")
    for sentence in pdf_sentences:
        sentence = sentence.strip()
    print("*" * 40 + "\n")
    return pdf_sentences


if __name__ == '__main__':
    sys.exit(main())
