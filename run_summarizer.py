#!local_py_env/bin/python2.7
import re
import sys
import os

from json.decoder import JSONDecoder

import pdfparser
import pdfparser.summarizer as pdfsummarizer
import pdfparser.text_extractor as text_extractor

PDF_ROOT_FOLDER = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testPDF/pdfs' # TODO: config file


def main():
    file_name = raw_input("File name: (press enter to exit)")
    if not file_name or len(file_name) == 0:
        return

    pdf_path = None
    pdf_file = None
    jt = None
    # find pdf on file system
    for root, dirs, files_list in os.walk(PDF_ROOT_FOLDER):
        if 'Summaries' in root.split('/'):
            continue
        if jt:
            break
        for pdf_file in files_list:
            if os.path.isfile(os.path.join(root, pdf_file)):
                jt = pdf_file.split('.')[0]
                if jt != file_name:
                    jt = None
                    continue
                else:
                    pdf_path = os.path.join(root, pdf_file)
                    break

    print 'pdf_path: ' + pdf_path
    print 'filename: ' + file_name
    print 'pdf: ' + pdf_file
    print 'jt: ' + jt

    if not pdf_path or not jt:
        print ('File {f} not found'.format(f=file_name))
        return

    with open(PDF_ROOT_FOLDER + '/Summaries/' + jt + '.pdf.summary', mode='wb') as out_file:
        print 'File {jt} found.\n'.format(jt=file_name)
        print 'Path: {pdf_path}\n'.format(pdf_path=pdf_path)

        json_pdf_text = generate_summary(out_file, pdf_path)

        print_pdf_summary(json_pdf_text, out_file)

        return


def print_pdf_summary(json_pdf_text, out_file):
    # If 'Summary' or 'Table of Content' found in pdf
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


def get_summary_or_toc(json_content):
    decoder = JSONDecoder()
    json_pdf = decoder.decode(json_content)
    pdf_txt = ''
    key = None

    if text_extractor.FragmentType.SUMMARY in json_pdf.keys():
        key = text_extractor.FragmentType.SUMMARY
    elif text_extractor.FragmentType.TABLE_OF_CONTENTS in json_pdf.keys():
        key = text_extractor.FragmentType.TABLE_OF_CONTENTS

    if key:
        for frag in json_pdf[key]:
            pdf_txt += frag + '\n'

    return pdf_txt


def get_text_from_json(json_content):
    ptrn_punct = '[.!?]'
    decoder = JSONDecoder()
    json_pdf = decoder.decode(json_content)
    pdf_txt = ''

    if text_extractor.FragmentType.SUMMARY in json_pdf.keys():
        for frag in json_pdf[text_extractor.FragmentType.SUMMARY]:
            pdf_txt += add_text(frag, pdf_txt, ptrn_punct)

    if text_extractor.FragmentType.TEXT in json_pdf.keys():
        for frag in json_pdf[text_extractor.FragmentType.TEXT]:
            pdf_txt += add_text(frag, pdf_txt, ptrn_punct)

    return pdf_txt


def add_text(frag, pdf_txt, ptrn_punct):
    frag = frag.strip()
    if not re.match(ptrn_punct, frag[-1]):
        frag += '.'
    frag +=  '\n'
    return frag


def extract_text(extractor, pdf_long_filename, extract_mode):
    pdf_file_path = os.path.join(PDF_ROOT_FOLDER, pdf_long_filename)
    pdf_text = extractor.extract_text(pdf_file_path, mode=extract_mode)
    return pdf_text


def extract_sentences(pdf_text):
    pdf_sentences = pdfparser.summarizer.extract_sentences(pdf_text)
    for sentence in pdf_sentences:
        sentence = sentence.strip()
    return pdf_sentences


if __name__ == '__main__':
    sys.exit(main())
