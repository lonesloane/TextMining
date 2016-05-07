from cStringIO import StringIO
from json import JSONEncoder

from nltk import PunktSentenceTokenizer
from pdfminer.converter import TextConverter, PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTRect, LTChar
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

from pdfparser import logger, _log_level
from pdfparser.pdf_fragment_type import FragmentType
from pdfparser.pdf_page_filter import PDFPageFilter
from pdfparser.table_edges_extractor import Cell

# LOG Files for debugging and visual analysis purposes
rec_def = None
text_def = None


class PDFTextExtractor:

    def __init__(self, report=None):
        # self.xml_root = ET.Element('pdfContent')
        self.contents = dict()
        self.report = report

    def extract_text(self, pdf_file_path):
        # pdf_text = self.convert_pdf_to_txt(pdf_file)
        pdf_text = self.convert_pdf_layout_to_text(pdf_file_path)
        return pdf_text

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

            validated_txt, _continue = self.validate(page_txt, None)
            if not _continue:
                break

            if len(validated_txt) > 0:
                logger.info("-"*40)
                logger.info("page {page_no} processed".format(page_no=page_no))
                logger.debug("Page content: %s", validated_txt)
                logger.info("-"*40)

            pdf_txt += '\n'+validated_txt

        fp.close()
        return pdf_txt

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
                logger.info("="*20)
                logger.info("Parsing PDF content\n")
                logger.info("="*20)
                pages = self.parse_pages(doc)

                page_nb = 0
                fragment_type = FragmentType.UNKNOWN
                for page_text, page_cells in pages:
                    logger.info('='*20)
                    logger.info('Validating page {page_nb}'.format(page_nb=page_nb))
                    logger.info('='*20)
                    fragment_type = self.validate(page_text, page_cells, fragment_type)
                    page_nb += 1
                    # TODO: See if possible to keep processing documents beyond annexes
                    if fragment_type is FragmentType.ANNEX:
                        break

                #pdf_txt = ET.tostring(self.xml_root)
                pdf_txt = JSONEncoder().encode(self.contents)

        except IOError:
            # the file doesn't exist or similar problem
            logger.error("Error while processing pdf file.")
        finally:
            # close the pdf file
            fp.close()

        return pdf_txt

    def parse_pages(self, doc):
        """With an open PDFDocument object, get the pages and parse each one
        """
        rsrcmgr = PDFResourceManager()
        laparams = LAParams()
        device = PDFPageAggregator(rsrcmgr, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        pages = []
        for i, page in enumerate(PDFPage.create_pages(doc)):
            #if i < 1 or i > 1:
            #    continue
            if _log_level > 2:
                logger.debug('\n'+'-'*50)
                logger.debug('Processing page {i}'.format(i=i))
                logger.debug('-'*50)
            interpreter.process_page(page)
            # receive the LTPage object for this page
            layout = device.get_result()
            # layout is an LTPage object which may contain child objects like LTTextBox, LTFigure, LTImage, etc.
            pages.append(self.parse_page_layout(layout))
        return pages

    def parse_page_layout(self, lt_objs, reverse=True):
        """Iterate through the list of LT* objects and capture the text data contained in each"""
        global rec_def, text_def
        if _log_level > 2:
            rec_def = open('rec_def.log', mode='w')
            text_def = open('text_def.log', mode='w')

        page_text = dict()  # k=(x0, y0, x1, y1) of the bbox, v=text within that bbox
        page_cells = []
        for lt_obj in lt_objs:
            if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                if _log_level > 1:
                    logger.debug('LTTextBox or LTTextLine')
                # text container, extract...
                page_text = self.extract_object_text_hash(page_text, lt_obj)
            elif isinstance(lt_obj, LTChar):
                if _log_level > 1:
                    logger.debug('LTChar')
                # text container, extract...
                page_text = self.extract_object_text_hash(page_text, lt_obj)
            elif isinstance(lt_obj, LTRect):
                # store cell coordinates used to identify table boundaries
                x0 = lt_obj.bbox[0]
                y0 = lt_obj.bbox[1]
                x1 = lt_obj.bbox[2]
                y1 = lt_obj.bbox[3]
                page_cells.append(Cell(x0, y0, x1, y1))
                if _log_level > 1:
                    logger.debug('LTRect: [x0={x0}, y0={y0}, x1={x1}, y1={y1}]'.format(x0=x0, y0=y0, x1=x1, y1=y1))
                    if _log_level > 2:
                        rec_def.write('{x0},{y0},{x1},{y1}\n'.format(x0=x0, y0=y0, x1=x1, y1=y1))
            elif isinstance(lt_obj, LTFigure):
                # TODO: Some documents are entirely made up of LTFigures. Not possible to simply ignore them !!!
                # At least, check if no text was extracted at all, in which case fallback to other extraction strategy.
                # eg:
                # '2014/11/03/JT03365454.pdf'
                # '2014/11/07/JT03365773.pdf'
                # '2014/11/07/JT03365809.pdf'
                if _log_level > 1:
                    logger.debug('LTFigure -- ignoring')
                # LTFigure objects are containers for other LT* objects, so recurse through the children
                # return parse_page_layout(lt_obj, reverse=False)
                continue
            else:
                # yet another type of Layout object...
                if _log_level > 1:
                    logger.debug('Unknown object type: ' + str(type(lt_obj)))

        if _log_level > 2:
            rec_def.close()
            text_def.close()

        return page_text, page_cells

    def extract_object_text_hash(self, h, lt_obj):
        global text_def
        x0 = lt_obj.bbox[0]
        y0 = lt_obj.bbox[1]
        x1 = lt_obj.bbox[2]
        y1 = lt_obj.bbox[3]
        if _log_level > 1:
            logger.debug('[x0={x0}, y0={y0}, x1={x1}, y1={y1}]:\n {s}'.format(x0=x0, y0=y0, x1=x1, y1=y1,
                                                                              s=to_bytestring(lt_obj.get_text())))
        if _log_level > 2:
            text_def.write('{x0}|{y0}|{x1}|{y1}|{s}\n'.format(x0=x0, y0=y0, x1=x1, y1=y1,
                                                              s=to_bytestring(lt_obj.get_text().replace('\n', ' '))))
        h[(x0, y0, x1, y1)] = to_bytestring(lt_obj.get_text())
        return h

    def validate(self, page_txt, page_cells, previous_fragment_type):
        logger.debug('Enter page validation')
        pdf_filter = PDFPageFilter(report=self.report)

        coord = None
        while True:
            is_cover = pdf_filter.is_cover(page_txt)
            if is_cover:
                logger.info('\nMATCH - {Cover Page} found.')
                current_fragment_type = FragmentType.COVER_PAGE
                break

            is_toc = pdf_filter.is_toc(page_txt, previous_fragment_type)
            if is_toc:
                logger.info('\nMATCH - {Table Of Contents} found.')
                current_fragment_type = FragmentType.TABLE_OF_CONTENTS
                break

            is_summary = pdf_filter.is_summary(page_txt, previous_fragment_type)
            if is_summary:
                logger.info('\nMATCH - {Summary} found.')
                current_fragment_type = FragmentType.SUMMARY
                break

            is_glossary = pdf_filter.is_glossary(page_txt, previous_fragment_type)
            if is_glossary:
                logger.info('\nMATCH - {Glossary} found.')
                current_fragment_type = FragmentType.GLOSSARY
                break

            is_bibliography, coord = pdf_filter.is_bibliography(page_txt, previous_fragment_type)
            if is_bibliography:
                logger.info('\nMATCH - {Bibliography} found.')
                current_fragment_type = FragmentType.BIBLIOGRAPHY
                break

            is_participants_list = pdf_filter.is_participants_list(page_txt, previous_fragment_type)
            if is_participants_list:
                logger.info('\nMATCH - {Participants List} found.')
                current_fragment_type = FragmentType.PARTICIPANTS_LIST
                break

            is_annex = pdf_filter.is_annex(page_txt, previous_fragment_type)
            if is_annex:
                logger.info('\nMATCH - {Annex} found.')
                current_fragment_type = FragmentType.ANNEX
                break

            pdf_filter.process_text(page_txt, page_cells)
            current_fragment_type = FragmentType.TEXT
            break

        logger.debug('Exit page validation')

        if coord:  # TODO: remove condition, should always be true...
            # TODO: split page_txt before and after coord
            # then call add_fragment with previous and current fragment_type
            previous_fragment_txt = get_previous_fragment_text(page_txt, coord)
            next_fragment_txt = get_next_fragment_text(page_txt, coord)
            self.add_fragment(previous_fragment_txt, fragment_type=previous_fragment_type)
            self.add_fragment(next_fragment_txt, fragment_type=current_fragment_type)
        else:
            fragment_txt = get_fragment_text(page_txt)
            self.add_fragment(fragment_txt, fragment_type=current_fragment_type)

        return current_fragment_type

    def add_fragment(self, page_txt, fragment_type):
        content_list = list()
        for p in page_txt:
            content_list.append(p)
        if fragment_type not in self.contents:
            self.contents[fragment_type] = content_list
        else:
            self.contents[fragment_type].extend(content_list)


def extract_sentences(pdf_text):
        pdf_sentences = PunktSentenceTokenizer().tokenize(pdf_text.decode('utf-8'))
        return pdf_sentences


def get_fragment_text(page_txt):
    txt = [(-coord[1], -coord[0], str_array) for coord, str_array in page_txt.items()]
    return re_order_text(txt)


def get_previous_fragment_text(page_txt, split_coord):
    txt = [(-coord[1], -coord[0], str_array) for coord, str_array in page_txt.items() if coord[1] > split_coord[1]]
    return re_order_text(txt)


def get_next_fragment_text(page_txt, split_coord):
    txt = [(-coord[1], -coord[0], str_array) for coord, str_array in page_txt.items() if coord[1] <= split_coord[1]]
    return re_order_text(txt)


def re_order_text(txt):
    txt = sorted(txt)
    logger.debug('-' * 20)
    logger.debug('Sorted page text:')
    logger.debug('-' * 20)
    for elem in txt:
        logger.debug('{elem}'.format(elem=elem))
    return [str_array for _, _, str_array in txt]


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
