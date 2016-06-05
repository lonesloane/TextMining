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
        txt = ''
        # TODO: use compiled regexp for better performances
        # TODO: improve logic by passing page number (cover is expected to be first page only)
        # TODO: deal with 'old' documents (see IMP19945916FRE) ==> look for combination of criteria
        #       rather than for all at once.
        for _, fragment in page_txt.items():
            txt += fragment.strip()

        # Cote
        # TODO: FIX this: DCD(2000)7
        if not re.search('[\w]+/[[\w/]+]?\(\d{2,4}\)\d*.*|C\(\d{2,4}\)\d*.*', txt):
            if _log_level > 0:
                logger.debug('No cote found')
            return False
        # Classification
        if not re.search(ur'For Official Use|Confidential|Unclassified|A Usage Officiel'
                         '|Confidentiel|Non classifi.|Diffusion Restreinte|Restricted Diffusion'
                         '|Restricted', txt, re.IGNORECASE):
            if _log_level > 0:
                logger.debug('No classification found')
            return False
        # OECD
        if not re.search(ur'Organisation for Economic Co-operation and Development'
                         '|International Transport Forum|European Conference of Ministers of Transport', txt):
            if _log_level > 0:
                logger.debug('No OECD found')
            return False
        # OCDE
        if not re.search(ur'Organisation de Coop.*ration et de D.*veloppement .*conomiques'
                         '|Forum International des Transports|Conf.*rence Europ.*enne des Ministres des Transports', txt):
            if _log_level > 0:
                logger.debug('No OCDE found')
            return False

        self.report.cover_page = 1
        return True

    def is_summary(self, page_txt, current_fragment_type):
        """

        Sample documents:
            - '2014/11/03/JT03365426.pdf'
        :param page_txt:
        :param current_fragment_type:
        :return:
        """
        #TODO: identify text within a box with title containing word summary or résumé (see 'IMP19991826FRE')
        for coord, fragment in page_txt.items():
            fragment = fragment.strip().lower()
            if (fragment == 'SUMMARY'.lower() or
                fragment == 'ABSTRACT'.lower() or
                fragment == 'RÉSUMÉ'.lower() or
                fragment == 'EXECUTIVE SUMMARY'.lower()):
                self.report.summary = 1
                return True
        return False

    def is_toc(self, page_txt, current_fragment_type):
        # TODO: IMP19961349FRE
        # TODO: improve to handle situation where text follows toc on same page (see IMP19981804ENG, IMP19901498FRE)
        nb = 0
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if re.search('TABLE OF CONTENTS', fragment) or \
                    re.search('TABLE DES MATI.+RES', fragment) or \
                    re.search('SOMMAIRE', fragment):  # Expected text in uppercase !
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
        nb = 0
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if (fragment.find('LIST OF ABBREVIATIONS') >= 0 or
                fragment.find('GLOSSARY') >= 0 or
                fragment.find('LIST OF ACRONYMS') >= 0):   # Expected text in uppercase !
                self.report.glossary = 1
                return True
            # Some examples of patterns usually found in glossaries:
            # "ATM – Agriculture Trade and Markets division of TAD"
            # "COAG – Committee for Agriculture of the OECD"
            nb += len(re.findall('(?:[A-Z]{3,10}\s+?–\s+?[A-Z])', fragment))
            if nb > 5:
                self.report.glossary = 1
                return True
        return False

    def is_bibliography(self, page_txt, current_fragment_type):
        nb = 0
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            # TODO: use regexps
            if (fragment.lower() == 'BIBLIOGRAPHY'.lower() or
                fragment.lower() == 'Bibliographie'.lower() or
                fragment.lower() == 'REFERENCES'.lower() or
                fragment.lower() == 'RÉFÉRENCES'.lower() or
                fragment.lower() == 'LITERATURE'.lower() or
                fragment.lower() == 'LITTERATURE'.lower()):
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
            if nb > 2: #and current_fragment_type == FragmentType.BIBLIOGRAPHY:
                self.report.bibliography = 1
                return True, None
        return False, None

    def is_participants_list(self, page_txt, current_fragment_type):
        # TODO: try to not rely on specific words (improve pattern recognition)
        # TODO: Fix: IMP19926745FRE
        nb = 0
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()

            # TODO: use regexp
            if (fragment.lower() == 'Participants list'.lower() or
                fragment.lower() == 'LIST OF PARTICIPANTS'.lower() or
                fragment == 'PRESENT' or fragment == 'PRESENTS' or
                fragment.lower() == 'Liste des participants'.lower() or
                fragment.lower().find('List of Participants / Liste des Participants'.lower()) > 0 or
                fragment.find('Liste des Participants/List of Presence') > 0 or
                fragment.lower().find('List of Participants/Liste des Participants'.lower()) > 0):
                self.report.participants_list = 1
                return True
            # Avoid un-necessary parsing of the page
            if not current_fragment_type == FragmentType.PARTICIPANTS_LIST:
                continue

            # TODO: write more robust unit tests for all regexp used !!!
            # if regexp matches and previous page was already 'Participants List'
            # then assume this is the continuation of 'Participants List'.
            # "Mr. Christian HEDERER, Counsellor for Energy, Trade, Industry and Science"
            # "Ms. Maria-Antoinetta SIMONS, Permanent Delegation of Belgium to the OECD"
            nb += len(re.findall('(?:M[r]?\.|Mme\.?|M[i|r]?s[s]?\.?|Dr\.?)(?: [A-Za-z\s]*?.*? [A-Z ]*[,|\s]?)', fragment))
            logger.debug('participants found. nb: {nb}'.format(nb=nb))
            if nb > 2 and current_fragment_type == FragmentType.PARTICIPANTS_LIST:
                self.report.participants_list = 1
                return True
            # "j.a.f.vandewijnboom@minez.nl\n"
            # "skowalczyk@ijhars.gov.pl \n"
            # "dkrzyzanowska@ijhars.gov.pl \n"
            # "dbalinska@ijhars.gov.pl\n"
            # "aszymanska@ijhars.gov.pl\n"
            # 'Marta.Dziubiak@minrol.gov.pl\n'
            nb += len(re.findall('\w*?\.?\w*@\w*\.\w*', fragment))
            logger.debug('participants found. nb: {nb}'.format(nb=nb))
            if nb > 2 and current_fragment_type == FragmentType.PARTICIPANTS_LIST:
                self.report.participants_list = 1
                return True
        return False

    def is_annex(self, page_txt, current_fragment_type):
        # Expect to find word 'ANNEX' (in upper case) as first word of sentence, top of the page
        # TODO: add logic to check that text is first on page
        # TODO: use regexp
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if fragment.rfind('ANNEX') == 0 or \
                fragment.rfind('[Annex]') == 0 or \
                fragment.rfind('APPENDIX') == 0 or \
                fragment.rfind('APPENDICE') == 0 or \
                fragment == 'TECHNICAL ANNEX' or \
                fragment == 'FIGURE AND TABLE ANNEX':  # Expected text in uppercase !
                self.report.annex = 1
                return True
        return False

    def is_notes(self, page_txt, current_fragment_type):
        # TODO: Finalize implementation of regexp
        # test on JT03367009, JT00111451
        nb = 0
        # Expect to find word 'NOTES' (in upper case) as first word of sentence, top of the page
        # TODO: add logic to check that text is first on page
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if fragment.rfind('NOTES') == 0:  # Expected text in uppercase !
                self.report.notes = 1
                return True
            # Avoid un-necessary parsing of the page
            if not current_fragment_type == FragmentType.NOTES:
                continue
            # if regexp matches and previous page was already 'Notes'
            # then assume this is the continuation of 'Notes'.
            # Some examples of patterns usually found in notes:
            # "13 See also Dumbill (2012), for which “big data” is “data that exceeds the processing capacity of "
            # "3 Drew Harwell, Whirlpool’s “Internet of Things” problem: No one really wants a “smart”"
            nb += len(re.findall('(?:M[r]?\.|Mme\.?|M[i|r]?s[s]?\.?|Dr\.?)(?: [A-Za-z\s]*?.*? [A-Z ]*[,|\s]?)', fragment))
            logger.debug('participants found. nb: {nb}'.format(nb=nb))
            if nb > 2 and current_fragment_type == FragmentType.NOTES:
                self.report.notes = 1
                return True
        return False

    def filter_tables(self, page_txt, page_cells):
        logger.debug('nb cells: {nb}'.format(nb=len(page_cells)))
        outer_edges = table_extractor.find_outer_edges(page_cells) if len(page_cells) > 1 else []
        logger.debug('nb candidate tables found: {nb}'.format(nb=len(outer_edges)))

        if len(outer_edges) > 0:
            # Consider only tables with at least MIN_NUMBER_ROWS and MIN_NUMBER_COLS
            outer_edges = [table for table in outer_edges if table.rows > PDFPageFilter.MIN_NUMBER_ROWS
                           and table.columns > PDFPageFilter.MIN_NUMBER_COLS]

        if len(outer_edges) > 0:
            # TODO: Find a way to keep the content of tables, surrounded by explicit "table" elements
            self.report.tables += len(outer_edges)
            logger.info('\nMATCH - {Table} found.')
            logger.debug('Found {ntables} actual tables on page'.format(ntables=len(outer_edges)))
            for table in outer_edges:
                logger.debug(table)
                logger.debug('{nrows} inner rows and {ncolumns} inner columns'.format(nrows=table.rows,
                                                                                      ncolumns=table.columns))
            logger.debug('Before table filtering, length of page text:{len}'.format(len=len(page_txt)))
            for coord, _ in page_txt.items():
                # TODO: change this to remove only numbers
                # and keep 1 occurrence of any textual content found in the tables (see JT00021419)
                if text_is_a_cell(coord, outer_edges):
                    logger.debug('\nignored text: {txt}'.format(txt=page_txt[coord]))
                    del page_txt[coord]
            logger.debug('After table filtering, length of page text:{len}'.format(len=len(page_txt)))

    @staticmethod
    def process_text(page_txt, page_cells):
        for coord, substring in page_txt.items():
            # remove paragraph numbers, e.g. "23."
            # sometimes wrongly inserted within the text from incorrect layout analysis
            result = re.sub('(^\s?[0-9]{1,4}\.(?:[0-9]{1,4})?\s?)', ' ', substring)
            if _log_level > 2:
                logger.debug('regexp on [{substring}]'.format(substring=substring))
                logger.debug('result: [{result}]'.format(result=result))
            page_txt[coord] = result


