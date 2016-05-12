import csv
import os
import unittest

import pdfparser.report
import pdfparser.text_extractor as pdfextractor

PDF_ROOT_FOLDER = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testPDF/pdfs'


class TextExtractorTestCase(unittest.TestCase):

    def test_corpus_extraction(self):
        expected_results = load_expected_results()
        for root, dirs, files_list in os.walk(PDF_ROOT_FOLDER):
            for pdf_file in files_list:
                if os.path.isfile(os.path.join(root, pdf_file)):
                    jt = pdf_file.split('.')[0]
                    if jt not in expected_results or expected_results[jt]['validated'] != '1':
                        continue
                    else:
                        print 'Validating jt: {jt}'.format(jt=jt)
                        print 'Expected structure: {struct}'.format(struct=expected_results[jt])
                    pdf_path = os.path.join(root, pdf_file)
                    print 'path: {pdf_path}'.format(pdf_path=pdf_path)
                    print 'processing: {root}/{pdf_file}'.format(root=root, pdf_file=pdf_file)
                    report = pdfparser.report.Report()
                    extractor = pdfextractor.PDFTextExtractor(report=report)
                    pdf_text = extractor.extract_text(pdf_path)
                    self.validate_pdf_structure(expected_results[jt], report)

    def validate_pdf_structure(self, expected_structure, extract_report):
        jt = expected_structure['jt']
        print '#'*30
        print 'JT: {jt}'.format(jt=jt)
        print '#'*30
        for key in expected_structure.iterkeys():
            if key == 'jt' or key == 'validated':
                continue
            actual = extract_report.__dict__[key.lower()]
            expected = int(expected_structure[key])
            self.assertEqual(expected,
                             actual,
                             msg='JT: {jt} - {key}: Expected {expected} - Actual {actual} '.format(jt=jt,
                                                                                                   key=key,
                                                                                                   expected=expected,
                                                                                                   actual=actual))
            match = True if expected == actual else False
            print '-'*30
            print '{key}: Expected {expected} - Actual {actual} - Result: {match}'.format(key=key,
                                                                                          expected=expected,
                                                                                          actual=actual,
                                                                                          match=match)
            print '-'*30


def load_expected_results():
    expected_results = dict()
    with open('expected_results.csv', 'rb') as csv_results:
        csvreader = csv.DictReader(csv_results, delimiter=',')
        for row in csvreader:
            expected_results[row['jt']] = row
    return expected_results


if __name__ == '__main__':
    unittest.main()
