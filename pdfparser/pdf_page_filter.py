# -*- coding: utf8 -*-
import logging

import pdfparser.table_edges_extractor as table_extractor

X0, Y0, X1, Y1 = 0, 1, 2, 3


class PDFPageFilter:

    def __init__(self):
        pass

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
    def is_toc(page_txt):
        nb = 0
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if fragment == 'TABLE OF CONTENTS' >= 0:  # Expected text in uppercase !
                return True
            # TODO: improve the following piece of crap...
            elif fragment.find('..........') > 0:
                nb += 1
            if nb > 5:
                return True
        return False

    @staticmethod
    def is_glossary(page_txt):
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if (fragment.find('LIST OF ABBREVIATIONS') >= 0 or
                fragment.find('GLOSSARY') >= 0):   # Expected text in uppercase !
                return True
        return False

    @staticmethod
    def is_bibliography(page_txt):
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if (fragment.lower().find('BIBLIOGRAPHY'.lower()) >= 0 or
                fragment.lower().find('Bibliographie'.lower()) >= 0 or
                fragment == 'REFERENCES'):  # Expected text in uppercase as unique word of sentence
                return True
        return False

    @staticmethod
    def is_participants_list(page_txt):
        for coord, fragment in page_txt.items():
            fragment = fragment.strip().lower()
            if (fragment.find('Participants list'.lower()) >= 0 or
                        fragment.find('Liste des participants'.lower()) >= 0):
                return True
        return False

    @staticmethod
    def is_annex(page_txt):
        ###
        # Expect to find word 'ANNEX' (in upper case) as first word of sentence, top of the page
        ###
        # TODO: add logic to check that text is first on page
        for coord, fragment in page_txt.items():
            fragment = fragment.strip()
            if fragment.rfind('ANNEX') == 0:  # Expected text in uppercase !
                return True
        return False

    @staticmethod
    def ignore_tables_content(page_txt, page_cells):
        outer_edges = table_extractor.find_outer_edges(page_cells)
        # TODO: move this logic into find_outer_edges
        if len(outer_edges) > 0:
            outer_edges = [cell for cell in outer_edges if cell.rows > 2 and cell.columns > 2]

        if len(outer_edges) > 0:
            logging.getLogger('summarizer').debug('Found {ntables} tables on page'.format(ntables=len(outer_edges)))
            for cell in outer_edges:
                logging.getLogger('summarizer').debug(cell)
                logging.getLogger('summarizer').debug('{nrows} inner rows '
                                                      'and {ncolumns} inner columns'.format(nrows=cell.rows,
                                                                                            ncolumns=cell.columns))
            for coord, _ in page_txt.items():
                if within_table(coord, outer_edges):
                    logging.getLogger('summarizer').debug('Inner text ignored.')
                    del page_txt[coord]


def within_table(text_cell, outer_edges):
    for cell in outer_edges:
        if cell.x0 <= text_cell[X0] and cell.y0 <= text_cell[Y0] \
                and text_cell[X1] <= cell.x1 and text_cell[Y1] <= cell.y1:
            logging.getLogger('summarizer').debug('Match found: {text_cell} and {cell}'.format(cell=cell,
                                                                                               text_cell=text_cell))
            return True
    return False
