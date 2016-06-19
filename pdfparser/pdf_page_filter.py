# -*- coding: utf8 -*-
import re

from pdfparser import logger, _log_level, _config
import pdfparser.table_edges_extractor as table_extractor
from pdfparser.pdf_fragment_type import FragmentType
from pdfparser.report import Report

X0, Y0, X1, Y1 = 0, 1, 2, 3


class PDFPageFilter:

    def __init__(self, report=None):
        self.__TEXT_MIN_FRACTION_SIZE = _config.getfloat('MAIN', 'TEXT_MIN_FRACTION_SIZE')
        self.__MIN_NUMBER_ROWS = _config.getfloat('MAIN', 'MIN_NUMBER_ROWS')
        self.__MIN_NUMBER_COLS = _config.getfloat('MAIN', 'MIN_NUMBER_COLS')

        self.report = report if report else Report()
        self.tables_text = list()

    def is_cover(self, page_txt):
        nb_match = 0
        txt = ''
        ptrn_cote = re.compile('[\w]+/[[\w/]+]?\(\d{2,4}\)\d*.*|'
                               '[\w]+\(\d{2,4}\)\d*.*')
        ptrn_classif = re.compile('For Official Use|Confidential|Unclassified|A Usage Officiel'
                                  '|Confidentiel|Non classifi.{1,2}|Diffusion Restreinte|Restricted Diffusion'
                                  '|Restricted|general distribution', re.IGNORECASE)
        ptrn_oecd = re.compile('Organisation for Economic Co-operation and Development'
                               '|International Transport Forum|'
                               'European Conference of Ministers of Transport|'
                               'Co-ordinated Organisations')
        ptrn_ocde = re.compile('Organisation de Coop.{1,2}ration et de D.{1,2}veloppement .{1,2}conomiques'
                               '|Forum International des Transports|'
                               'Conf.{1,2}rence Europ.{1,2}enne des Ministres des Transports|'
                               'Organisations Coordonn.{1,2}es')
        ptrn_oecd_telex = re.compile('.*ORGANISATION FOR ECONOMIC.*\s?.*CO.*?OPERATION AND DEVELOPMENT.*', re.MULTILINE)
        ptrn_oecd_telex_start = re.compile('.*ORGANISATION FOR ECONOMIC.*\s?.*')
        ptrn_oecd_telex_end = re.compile('.*CO.*?OPERATION AND DEVELOPMENT.*')
        ptrn_ocde_telex = re.compile('.*ORGANISATION DE COOP.{1,2}RATION.*\s?.*ET DE D.{1,2}VELOPPEMENT .{1,2}CONOMIQUES.*', re.MULTILINE)
        ptrn_ocde_telex_start = re.compile('.*ORGANISATION DE COOP.{1,2}RATION.*\s?.*')
        ptrn_ocde_telex_end = re.compile('.*ET DE D.{1,2}VELOPPEMENT .{1,2}CONOMIQUES.*')

        for _, fragment in page_txt.items():
            txt += fragment.strip()

        # Cote
        if re.search(ptrn_cote, txt):
            nb_match += 1
        else:
            if _log_level > 0:
                logger.debug('No cote found')
        # Classification
        if re.search(ptrn_classif, txt):
            nb_match += 1
        else:
            if _log_level > 0:
                logger.debug('No classification found')
        # OECD
        if re.search(ptrn_oecd, txt) or re.search(ptrn_oecd_telex, txt):
            nb_match += 1
        elif re.search(ptrn_oecd_telex_start, txt) or re.search(ptrn_oecd_telex_end, txt):
            nb_match += 0.5
        else:
            if _log_level > 0:
                logger.debug('No OECD found')
        # OCDE
        if re.search(ptrn_ocde, txt) or re.search(ptrn_ocde_telex, txt):
            nb_match += 1
        elif re.search(ptrn_ocde_telex_start, txt) or re.search(ptrn_ocde_telex_end, txt):
            nb_match += 0.5
        else:
            if _log_level > 0:
                logger.debug('No OCDE found')

        if nb_match > 2:
            self.report.cover_page = 1
            return True
        else:
            return False

    def is_summary(self, page_txt, current_fragment_type):
        """

        Sample documents:
            - '2014/11/03/JT03365426.pdf'
        :param page_txt:
        :param current_fragment_type:
        :return:
        """
        ptrn_summary = re.compile('^\s*?SUMMARY\s*?$|'
                                  '^\s*?ABSTRACT\s*?$|'
                                  '^\s*?R.{1,2}SUM.{1,2}\s*?$|'
                                  '^\s*?EXECUTIVE SUMMARY\s*?$', re.IGNORECASE)
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if re.match(ptrn_summary, fragment):
                logger.debug('Summary "Title" found: {frag}'.format(frag=fragment))
                self.report.summary = 1
                return True
        return False

    def is_toc(self, page_txt, current_fragment_type):
        # TODO: improve to handle situation where text follows toc on same page (see IMP19901498FRE)
        ptrn_toc_title = re.compile('TABLE OF CONTENTS|TABLE DES MATI.{1,2}RES|SOMMAIRE')  # Expected text in uppercase
        ptrn_toc_exact = re.compile('Table des mati.{1,2}res')  # Expected text in uppercase
        ptrn_toc_cont = re.compile('([\.]{10,}?\s[0-9]{1,4})')
        nb = 0
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if re.search(ptrn_toc_title, fragment) or re.match(ptrn_toc_exact, fragment):
                self.report.toc = 1
                return True
            # Avoid un-necessary parsing of the page
            if not current_fragment_type == FragmentType.TABLE_OF_CONTENTS:
                continue
            # if regexp matches and previous page was already 'Table of Content'
            # then assume this is the continuation of 'Table of Content'
            nb += len(re.findall(ptrn_toc_cont, fragment))
            if nb > 2 and current_fragment_type == FragmentType.TABLE_OF_CONTENTS:
                self.report.toc = 1
                return True
        return False

    def is_glossary(self, page_txt, current_fragment_type):
        ptrn_glossary_title = re.compile('^\W*?LIST OF ABBREVIATIONS|'
                                         '^\W*?GLOSSARY|'
                                         '^\W*?LIST OF ACRONYMS|'
                                         '^\W*?Abbreviations\s*?$')
        ptrn_glossary_struct = re.compile('(?:[A-Z]{3,10}\s+?–\s+?[A-Z])')
        nb = 0
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if re.search(ptrn_glossary_title, fragment):   # Expected text in uppercase !
                self.report.glossary = 1
                return True
            # Avoid un-necessary parsing of the page
            if not current_fragment_type == FragmentType.GLOSSARY:
                continue
            # Some examples of patterns usually found in glossaries:
            # "ATM – Agriculture Trade and Markets division of TAD"
            # "COAG – Committee for Agriculture of the OECD"
            nb += len(re.findall(ptrn_glossary_struct, fragment))
            if nb > 5:
                self.report.glossary = 1
                return True
        return False

    def is_bibliography(self, page_txt, current_fragment_type):
        # TODO: either improve regexp (case sensitive?)
        # or detect that text initially came from a table (see JT03366941 page 49)
        ptrn_biblio = re.compile('^\s*?bibliograph(y|ie)\s*?$|'
                                 '^\s*?r.{1,2}f.{1,2}rence(?:s)?\s*?$|'
                                 '^\s*?lit(?:t)?erature\s*?$', re.IGNORECASE)
        ptrn_biblio_cont = re.compile('((?:[A-Z].*[A-Z])?(?:OECD)?.*\([0-9]{4}.*\).*)')
        nb = 0
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if re.match(ptrn_biblio, fragment):
                logger.debug('Bibliography "Title" found: {frag}'.format(frag=fragment))
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
            nb += len(re.findall(ptrn_biblio_cont, fragment))
            if nb > 2:  # and current_fragment_type == FragmentType.BIBLIOGRAPHY:
                logger.debug('Bibliography "pattern" found.')
                self.report.bibliography = 1
                return True, None
        return False, None

    def is_participants_list(self, page_txt, current_fragment_type):
        ptrn_part_exact_1 = re.compile('Participants list|LIST OF PARTICIPANTS|Liste des participants',
                                       re.IGNORECASE)
        ptrn_part_exact_2 = re.compile('^\W*?PRESENT(S)?\W*?$')
        ptrn_part_find_1 = re.compile('(List of Participants|Liste des Participants)'
                                    ' ?/ ?(Liste des Participants|List of Presence)',
                                    re.IGNORECASE)
        ptrn_part_find_2 = re.compile('LIST OF PARTICIPANTS')
        nb = 0
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()

            if re.match(ptrn_part_exact_1, fragment) :
                self.report.participants_list = 1
                logger.debug('participants section title found. Match:{match}'.format(match='ptrn_part_exact_1'))
                return True, coord
            if re.match(ptrn_part_exact_2, fragment):
                self.report.participants_list = 1
                logger.debug('participants section title found. Match:{match}'.format(match='ptrn_part_exact_2'))
                return True, coord
            if re.search(ptrn_part_find_1, fragment):
                self.report.participants_list = 1
                logger.debug('participants section title found. Match:{match}'.format(match='ptrn_part_find_1'))
                return True, coord
            if re.search(ptrn_part_find_2, fragment):
                self.report.participants_list = 1
                logger.debug('participants section title found. Match:{match}'.format(match='ptrn_part_find_2'))
                return True, coord
            # Avoid un-necessary parsing of the page
            if not current_fragment_type == FragmentType.PARTICIPANTS_LIST:
                continue

            # if regexp matches and previous page was already 'Participants List'
            # then assume this is the continuation of 'Participants List'.
            # "Mr. Christian HEDERER, Counsellor for Energy, Trade, Industry and Science"
            # "Ms. Maria-Antoinetta SIMONS, Permanent Delegation of Belgium to the OECD"
            nb += len(re.findall('^\s*?(?:M[r]?\.?|Mme\.?|M[i|r]?s[s]?\.?|Dr\.?)(?: [A-Za-z\s]*?.*? [A-Z ]*[,|\s]?)', fragment))
            logger.debug('continued participants found. nb: {nb}'.format(nb=nb))
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
            logger.debug('continued participants found. nb: {nb}'.format(nb=nb))
            if nb > 2 and current_fragment_type == FragmentType.PARTICIPANTS_LIST:
                self.report.participants_list = 1
                return True
        return False

    def is_annex(self, page_txt, current_fragment_type):
        ptrn_annex = re.compile('^\W*ANNEX(E)?\s*[0-9]?[A-Z]?\.?\s*$|'
                                '^\W*ANNEX(E)?\s*[0-9]?[A-Z]?\.?\s*?-?\s*?:?[\W\w]*?$|'
                                '^\W*Annex(e)?\s{1,2}[0-9]?[a-z]?\s*$|'
                                '^\W*APPENDI(X|CE)\s*[0-9]?[A-Z]?\s*$|'
                                '^\s*TECHNICAL ANNEX\s*$|'
                                '^\s*FIGURE AND TABLE ANNEX\s*$')
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if re.search(ptrn_annex, fragment):
                self.report.annex = 1
                return True
        return False

    def filter_tables(self, page_txt, page_cells):
        logger.debug('nb cells: {nb}'.format(nb=len(page_cells)))
        outer_edges = table_extractor.find_outer_edges(page_cells) if len(page_cells) > 1 else []
        logger.debug('nb candidate tables found: {nb}'.format(nb=len(outer_edges)))

        if len(outer_edges) > 0:
            # Consider only tables with at least MIN_NUMBER_ROWS and MIN_NUMBER_COLS
            outer_edges = [table for table in outer_edges if table.rows > self.__MIN_NUMBER_ROWS and
                           table.columns > self.__MIN_NUMBER_COLS]

        if len(outer_edges) > 0:
            self.report.tables = 1
            logger.info('\nMATCH - {Table} found.')
            logger.debug('Found {ntables} actual tables on page'.format(ntables=len(outer_edges)))
            for table in outer_edges:
                logger.debug(table)
                logger.debug('{nrows} inner rows and {ncolumns} inner columns'.format(nrows=table.rows,
                                                                                      ncolumns=table.columns))
            logger.debug('Before table filtering, length of page text:{len}'.format(len=len(page_txt)))
            for coord, _ in page_txt.items():
                cell_content = page_txt[coord].strip()
                if self.text_is_a_cell(coord, outer_edges):
                    cell_content = filter_number(cell_content)
                    cell_content = self.filter_repetition(cell_content)
                    page_txt[coord] = cell_content
            logger.debug('After table filtering, length of page text:{len}'.format(len=len(page_txt)))

    def filter_repetition(self, cell_content):
        if _log_level > 2:
            logger.debug(u'Looking if {txt} is a repetition'.format(txt=cell_content))
        fragments = split_cell_content(cell_content)
        result = ''

        if not fragments:
            return cell_content

        for fragment in fragments:
            if fragment in self.tables_text:
                if _log_level > 1:
                    logger.debug(u'[Table inner text] - repetition found: {txt}'.format(txt=fragment))
            else:
                if _log_level > 2:
                    logger.debug(u'{txt} not found yet in {tt}'.format(txt=fragment, tt=self.tables_text))
                self.tables_text.append(fragment)
                result += fragment + '\n'
        return result

    def text_is_a_fraction(self, coord, table):
        table_width = abs(table.x0 - table.x1)
        text_width = abs(coord[X0] - coord[X1])
        fraction = text_width / table_width

        if _log_level > 2:
            logger.debug('table x0: {x0} - table x1: {x1}'.format(x0=table.x0, x1=table.x1))
            logger.debug('table width: {cw}'.format(cw=table_width))
            logger.debug('text x0: {x0} - text x1: {x1}'.format(x0=coord[X0], x1=coord[X1]))
            logger.debug('text width: {tw}'.format(tw=text_width))
            logger.debug('Fraction: {fraction}'.format(fraction=fraction))

        if fraction < self.__TEXT_MIN_FRACTION_SIZE:
            return True
        return False

    def text_is_a_cell(self, coord, outer_edges):
        for table in outer_edges:
            #if text_within_table(coord, table) and self.text_is_a_fraction(coord, table):
            if text_within_table(coord, table):
                if _log_level > 1:
                    logger.debug('Text cell {text_cell} inside table.'.format(text_cell=coord))
                return True
        return False


