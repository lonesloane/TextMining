# -*- coding: utf8 -*-
import logging


class PDFPageFilter:

    def __init__(self):
        pass

    @staticmethod
    def is_cover(page_txt):
        page_txt = page_txt.strip().lower()
        if (page_txt.find('For Official Use'.lower()) >= 0 or
            page_txt.find('Confidential'.lower()) >= 0 or
            page_txt.find('A usage officiel'.lower()) >= 0 or
            page_txt.find('Confidentiel'.lower()) >= 0 or
            page_txt.find('Non classifié'.lower()) >= 0 or
            page_txt.find('Unclassified'.lower()) >= 0) and \
            (page_txt.find('Organisation de Coopération et de Développement Économiques'.lower()) >= 0 and
            page_txt.find('Organisation for Economic Co-operation and Development'.lower()) >= 0):
            return True
        return False

    @staticmethod
    def is_toc(page_txt):
        page_txt = page_txt.strip()
        if page_txt.find('TABLE OF CONTENTS') >= 0:  # Expected text in uppercase !
            return True
        return False

    @staticmethod
    def is_list_of_abbreviations(page_txt):
        page_txt = page_txt.strip()
        if page_txt.find('LIST OF ABBREVIATIONS') >= 0:   # Expected text in uppercase !
            return True
        return False

    @staticmethod
    def is_bibliography(page_txt):
        page_txt = page_txt.strip()
        if (page_txt.lower().find('BIBLIOGRAPHY'.lower()) >= 0 or
            page_txt.lower().find('Bibliographie'.lower()) >= 0 or
            page_txt.find('REFERENCES') >= 0):  # Expected text in uppercase !
            return True
        return False

    @staticmethod
    def is_participants_list(page_txt):
        page_txt = page_txt.strip().lower()
        if (page_txt.find('Participants list'.lower()) >= 0 or
            page_txt.find('Liste des participants'.lower()) >=0):
            return True
        return False

    @staticmethod
    def is_annex(page_txt):
        # TODO: add logic to check that text is first on page
        page_txt = page_txt.strip()
        if page_txt.find('ANNEX') >= 0:  # Expected text in uppercase !
            return True
        return False

    @staticmethod
    def contains_table(page_txt):
        # TODO: add logic to ignore only table and not remaining text
        # TODO: add logic to ignore tables spanning several pages
        # TODO: add logic to check text is first on page
        page_txt = page_txt.strip()
        if page_txt.find('TABLE') >= 0:  # Expected text in uppercase !
            return True
        return False
