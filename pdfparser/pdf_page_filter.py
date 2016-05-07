# -*- coding: utf8 -*-
import re

from pdfparser import logger, _log_level
import pdfparser.table_edges_extractor as table_extractor
from pdfparser.pdf_fragment_type import FragmentType
from pdfparser.report import Report

X0, Y0, X1, Y1 = 0, 1, 2, 3


class PDFPageFilter:
    # TODO: extract to configuration file
    MIN_NUMBER_ROWS = 2
    MIN_NUMBER_COLS = 2

    def __init__(self, report=None):
        self.report = report if report else Report()

    def is_cover(self, page_txt):
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
                self.report.cover = 1
                return True
        return False

    def is_summary(self, page_txt, current_fragment_type):
        """

        Sample documents:
            - '2014/11/03/JT03365426.pdf'
        :param page_txt:
        :param current_fragment_type:
        :return:
        """
        for coord, fragment in page_txt.items():
            fragment = fragment.strip().lower()
            if (fragment == 'SUMMARY'.lower() or
                fragment == 'RÉSUMÉ'.lower() or
                fragment == 'EXECUTIVE SUMMARY'.lower()):
                self.report.summary = 1
                return True
        return False

    def is_toc(self, page_txt, current_fragment_type):
        nb = 0
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if fragment == 'TABLE OF CONTENTS' or \
               fragment == 'TABLE DES MATIÈRES':  # Expected text in uppercase !
                self.report.toc = 1
                return True
            # Avoid un-necessary parsing of the page
            if not current_fragment_type == FragmentType.TABLE_OF_CONTENTS:
                continue
            # if regexp matches and previous page was already 'Table of Content'
            # then assume this is the continuation of 'Table of Content'
            nb += len(re.findall('([\.]{10,}?\s[0-9]{1,4})', fragment))
            if nb > 2 and current_fragment_type == FragmentType.TABLE_OF_CONTENTS:
                self.report.toc = 1
                return True
        return False

    def is_glossary(self, page_txt, current_fragment_type):
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if (fragment.find('LIST OF ABBREVIATIONS') >= 0 or
                fragment.find('GLOSSARY') >= 0):   # Expected text in uppercase !
                self.report.glossary = 1
                return True
        return False

    def is_bibliography(self, page_txt, current_fragment_type):
        nb = 0
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            # TODO: improve the following to avoid false positive
            if (fragment.lower() == 'BIBLIOGRAPHY'.lower() or
                fragment.lower() == 'Bibliographie'.lower() or
                fragment == 'REFERENCES' or fragment == 'RÉFÉRENCES'):
                self.report.bibliography = 1
                return True, coord
            # Avoid un-necessary parsing of the page
            if not current_fragment_type == FragmentType.BIBLIOGRAPHY:
                continue
            # if regexp matches and previous page was already 'Bibliography'
            # then assume this is the continuation of 'Bibliography'.
            # Some examples of patterns usually found in bibliographies:
            # "Baumol, W. (1967), “Macroeconomics of unbalanced growth: the anatomy of urban crisis”, American"
            # "OECD (2010c), The OECD Innovation Strategy: Getting a Head Start on Tomorrow, Paris: OECD."
            nb += len(re.findall('((?:[A-Z].*[A-Z])?(?:OECD)?.*\([0-9]{4}.*\).*)', fragment))
            if nb > 2 and current_fragment_type == FragmentType.BIBLIOGRAPHY:
                self.report.bibliography = 1
                return True, None
        return False, None

    def is_participants_list(self, page_txt, current_fragment_type):
        for coord, fragment in page_txt.items():
            fragment = fragment.strip().lower()
            if (fragment.find('Participants list'.lower()) >= 0 or
                fragment.find('Liste des participants'.lower()) >= 0):
                self.report.participants_list = 1
                return True
        return False

    def is_annex(self, page_txt, current_fragment_type):
        # Expect to find word 'ANNEX' (in upper case) as first word of sentence, top of the page
        # TODO: add logic to check that text is first on page
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if fragment.rfind('ANNEX') == 0:  # Expected text in uppercase !
                self.report.annex = 1
                return True
        return False

    def filter_tables(self, page_txt, page_cells):
        outer_edges = table_extractor.find_outer_edges(page_cells) if len(page_cells) > 1 else []

        if len(outer_edges) > 0:
            # Consider only tables with at least MIN_NUMBER_ROWS and MIN_NUMBER_COLS
            outer_edges = [cell for cell in outer_edges if cell.rows > PDFPageFilter.MIN_NUMBER_ROWS
                           and cell.columns > PDFPageFilter.MIN_NUMBER_COLS]

        if len(outer_edges) > 0:
            # TODO: Find a way to keep the content of tables, surrounded by explicit "table" elements
            self.report.tables += 1
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

    def process_text(self, page_txt, page_cells):
        self.filter_tables(page_txt, page_cells)
        for coord, substring in page_txt.items():
            # remove paragraph numbers, e.g. "23."
            # sometimes wrongly inserted within the text from incorrect layout analysis
            result = re.sub('(\s?[0-9]{1,4}\.\s?)', ' ', substring)
            if _log_level > 2:
                logger.debug('regexp on [{substring}]'.format(substring=substring))
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

