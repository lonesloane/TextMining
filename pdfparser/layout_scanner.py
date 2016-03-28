#!/usr/bin/python
import logging
import sys
import os
from binascii import b2a_hex

from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument, PDFNoOutlines
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import PDFPageAggregator
from pdfminer.layout import LAParams, LTTextBox, LTTextLine, LTFigure, LTImage, LTChar, LTRect

logger = logging.getLogger('pdf_layout')


def with_pdf(pdf_doc, fn, *args):
    """Open the pdf document, and apply the function, returning the results"""
    result = None
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
            # apply the function and return the result
            result = fn(doc, *args)

        # close the pdf file
        fp.close()
    except IOError:
        # the file doesn't exist or similar problem
        pass
    return result


###
# Table of Contents
###
def _parse_toc(doc):
    """With an open PDFDocument object, get the table of contents (toc) data
    [this is a higher-order function to be passed to with_pdf()]"""
    toc = []
    try:
        outlines = doc.get_outlines()
        for (level, title, dest, a, se) in outlines:
            toc.append((level, title))
    except PDFNoOutlines:
        pass
    return toc


def get_toc(pdf_doc):
    """Return the table of contents (toc), if any, for this pdf file"""
    return with_pdf(pdf_doc, _parse_toc)


###
# Extracting Text
###
def to_bytestring(s, enc='utf-8'):
    """Convert the given unicode string to a bytestring, using the standard encoding,
    unless it's already a bytestring"""
    if s:
        if isinstance(s, str):
            return s
        else:
            return s.encode(enc)


def update_page_text_hash(h, lt_obj, pct=0.2):
    """Use the bbox x0,x1 values within pct% to produce lists of associated text within the hash"""

    x0 = lt_obj.bbox[0]
    x1 = lt_obj.bbox[2]

    key_found = False
    for k, v in h.items():
        key_found = True
        logger.debug('+++String extracted: {s}'.format(s=to_bytestring(lt_obj.get_text())))
        v.append(to_bytestring(lt_obj.get_text()))
        h[k] = v
        # hash_x0 = k[0]
        # if x0 >= (hash_x0 * (1.0-pct)) and (hash_x0 * (1.0+pct)) >= x0:
        #     hash_x1 = k[1]
        #     if x1 >= (hash_x1 * (1.0-pct)) and (hash_x1 * (1.0+pct)) >= x1:
        #         # the text inside this LT* object was positioned at the same
        #         # width as a prior series of text, so it belongs together
        #         key_found = True
        #         v.append(to_bytestring(lt_obj.get_text()))
        #         h[k] = v
    if not key_found:
        # the text, based on width, is a new series,
        # so it gets its own series (entry in the hash)
        logger.debug('---String extracted: {s}'.format(s=to_bytestring(lt_obj.get_text())))
        h[(x0, x1)] = [to_bytestring(lt_obj.get_text())]

    return h


def parse_lt_objs(lt_objs, page_number, text=[]):
    """Iterate through the list of LT* objects and capture the text data contained in each"""
    text_content = []

    page_text = {}  # k=(x0, x1) of the bbox, v=list of text strings within that bbox width (physical column)
    for lt_obj in lt_objs:
        if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
            logger.debug('LTTextBox or LTTextLine')
            # text, so arrange is logically based on its column width
            page_text = update_page_text_hash(page_text, lt_obj)
        elif isinstance(lt_obj, LTFigure):
            logger.debug('LTFigure -- ignoring')
            # LTFigure objects are containers for other LT* objects, so recurse through the children
            # text_content.append(parse_lt_objs(lt_obj, page_number, text_content))
            # WE IGNORE FIGURES
            continue
        elif isinstance(lt_obj, LTRect):
            logger.debug('LTRect')
        else:
            # Could this be yet another type of Layout object?
            logger.debug('Unknown object type: ' + str(type(lt_obj)))

    for k, v in sorted([(key,value) for (key,value) in page_text.items()]):
        # sort the page_text hash by the keys (x0,x1 values of the bbox),
        # which produces a top-down, left-to-right sequence of related columns
        text_content.append(''.join(v))

    return '\n'.join(text_content)


###
# Processing Pages
###
def _parse_pages (doc):
    """With an open PDFDocument object, get the pages and parse each one
    [this is a higher-order function to be passed to with_pdf()]"""
    rsrcmgr = PDFResourceManager()
    laparams = LAParams()
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    text_content = []
    for i, page in enumerate(PDFPage.create_pages(doc)):
        logger.debug('\n'+'-'*50)
        logger.debug(u'Processing page nb {i}'.format(i=i))
        logger.debug('-'*50)
        interpreter.process_page(page)
        # receive the LTPage object for this page
        layout = device.get_result()
        # layout is an LTPage object which may contain child objects like LTTextBox, LTFigure, LTImage, etc.
        text_content.append(parse_lt_objs(layout, (i+1)))

    return text_content


def get_pages(pdf_doc):
    """Process each of the pages in this pdf file and return a list of strings
    representing the text found in each page"""
    return with_pdf(pdf_doc, _parse_pages)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
