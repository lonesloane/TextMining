import logging
from cStringIO import StringIO

from nltk import PunktSentenceTokenizer

from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTRect, LTChar
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from pdfparser.pdf_page_filter import PDFPageFilter

LOG_LEVEL = logging.DEBUG
_log_level = 3  # verbosity of log. 1:normal - 2:verbose - 3:visual

# LOG Files for debugging and visual analysis purposes
rec_def = None
text_def = None


class PDFTextExtractor:

    def __init__(self):
        self.logger = logging_setup()

    def extract_sentences(self, pdf_file_path):
        # pdf_string = convert_pdf_to_txt(pdf_file)
        pdf_string = self.convert_pdf_layout_to_text(pdf_file_path)
        pdf_sentences = PunktSentenceTokenizer().tokenize(pdf_string.decode('utf-8'))
        return pdf_sentences

    def convert_pdf_layout_to_text(self, pdf_doc):
        pdf_txt = ''
        try:
            # open the pdf file
            fp = open(pdf_doc, 'rb')
            # create a parser object associated with the file object
            parser = PDFParser(fp)
            # create a PDFDocument object that stores the document structure
            doc = PDFDocument(parser)
            # connect the parser and document objects
            parser.set_document(doc)

            if doc.is_extractable:
                pages = self._parse_pages(doc)
                page_no = 0

                for page in pages:
                    validated_txt, _continue = self.validate(page)
                    if not _continue:
                        break

                    if len(validated_txt) > 0:
                        self.logger.info("-"*20)
                        self.logger.info("page {page_no}".format(page_no=page_no))
                        self.logger.info("-"*20)
                        self.logger.debug(validated_txt)
                        self.logger.info("+"*40)

                    page_no += 1

                    pdf_txt += '\n'+validated_txt

            # close the pdf file
            fp.close()
        except IOError:
            # the file doesn't exist or similar problem
            self.logger.error("Error while processing pdf file.")

        return pdf_txt

    def convert_pdf_to_txt(self, path):
        rsrcmgr = PDFResourceManager()
        codec = 'utf-8'
        laparams = LAParams()
        fp = file(path, 'rb')
        password = ""
        maxpages = 0
        caching = True
        pagenos = set()
        pdf_txt = ''
        page_no = 0
        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,
                                      caching=caching, check_extractable=True):
            retstr = StringIO()
            page_no += 1

            device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
            PDFPageInterpreter(rsrcmgr, device).process_page(page)

            page_txt = retstr.getvalue()
            device.close()
            retstr.close()

            validated_txt, _continue = self.validate(page_txt)
            if not _continue:
                break

            if len(validated_txt) > 0:
                self.logger.info("-"*40)
                self.logger.info("page {page_no} processed".format(page_no=page_no))
                self.logger.debug("Page content: %s", validated_txt)
                self.logger.info("-"*40)

            pdf_txt += '\n'+validated_txt

        fp.close()
        return pdf_txt

    def extract_object_text_hash(self, h, lt_obj):
        global text_def
        x0 = lt_obj.bbox[0]
        y0 = lt_obj.bbox[1]
        x1 = lt_obj.bbox[2]
        y1 = lt_obj.bbox[3]
        if _log_level > 1:
            self.logger.debug('[x0={x0}, y0={y0}, x1={x1}, y1={y1}]:\n {s}'.format(x0=x0, y0=y0, x1=x1, y1=y1,
                                                                              s=to_bytestring(lt_obj.get_text())))
        if _log_level > 2:
            text_def.write('{x0}|{y0}|{x1}|{y1}|{s}\n'.format(x0=x0, y0=y0, x1=x1, y1=y1,
                                                              s=to_bytestring(lt_obj.get_text().replace('\n', ' '))))
        h[(y0, x0, y1, x1)] = to_bytestring(lt_obj.get_text())
        return h

    def parse_page_layout(self, lt_objs, reverse=True):
        """Iterate through the list of LT* objects and capture the text data contained in each"""
        global rec_def, text_def
        if _log_level > 2:
            rec_def = open('rec_def.log', mode='w')
            text_def = open('text_def.log', mode='w')

        text_content = []
        page_text = {}  # k=(x0, y0, x1, y1) of the bbox, v=text within that bbox
        for lt_obj in lt_objs:
            if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                if _log_level > 1:
                    self.logger.debug('LTTextBox or LTTextLine')
                # text container, extract...
                page_text = self.extract_object_text_hash(page_text, lt_obj)
            elif isinstance(lt_obj, LTChar):
                if _log_level > 1:
                    self.logger.debug('LTChar')
                # text container, extract...
                page_text = self.extract_object_text_hash(page_text, lt_obj)
            elif isinstance(lt_obj, LTFigure):
                # TODO: Some documents are entirely made up of LTFigures. Not possible to simply ignore them !!!
                # At least, check if no text was extracter at all, in which case fallback to other extraction strategy.
                '2014/11/07/JT03365773.pdf'
                '2014/11/07/JT03365809'
                if _log_level > 1:
                    self.logger.debug('LTFigure -- ignoring')
                # LTFigure objects are containers for other LT* objects, so recurse through the children
                # return parse_page_layout(lt_obj, reverse=False)
                continue
            elif isinstance(lt_obj, LTRect):
                # IGNORE LTRect
                if _log_level > 1:
                    x0 = lt_obj.bbox[0]
                    y0 = lt_obj.bbox[1]
                    x1 = lt_obj.bbox[2]
                    y1 = lt_obj.bbox[3]
                    self.logger.debug('LTRect: [x0={x0}, y0={y0}, x1={x1}, y1={y1}]'.format(x0=x0, y0=y0, x1=x1, y1=y1))
                    if _log_level > 2:
                        rec_def.write('{x0},{y0},{x1},{y1}\n'.format(x0=x0, y0=y0, x1=x1, y1=y1))
                continue
            else:
                # Could this be yet another type of Layout object?
                if _log_level > 1:
                    self.logger.debug('Unknown object type: ' + str(type(lt_obj)))

        if _log_level > 2:
            rec_def.close()
            text_def.close()

        return sorted([(key, value) for (key, value) in page_text.items()], reverse=reverse)

    def _parse_pages(self, doc):
        """With an open PDFDocument object, get the pages and parse each one
        """
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pages = []
        for i, page in enumerate(PDFPage.create_pages(doc)):
            #if i < 6 or i > 6:
            #    continue
            if _log_level > 2:
                self.logger.debug('\n'+'-'*50)
                self.logger.debug(u'Processing page {i}'.format(i=i))
                self.logger.debug('-'*50)
            interpreter.process_page(page)
            # receive the LTPage object for this page
            layout = device.get_result()
            # layout is an LTPage object which may contain child objects like LTTextBox, LTFigure, LTImage, etc.
            pages.append(self.parse_page_layout(layout))
        return pages

    def validate(self, page_txt):
        if PDFPageFilter.is_cover(page_txt):
            self.logger.info('\n{Cover Page} found. Page ignored.')
            return '', True
        elif PDFPageFilter.is_toc(page_txt):
            self.logger.info('\n{Table Of Contents} found. Page ignored.')
            return '', True
        elif PDFPageFilter.is_glossary(page_txt):
            self.logger.info('\n{Glossary} found. Page ignored.')
            return '', True
        elif PDFPageFilter.is_bibliography(page_txt):
            self.logger.info('\n{Bibliography} found. Remaining pages ignored.')
            return '', False
        elif PDFPageFilter.is_participants_list(page_txt):
            self.logger.info('\n{Participants List} found. Remaining pages ignored.')
            return '', False
        elif PDFPageFilter.is_annex(page_txt):
            self.logger.info('\n{Annex} found. Remaining pages ignored.')
            return '', False
        elif PDFPageFilter.contains_table(page_txt):
            self.logger.info('\n{Table} found. Page ignored.')
            return '', True

        txt = ''.join([str_array for coord, str_array in page_txt])
        return txt, True


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


def to_bytestring(s, enc='utf-8'):
        """Convert the given unicode string to a bytestring, using the standard encoding,
        unless it's already a bytestring"""
        if s:
            if isinstance(s, str):
                return s
            else:
                return s.encode(enc)


if __name__ == '__main__':
    pass
