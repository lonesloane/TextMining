# -*- coding: utf8 -*-
import logging
import unittest

import pdfparser.text_extractor as extractor
from pdfparser.pdf_fragment_type import FragmentType


class TextExtractorTestCase(unittest.TestCase):

    def test_clean_fragment(self):
        fragment_text = list()
        fragment_text.append("Pays membres du Centre de développement et membres de l’OCDE : Allemagne, Autriche, Belgique, Chili, \nCorée,  Danemark,  Espagne,  Finlande,  France,  Irlande,  Islande,  Israël,  Italie,  Luxembourg,  Mexique, \nNorvège,  Pays-Bas,  Pologne,  Portugal,  République  slovaque,  République  tchèque,  Royaume-Uni,  Suède, \nSuisse et Turquie.   \n")
        fragment_text.append("3  \n")
        fragment_text.append("Pays  membres  du  Centre  de  développement  non  membres  de  l’OCDE :  Brésil  (mars  1994) ;  Inde (février \n2001) ;  Panama  (juillet  2013) ;  Roumanie  (octobre  2004) ;  Thaïlande  (mars  2005) ;  Afrique  du  Sud \n(mai 2006) ;  Égypte  et  Vietnam  (mars  2008) ;  Colombie  (juillet  2008) ;  Indonésie  (février 2009) ;  Costa \nRica,  Maurice,  Maroc  et  Pérou  (mars  2009) ;  République  dominicaine  (novembre  2009),  Sénégal  (février \n2011) ; et Argentine et Cap-Vert (mars 2011).   \n")
        fragment_text.append("L’Union européenne participe également au Comité directeur du Centre. \n")
        fragment_text.append(" \n")
        fragment_text.append("3 \n")
        fragment_text.append(" \n")
        self.assertEquals(len(fragment_text), 7)

        fragment_text = extractor.strip_page_number(fragment_text)

        self.assertEquals(len(fragment_text), 5)
        self.assertEquals(" \n", fragment_text[4])
        self.assertEquals("L’Union européenne participe également au Comité directeur du Centre. \n", fragment_text[3])

    def test_strip_cote(self):
        fragment_text = list()
        fragment_text.append(" \n")
        fragment_text.append("C(2014)151 \n")
        fragment_text.append(" \n")
        fragment_text.append(" \n")
        fragment_text.append(" \nDans un courrier au Directeur du Centre de développement (ci-après désigné le « Centre ») daté du \n21 mai  2013,  M. Emmanuel  Kalou,  Directeur  de  Cabinet  du  ministre  d´État,  ministre  des  Affaires \nétrangères de la Côte d’Ivoire, avait exprimé le souhait de son pays de rejoindre le Centre. Cette demande a \nété suivie par la participation d’une forte délégation ivoirienne conduite par le Premier Ministre, M. Daniel \nKablan Duncan, au 13e Forum économique international sur l’Afrique organisé par le Centre à Paris les 7 et \n8  octobre  2013,  puis  confirmée  par  un  courrier  de  M. Charles  Koffi  Diby,  ministre  d´État,  ministre  des \nAffaires étrangères, daté du 22 novembre 2013, qui réitérait le souhait et la demande de la Côte d’Ivoire de \ndevenir membre du Centre. Le gouvernement ivoirien espère pouvoir compter sur les acquis de l’expérience \nde  l’OCDE  pour  l’aider  à  atteindre  l’objectif  qu’il  s’est  fixé  de  faire  de  la  Côte  d’Ivoire  une  économie \némergente à l’horizon 2020. \n")

        self.assertEquals(len(fragment_text), 5)

        fragment_text = extractor.strip_cote(fragment_text)

        self.assertEquals(len(fragment_text), 3)
        self.assertEquals(" \n", fragment_text[1])
        self.assertEquals(" \nDans un courrier au Directeur du Centre de développement (ci-après désigné le « Centre ») daté du \n21 mai  2013,  M. Emmanuel  Kalou,  Directeur  de  Cabinet  du  ministre  d´État,  ministre  des  Affaires \nétrangères de la Côte d’Ivoire, avait exprimé le souhait de son pays de rejoindre le Centre. Cette demande a \nété suivie par la participation d’une forte délégation ivoirienne conduite par le Premier Ministre, M. Daniel \nKablan Duncan, au 13e Forum économique international sur l’Afrique organisé par le Centre à Paris les 7 et \n8  octobre  2013,  puis  confirmée  par  un  courrier  de  M. Charles  Koffi  Diby,  ministre  d´État,  ministre  des \nAffaires étrangères, daté du 22 novembre 2013, qui réitérait le souhait et la demande de la Côte d’Ivoire de \ndevenir membre du Centre. Le gouvernement ivoirien espère pouvoir compter sur les acquis de l’expérience \nde  l’OCDE  pour  l’aider  à  atteindre  l’objectif  qu’il  s’est  fixé  de  faire  de  la  Côte  d’Ivoire  une  économie \némergente à l’horizon 2020. \n",
                          fragment_text[2])

    @unittest.skip('deprecated method')
    def test_is_cote(self):
        cotes = list()
        cotes.append("C(2014)151 \n")
        cotes.append("EXD/INT/D(2001)30 \n")
        cotes.append("NEA/CRPPH(2001)2 \n")
        cotes.append("AGP/HR/VAC(94)5 \n")
        cotes.append("AGR/CA(94)12 \n")
        cotes.append("AGP/GRD/DOC(95)89 \n")
        cotes.append("AGP/HR/VAC(95)8 \n")
        cotes.append("AGP/CONF/D(96)65 \n")
        cotes.append("AGR/FI(97)2 \n")
        cotes.append("CTPA/CFA/WP6/NOE2(2016)3/REV2 \n")
        cotes.append("DCD/DAC/A(2016)5 \n")
        cotes.append("ENV/EPOC(2016)9 \n")
        cotes.append("ENV/WKP(2016)8 \n")
        cotes.append("CTPA/CFA/TFDE/NOE2(2015)10/REV4/CONF \n")
        cotes.append("DAF/COMP/LACF(2015)8 \n")
        cotes.append("DAF/INV/STAT/ACS/A(2015)1 \n")
        cotes.append("NEA/NDC(2015)4 \n")
        cotes.append("DAF/INV/CMF/AS/ATFC(2014)6/FINAL \n")
        cotes.append("CES/PE(2014)4 \n")
        cotes.append("DSTI/EAS/STP/NESTI(2014)11 \n")
        cotes.append("CTPA/CFA/BP/M(2013)1/REV1/CONF \n")
        cotes.append("DAF/COMP/GF/WD(2014)7 \n")
        cotes.append("TAD/PR/II(2012)5/REV \n")
        cotes.append("DELSA/ELSA(2012)9 \n")
        cotes.append("NEA/COM(2012)4 \n")
        cotes.append("GOV/TDPC/URB/A(2012)1 \n")
        cotes.append("EXD/OPS/IMSD/DOC(2012)229 \n")
        for cote in cotes:
            self.assertTrue(extractor.is_cote(cote), 'Cote not correctly identified: [{cote}]'.format(cote=cote))

        self.assertFalse(extractor.is_cote("This is not a cote"))

    def test_strip_classification(self):
        fragment_text = list()
        fragment_text.append(" \n")
        fragment_text.append("CONFIDENTIAL \n")
        fragment_text.append(" \n")
        fragment_text.append(" \n")
        fragment_text.append(" \nDans un courrier au Directeur du Centre de développement (ci-après désigné l « Centre ») daté du \n21 mai  2013,  M. Emmanuel  Kalou,  Directeur  de  Cabinet  du  ministre  d´État,  ministre  des  Affaires \nétrangères de la Côte d’Ivoire, avait exprimé le souhait de son pays de rejoindre le Centre. Cette demande a \nété suivie par la participation d’une forte délégation ivoirienne conduite par le Premier Ministre, M. Daniel \nKablan Duncan, au 13e Forum économique international sur l’Afrique organisé par le Centre à Paris les 7 et \n8  octobre  2013,  puis  confirmée  par  un  courrier  de  M. Charles  Koffi  Diby,  ministre  d´État,  ministre  des \nAffaires étrangères, daté du 22 novembre 2013, qui réitérait le souhait et la demande de la Côte d’Ivoire de \ndevenir membre du Centre. Le gouvernement ivoirien espère pouvoir compter sur les acquis de l’expérience \nde  l’OCDE  pour  l’aider  à  atteindre  l’objectif  qu’il  s’est  fixé  de  faire  de  la  Côte  d’Ivoire  une  économie \némergente à l’horizon 2020. \n")

        self.assertEquals(len(fragment_text), 5)

        fragment_text = extractor.strip_classification(fragment_text)

        self.assertEquals(len(fragment_text), 3)
        self.assertEquals(" \n", fragment_text[1])
        self.assertEquals(" \nDans un courrier au Directeur du Centre de développement (ci-après désigné l « Centre ») daté du \n21 mai  2013,  M. Emmanuel  Kalou,  Directeur  de  Cabinet  du  ministre  d´État,  ministre  des  Affaires \nétrangères de la Côte d’Ivoire, avait exprimé le souhait de son pays de rejoindre le Centre. Cette demande a \nété suivie par la participation d’une forte délégation ivoirienne conduite par le Premier Ministre, M. Daniel \nKablan Duncan, au 13e Forum économique international sur l’Afrique organisé par le Centre à Paris les 7 et \n8  octobre  2013,  puis  confirmée  par  un  courrier  de  M. Charles  Koffi  Diby,  ministre  d´État,  ministre  des \nAffaires étrangères, daté du 22 novembre 2013, qui réitérait le souhait et la demande de la Côte d’Ivoire de \ndevenir membre du Centre. Le gouvernement ivoirien espère pouvoir compter sur les acquis de l’expérience \nde  l’OCDE  pour  l’aider  à  atteindre  l’objectif  qu’il  s’est  fixé  de  faire  de  la  Côte  d’Ivoire  une  économie \némergente à l’horizon 2020. \n",
                          fragment_text[2])

    def test_re_order_text(self):
        txt = list()
        txt.append((0, 1, "0:1"))
        txt.append((1, 0, "1:0"))
        txt.append((1, 1, "1:1"))
        txt.append((2, 0, "2:0"))
        txt.append((2, 1, "2:1"))
        txt.append((-2, 2, "-2:2"))
        txt.append((0, 0, "0:0"))
        txt.append((0, 2, "0:2"))
        txt.append((1, -2, "1:-2"))
        actual = extractor.re_order_text(txt)
        expected = ['-2:2', '0:0', '0:1', '0:2', '1:-2', '1:0', '1:1', '2:0', '2:1']
        self.assertListEqual(actual, expected)

    def test_get_fragment_text(self):
        page_txt = dict()
        page_txt[(0, 1)] = "0:1"
        page_txt[(1, 0)] = "1:0"
        page_txt[(1, 1)] = "1:1"
        page_txt[(2, 0)] = "2:0"
        page_txt[(2, 1)] = "2:1"
        page_txt[(2, 2)] = "2:2"
        page_txt[(0, 0)] = "0:0"
        page_txt[(0, 2)] = "0:2"
        page_txt[(1, 2)] = "1:2"
        actual = extractor.get_fragment_text(page_txt)
        expected = ['0:2', '1:2', '2:2', '0:1', '1:1', '2:1', '0:0', '1:0', '2:0']
        self.assertListEqual(expected, actual)

    def test_get_previous_fragment_text(self):
        page_txt = dict()
        page_txt[(0, 1)] = "0:1"
        page_txt[(1, 0)] = "1:0"
        page_txt[(1, 1)] = "1:1"
        page_txt[(2, 0)] = "2:0"
        page_txt[(2, 1)] = "2:1"
        page_txt[(2, 2)] = "2:2"
        page_txt[(0, 0)] = "0:0"
        page_txt[(0, 2)] = "0:2"
        page_txt[(1, 2)] = "1:2"
        actual = extractor.get_previous_fragment_text(page_txt, (2, 0))
        expected = ['0:2', '1:2', '2:2', '0:1', '1:1', '2:1']
        self.assertListEqual(expected, actual)
        actual = extractor.get_previous_fragment_text(page_txt, (2, 1))
        expected = ['0:2', '1:2', '2:2']
        self.assertListEqual(expected, actual)
        actual = extractor.get_previous_fragment_text(page_txt, (2, 2))
        expected = []
        self.assertListEqual(expected, actual)
        actual = extractor.get_previous_fragment_text(page_txt, (2, -1))
        expected = ['0:2', '1:2', '2:2', '0:1', '1:1', '2:1', '0:0', '1:0', '2:0']
        self.assertListEqual(expected, actual)

    def test_get_next_fragment_text(self):
        page_txt = dict()
        page_txt[(0, 1)] = "0:1"
        page_txt[(1, 0)] = "1:0"
        page_txt[(1, 1)] = "1:1"
        page_txt[(2, 0)] = "2:0"
        page_txt[(2, 1)] = "2:1"
        page_txt[(2, 2)] = "2:2"
        page_txt[(0, 0)] = "0:0"
        page_txt[(0, 2)] = "0:2"
        page_txt[(1, 2)] = "1:2"
        actual = extractor.get_next_fragment_text(page_txt, (2, 0))
        expected = ['0:0', '1:0', '2:0']
        self.assertListEqual(expected, actual)
        actual = extractor.get_next_fragment_text(page_txt, (2, 1))
        expected = ['0:1', '1:1', '2:1', '0:0', '1:0', '2:0']
        self.assertListEqual(expected, actual)
        actual = extractor.get_next_fragment_text(page_txt, (2, 2))
        expected = ['0:2', '1:2', '2:2', '0:1', '1:1', '2:1', '0:0', '1:0', '2:0']
        self.assertListEqual(expected, actual)
        actual = extractor.get_next_fragment_text(page_txt, (2, -1))
        expected = []
        self.assertListEqual(expected, actual)

    @unittest.skip('Not yet implemented')
    def test_extract_object_text_hash(self):
        self.assertTrue(False)

    def test_add_fragment_debug(self):
        fragment_text = list()
        fragment_text.append("Representatives of other international organisations, including UNCTAD, UNESCO and IUCN,")
        fragment_text.append("were invited to intervene and report about their activities as appropriate during the meeting.")
        text_extractor = extractor.PDFTextExtractor()
        text_extractor.add_fragment(fragment_text, FragmentType.TEXT)
        text = text_extractor.contents[FragmentType.TEXT]
        print 'text: {t}'.format(t=text)
        self.assertEquals(1, len(text))
        self.assertEquals('Representatives of other international organisations, including UNCTAD, UNESCO and IUCN, were invited to intervene and report about their activities as appropriate during the meeting.', text[0])

    def test_add_fragment(self):
        fragment_text = list()
        fragment_text.append("A complete sentence.")
        fragment_text.append("An incomplete sentence")
        fragment_text.append("continued in the next fragment.")
        fragment_text.append("Another incomplete sentence")
        fragment_text.append("also continued. And followed by another complete sentence.")
        fragment_text.append("And the final sentence.")
        text_extractor = extractor.PDFTextExtractor()
        text_extractor.add_fragment(fragment_text, FragmentType.TEXT)
        text = text_extractor.contents[FragmentType.TEXT]
        print text
        self.assertEquals(4, len(text))
        self.assertEquals('An incomplete sentence continued in the next fragment.', text[1])
        self.assertEquals('Another incomplete sentence also continued. And followed by another complete sentence.', text[2])
        self.assertEquals('And the final sentence.', text[3])

        fragment_text.append("Should also work if the final punctuation is not a dot!!!")
        text_extractor = extractor.PDFTextExtractor()
        text_extractor.add_fragment(fragment_text, FragmentType.TEXT)
        text = text_extractor.contents[FragmentType.TEXT]
        self.assertEquals(5, len(text))
        self.assertEquals('Should also work if the final punctuation is not a dot!!!', text[4])

        fragment_text.append("Should also work if the final punctuation is not a dot...")
        text_extractor = extractor.PDFTextExtractor()
        text_extractor.add_fragment(fragment_text, FragmentType.TEXT)
        text = text_extractor.contents[FragmentType.TEXT]
        self.assertEquals(6, len(text))
        self.assertEquals('Should also work if the final punctuation is not a dot...', text[5])

        fragment_text.append("Should also work if the final punctuation is not a dot?")
        text_extractor = extractor.PDFTextExtractor()
        text_extractor.add_fragment(fragment_text, FragmentType.TEXT)
        text = text_extractor.contents[FragmentType.TEXT]
        self.assertEquals(7, len(text))
        self.assertEquals('Should also work if the final punctuation is not a dot?', text[6])
        '''
        fragment_text.append("Should also work if the final fragment is incomplete")
        text_extractor = extractor.PDFTextExtractor()
        text_extractor.add_fragment(fragment_text, FragmentType.TEXT)
        text = text_extractor.contents[FragmentType.TEXT]
        self.assertEquals(8, len(text))
        self.assertEquals('Should also work if the final fragment is incomplete', text[7])
        '''

    def test_add_fragment_over_pages(self):
        fragment_text = list()
        fragment_text.append("A complete sentence.")
        fragment_text.append("An incomplete sentence")
        fragment_text.append("continued in the next fragment.")
        fragment_text.append("Another incomplete sentence")
        fragment_text.append("also continued. And followed by another complete sentence.")
        fragment_text.append("And the last sentence")
        text_extractor = extractor.PDFTextExtractor()
        text_extractor.add_fragment(fragment_text, FragmentType.TEXT)
        text = text_extractor.contents[FragmentType.TEXT]
        print text
        self.assertEquals(3, len(text))
        self.assertEquals('Another incomplete sentence also continued. And followed by another complete sentence.', text[2])

        fragment_text = list()
        fragment_text.append("is now a complete sentence.")
        fragment_text.append("An incomplete sentence")
        fragment_text.append("continued in the next fragment.")
        text_extractor.add_fragment(fragment_text, FragmentType.TEXT)
        text = text_extractor.contents[FragmentType.TEXT]
        self.assertEquals(5, len(text))
        self.assertEquals('And the last sentence is now a complete sentence.', text[3])

    def test_validate_page(self):
        self.assertTrue(False, 'not yet implemented')

    def test_add_text_content(self):
        self.assertTrue(False, 'not yet implemented')

    def test_remove_empty_lines(self):
        self.assertTrue(False, 'not yet implemented')

    def test_strip_paragraph_numbers(self):
        self.assertTrue(False, 'not yet implemented')

    def test_strip_header(self):
        fragment_text = list()
        fragment_text.append("A complete sentence.")
        fragment_text.append("An incomplete sentence")
        fragment_text.append("continued in the next fragment.")
        fragment_text.append("Another incomplete sentence")
        fragment_text.append("also continued. And followed by another complete sentence.")
        fragment_text.append("And the last sentence")
        txt = extractor.strip_header(fragment_txt=fragment_text)
        print txt

    def test_strip_page_number(self):
        self.assertTrue(False, 'not yet implemented')

    def test_should_force_raw_extraction(self):

        pdf_extractor = extractor.PDFTextExtractor()
        expected = True
        actual = pdf_extractor.should_force_raw_extraction()
        self.assertEqual(expected, actual)

        pdf_extractor = extractor.PDFTextExtractor(single_page=1)
        expected = False
        actual = pdf_extractor.should_force_raw_extraction()
        self.assertEqual(expected, actual)

        pdf_extractor = extractor.PDFTextExtractor()
        contents = dict()
        contents[FragmentType.TEXT] = "This is the text..."
        pdf_extractor.contents = contents
        expected = False
        actual = pdf_extractor.should_force_raw_extraction()
        self.assertEqual(expected, actual)

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
    unittest.main()
