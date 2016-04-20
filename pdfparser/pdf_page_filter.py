# -*- coding: utf8 -*-
import re

from pdfparser import logger, _log_level
import pdfparser.table_edges_extractor as table_extractor
from pdfparser.pdf_fragment_type import FragmentType

X0, Y0, X1, Y1 = 0, 1, 2, 3


class PDFPageFilter:
    # TODO: extract to configuration file
    MIN_NUMBER_ROWS = 2
    MIN_NUMBER_COLS = 2

    def __init__(self):
        pass

    @staticmethod
    def is_summary(page_txt, current_fragment_type):
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if (fragment.lower().find('SUMMARY'.lower()) >= 0 or
                fragment.lower().find('EXECUTIVE SUMMARY'.lower()) >= 0):
                return True
        return False

    @staticmethod
    def is_cover(page_txt):
        for coord, fragment in page_txt.items():
            fragment = fragment.strip().lower()
            if (fragment.find('For Official Use'.lower()) >= 0 or
                fragment.find('Confidential'.lower()) >= 0 or
                fragment.find('A usage officiel'.lower()) >= 0 or
                fragment.find('Confidentiel'.lower()) >= 0 or
                fragment.find('Non classifié'.lower()) >= 0 or
                fragment.find('Unclassified'.lower()) >= 0) and \
                (fragment.find('Organisation de Coopération et de Développement Économiques'.lower()) >= 0 and
                fragment.find('Organisation for Economic Co-operation and Development'.lower()) >= 0):
                return True
        return False

    @staticmethod
    def is_toc(page_txt, current_fragment_type):
        nb = 0
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if fragment == 'TABLE OF CONTENTS' >= 0:  # Expected text in uppercase !
                return True
            # if regexp matches and previous page was already 'Table of Content'
            # then assume this is the continuation of 'Table of Content'
            nb += len(re.findall('([\.]{10,}?\s[0-9]{1,4})', fragment))
            if nb > 2 and current_fragment_type == FragmentType.TABLE_OF_CONTENTS:
                return True
        return False

    @staticmethod
    def is_glossary(page_txt, current_fragment_type):
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if (fragment.find('LIST OF ABBREVIATIONS') >= 0 or
                fragment.find('GLOSSARY') >= 0):   # Expected text in uppercase !
                return True
        return False

    @staticmethod
    def is_bibliography(page_txt, current_fragment_type):
        nb = 0
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            # TODO: improve the following to avoid false positive
            if (fragment.lower().find('BIBLIOGRAPHY'.lower()) >= 0 or
                fragment.lower().find('Bibliographie'.lower()) >= 0 or
                fragment == 'REFERENCES' or fragment == 'RÉFÉRENCES'):
                return True
            # if regexp matches and previous page was already 'Bibliography'
            # then assume this is the continuation of 'Bibliography'.
            # Some examples of patterns usually found in bibliographies:
            # "Baumol, W. (1967), “Macroeconomics of unbalanced growth: the anatomy of urban crisis”, American"
            # "OECD (2010c), The OECD Innovation Strategy: Getting a Head Start on Tomorrow, Paris: OECD."
            nb += len(re.findall('((?:[A-Z].*[A-Z])?(?:OECD)?.*\([0-9]{4}.*\).*)', fragment))
            if nb > 2 and current_fragment_type == FragmentType.BIBLIOGRAPHY:
                return True
        return False

    @staticmethod
    def is_participants_list(page_txt, current_fragment_type):
        for coord, fragment in page_txt.items():
            fragment = fragment.strip().lower()
            if (fragment.find('Participants list'.lower()) >= 0 or
                        fragment.find('Liste des participants'.lower()) >= 0):
                return True
        return False

    @staticmethod
    def is_annex(page_txt, current_fragment_type):
        # Expect to find word 'ANNEX' (in upper case) as first word of sentence, top of the page
        # TODO: add logic to check that text is first on page
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if fragment.rfind('ANNEX') == 0:  # Expected text in uppercase !
                return True
        return False

    @staticmethod
    def filter_tables(page_txt, page_cells):
        outer_edges = table_extractor.find_outer_edges(page_cells) if len(page_cells) > 1 else []

        if len(outer_edges) > 0:
            # Consider only tables with at least MIN_NUMBER_ROWS and MIN_NUMBER_COLS
            outer_edges = [cell for cell in outer_edges if cell.rows > PDFPageFilter.MIN_NUMBER_ROWS
                           and cell.columns > PDFPageFilter.MIN_NUMBER_COLS]

        if len(outer_edges) > 0:
            # TODO: Find a way to keep the content of tables, surrounded by explicit "table" elements
            logger.info('\nMATCH - {Table} found.')
            logger.debug('Found {ntables} tables on page'.format(ntables=len(outer_edges)))
            for cell in outer_edges:
                logger.debug(cell)
                logger.debug('{nrows} inner rows and {ncolumns} inner columns'.format(nrows=cell.rows,
                                                                                      ncolumns=cell.columns))
            logger.debug('Before table filtering, length of page text:{len}'.format(len=len(page_txt)))
            for coord, _ in page_txt.items():
                if within_table(coord, outer_edges):
                    if _log_level > 2:
                        logger.debug('Inner text ignored.')
                    del page_txt[coord]
            logger.debug('After table filtering, length of page text:{len}'.format(len=len(page_txt)))

    @staticmethod
    def process_text(page_txt, page_cells):
        PDFPageFilter.filter_tables(page_txt, page_cells)
        for coord, substring in page_txt.items():
            # remove paragraph numbers, e.g. "23."
            # sometimes wrongly inserted within the text from incorrect layout analysis
            if _log_level > 2:
                logger.debug('regexp on [{substring}]'.format(substring=substring))
            result = re.sub('(\s?[0-9]{1,4}\.\s?)', ' ', substring)
            if _log_level > 2:
                logger.debug('result: [{result}]'.format(result=result))
            page_txt[coord] = result


def within_table(text_cell, outer_edges):
    for cell in outer_edges:
        if cell.x0 <= text_cell[X0] and cell.y0 <= text_cell[Y0] \
                and text_cell[X1] <= cell.x1 and text_cell[Y1] <= cell.y1:
            if _log_level > 2:
                logger.debug('Match found: {text_cell} and {cell}'.format(cell=cell, text_cell=text_cell))
            return True
    return False
