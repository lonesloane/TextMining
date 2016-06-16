import csv
import os
import unittest

import pdfparser.report
import pdfparser.text_extractor as pdfextractor

TEST_ROOT_FOLDER = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testPDF/'
PDF_ROOT_FOLDER = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testPDF/pdfs'


class TextExtractorTestCase(unittest.TestCase):

    def test_corpus_extraction(self):
        expected_results = load_expected_results()
        with open(os.path.join(TEST_ROOT_FOLDER, 'test_results.txt'), 'wb') as test_results:
            for root, dirs, files_list in os.walk(PDF_ROOT_FOLDER):
                for pdf_file in files_list:
                    if os.path.isfile(os.path.join(root, pdf_file)):
                        jt = pdf_file.split('.')[0]
                        if jt not in expected_results or expected_results[jt]['validated'] != '1':
                            continue
                        pdf_path = os.path.join(root, pdf_file)
                        report = pdfparser.report.Report()
                        extractor = pdfextractor.PDFTextExtractor(report=report)
                        pdf_text = extractor.extract_text(pdf_path)
                        self.validate_pdf_structure(expected_results[jt], report, test_results)
            test_results.flush()

    def validate_pdf_structure(self, expected_structure, extract_report, test_results):
        jt = expected_structure['jt']
        test_results.write('#'*30+'\n')
        test_results.write('JT: {jt}\n'.format(jt=jt))
        test_results.write('#'*30+'\n')
        for key in expected_structure.iterkeys():
            if key == 'jt' or key == 'validated':
                continue
            actual = extract_report.__dict__[key.lower()]
            expected = int(expected_structure[key])
            '''
            self.assertEqual(expected,
                             actual,
                             msg='JT: {jt} - {key}: Expected {expected} - Actual {actual} '.format(jt=jt,
                                                                                                   key=key,
                                                                                                   expected=expected,
                                                                                                   actual=actual))
            '''
            match = True if expected == actual else False
            if not match:
                test_results.write('-'*30+'\n')
                test_results.write('{key}: Expected {expected} - Actual {actual} - Result: {match}\n'.format(key=key,
                                                                                              expected=expected,
                                                                                              actual=actual,
                                                                                              match=match))
                test_results.write('-'*30+'\n')


def load_expected_results():
    expected_results = dict()
    with open('expected_results.csv', 'rb') as csv_results:
        csvreader = csv.DictReader(csv_results, delimiter=',')
        for row in csvreader:
            expected_results[row['jt']] = row
    return expected_results


if __name__ == '__main__':
    unittest.main()
