import os
import csv

import pdfparser.report as parsing_report
import pdfparser.text_extractor as pdfextractor

PDF_ROOT_FOLDER = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testPDF/pdfs'


def main():
    extraction_results = list()
    nb_extracted = 1
    for root, dirs, files_list in os.walk(PDF_ROOT_FOLDER):
        for pdf_file in files_list:
            if nb_extracted > 100:
                break
            print '='*40
            print 'processing file number: {nb}'.format(nb=nb_extracted)
            print '=' * 40
            if os.path.isfile(os.path.join(root, pdf_file)):
                report = parsing_report.Report()
                extractor = pdfextractor.PDFTextExtractor(report=report)
                jt = pdf_file.split('.')[0]
                print 'jt: {jt}'.format(jt=jt)
                pdf_path = os.path.join(root, pdf_file)
                print 'path: {pdf_path}'.format(pdf_path=pdf_path)
                print 'processing: {root}/{pdf_file}'.format(root=root, pdf_file=pdf_file)
                pdf_file_path = os.path.join(PDF_ROOT_FOLDER, pdf_path)
                extractor.extract_text(pdf_file_path)

                extraction_result = dict()
                for item, nb in report.__dict__.iteritems():
                    print '{nb} {item} found in pdf'.format(nb=nb, item=item)
                    extraction_result[item] = nb
                extraction_result['jt'] = jt
                extraction_result['validated'] = 0
                extraction_results.append(extraction_result)

                nb_extracted += 1

    with open('expected_results.csv', 'wb') as csv_file:
        fieldnames = ['jt', 'cover_page', 'toc', 'summary', 'glossary', 'bibliography', 'participants_list',
                      'annex', 'tables', 'validated']
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for item in extraction_results:
            writer.writerow(item)

if __name__ == '__main__':
    main()