def filter_number(cell_content):
    if _log_level > 2:
        logger.debug(u'Looking if {txt} is a number'.format(txt=cell_content))
    fragments = split_cell_content(cell_content)
    result = ''
    for fragment in fragments:
        if re.match('^\s*?[0-9\.,]+\s*?$', fragment):
            if _log_level > 1:
                logger.debug(u'[Table inner text] - number found: {nb}'.format(nb=fragment))
        else:
            if _log_level > 1:
                logger.debug(u'[Table inner text] - not a number.')
            result += fragment + '\n'
    return result


def split_cell_content(cell_content):
    fragments = list()
    if '.' in cell_content:
        splits = [elem+'.' for elem in cell_content.split('.') if len(elem)]
        if len(splits) > 1:
            for frag in splits:
                if '\n' in frag:
                    fragments.extend(frag.split('\n'))
                else:
                    fragments.append(frag)
    elif '\n' in cell_content:
        splits = [elem for elem in cell_content.split('\n') if len(elem)]
        for frag in splits:
            fragments.append(frag)
    else:
        fragments.append(cell_content)
    return fragments


def text_within_table(coord, table):
    if table.x0 <= coord[X0] and table.y0 <= coord[Y0] \
            and table.x1 >= coord[X1] and table.y1 >= coord[Y1]:
        return True
    return False

