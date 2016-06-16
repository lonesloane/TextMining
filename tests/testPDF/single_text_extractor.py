import os

import pdfparser.report
import pdfparser.text_extractor as text_extractor

PDF_ROOT_FOLDER = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testPDF/pdfs'


def main():

    report = pdfparser.report.Report()
    file_name = raw_input('File name: (press enter to exit)')
    page_number = raw_input('Single page number: (press enter to ignore)')
    if page_number:
        pdfparser._log_level = 2

    extractor = text_extractor.PDFTextExtractor(report, page_number)
    for root, dirs, files_list in os.walk(PDF_ROOT_FOLDER):
        for pdf_file in files_list:
            if os.path.isfile(os.path.join(root, pdf_file)):
                jt = pdf_file.split('.')[0]
                if jt != file_name:
                    continue
                print 'File {jt} found.'.format(jt=jt)
                pdf_path = os.path.join(root, pdf_file)
                print 'Path: {pdf_path}'.format(pdf_path=pdf_path)
                print 'Processing: {root}/{pdf_file}'.format(root=root, pdf_file=pdf_file)
                pdf_text = extract_text(extractor, pdf_path)

    for item, nb in report.__dict__.iteritems():
        print '{nb} {item} found in pdf'.format(nb=nb, item=item)
    # extract_sentences(pdf_text)


def extract_text(extractor, pdf_long_filename):
    pdf_file_path = os.path.join(PDF_ROOT_FOLDER, pdf_long_filename)
    pdf_text = extractor.extract_text(pdf_file_path)
    with open('pdf_text.json', 'wb') as json_file:
        json_file.write(pdf_text)
    print("\n" + "*" * 40)
    print("PDF TEXT EXTRACTED SUCCESSFULLY")
    print("*" * 40 + "\n")
    return pdf_text


def extract_sentences(pdf_text):
    # TODO: take only text section from json!!!
    pdf_sentences = text_extractor.extract_sentences(pdf_text)
    print("\n" + "*" * 40 + "\n")
    print("EXTRACTED SENTENCES:\n")
    print("*" * 40 + "\n")
    isentence = 0
    for sentence in pdf_sentences:
        isentence += 1
        sentence = sentence.strip()
        print("\n[sentence {isentence}]:\n{sentence}".format(isentence=isentence,
                                                             sentence=sentence.encode('utf-8')))
    print("*" * 40 + "\n")


if __name__ == '__main__':
    main()


