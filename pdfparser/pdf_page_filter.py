# -*- coding: utf8 -*-
import logging


class PDFPageFilter:

    def __init__(self):
        pass

    @staticmethod
    def is_cover(page_txt):
        for coord, fragment in page_txt:
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
        for coord, fragment in page_txt:
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
        for coord, fragment in page_txt:
            fragment = fragment.strip()
            if (fragment.find('LIST OF ABBREVIATIONS') >= 0 or
                fragment.find('GLOSSARY') >= 0):   # Expected text in uppercase !
                return True
        return False

    @staticmethod
    def is_bibliography(page_txt):
        for coord, fragment in page_txt:
            fragment = fragment.strip()
            if (fragment.lower().find('BIBLIOGRAPHY'.lower()) >= 0 or
                fragment.lower().find('Bibliographie'.lower()) >= 0 or
                fragment == 'REFERENCES'):  # Expected text in uppercase as unique word of sentence
                return True
        return False

    @staticmethod
    def is_participants_list(page_txt):
        for coord, fragment in page_txt:
            fragment = fragment.strip().lower()
            if (fragment.find('Participants list'.lower()) >= 0 or
                fragment.find('Liste des participants'.lower()) >=0):
                return True
        return False

    @staticmethod
    def is_annex(page_txt):
        ###
        # Expect to find word 'ANNEX' (in upper case) as first word of sentence, top of the page
        ###
        # TODO: add logic to check that text is first on page
        for coord, fragment in page_txt:
            fragment = fragment.strip()
            if fragment.rfind('ANNEX') == 0:  # Expected text in uppercase !
                return True
        return False

    @staticmethod
    def contains_table(page_txt):
        # TODO: add logic to ignore only table and not remaining text
        # TODO: add logic to ignore tables spanning several pages
        # TODO: add logic to check text is first on page
        for coord, fragment in page_txt:
            fragment = fragment.strip()
            # TODO: remove this ridiculous test...
            if fragment.find('TABLE') >= 0:  # Expected text in uppercase !
                return True
        return False