def text_is_a_cell(coord, outer_edges):
    for table in outer_edges:
        if text_within_table(coord, table) and text_is_a_fraction(coord, table):
            if _log_level > 2:
                logger.debug('Match found: {text_cell} and {cell}'.format(cell=table, text_cell=coord))
                logger.debug('Inner text ignored.')
            return True
    return False


def text_within_table(coord, table):
    if table.x0 <= coord[X0] and table.y0 <= coord[Y0] \
            and table.x1 >= coord[X1] and table.y1 >= coord[Y1]:
        return True
    return False


def text_is_a_fraction(coord, table):
    cell_width = abs(table.x0 - table.x1)
    text_width = abs(coord[X0] - coord[X1])
    fraction = text_width / cell_width

    if _log_level > 2:
        logger.debug('table x0: {x0} - table x1: {x1}'.format(x0=table.x0, x1=table.x1))
        logger.debug('table width: {cw}'.format(cw=cell_width))
        logger.debug('text x0: {x0} - text x1: {x1}'.format(x0=coord[X0], x1=coord[X1]))
        logger.debug('text width: {tw}'.format(tw=text_width))
        logger.debug('Fraction: {fraction}'.format(fraction=fraction))

    if fraction < .50:  # TODO: extract limit to config file
        return True
    return False
