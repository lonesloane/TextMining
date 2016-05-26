# -*- coding: utf8 -*-

import logging
import unittest
import pdfparser.text_extractor as extractor


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
        fragment_text.append(" \nDans un courrier au Directeur du Centre de développement (ci-après désigné l « Centre ») daté du \n21 mai  2013,  M. Emmanuel  Kalou,  Directeur  de  Cabinet  du  ministre  d´État,  ministre  des  Affaires \nétrangères de la Côte d’Ivoire, avait exprimé le souhait de son pays de rejoindre le Centre. Cette demande a \nété suivie par la participation d’une forte délégation ivoirienne conduite par le Premier Ministre, M. Daniel \nKablan Duncan, au 13e Forum économique international sur l’Afrique organisé par le Centre à Paris les 7 et \n8  octobre  2013,  puis  confirmée  par  un  courrier  de  M. Charles  Koffi  Diby,  ministre  d´État,  ministre  des \nAffaires étrangères, daté du 22 novembre 2013, qui réitérait le souhait et la demande de la Côte d’Ivoire de \ndevenir membre du Centre. Le gouvernement ivoirien espère pouvoir compter sur les acquis de l’expérience \nde  l’OCDE  pour  l’aider  à  atteindre  l’objectif  qu’il  s’est  fixé  de  faire  de  la  Côte  d’Ivoire  une  économie \némergente à l’horizon 2020. \n")

        self.assertEquals(len(fragment_text), 5)

        fragment_text = extractor.strip_cote(fragment_text)

        self.assertEquals(len(fragment_text), 3)
        self.assertEquals(" \n", fragment_text[1])
        self.assertEquals(" \nDans un courrier au Directeur du Centre de développement (ci-après désigné l « Centre ») daté du \n21 mai  2013,  M. Emmanuel  Kalou,  Directeur  de  Cabinet  du  ministre  d´État,  ministre  des  Affaires \nétrangères de la Côte d’Ivoire, avait exprimé le souhait de son pays de rejoindre le Centre. Cette demande a \nété suivie par la participation d’une forte délégation ivoirienne conduite par le Premier Ministre, M. Daniel \nKablan Duncan, au 13e Forum économique international sur l’Afrique organisé par le Centre à Paris les 7 et \n8  octobre  2013,  puis  confirmée  par  un  courrier  de  M. Charles  Koffi  Diby,  ministre  d´État,  ministre  des \nAffaires étrangères, daté du 22 novembre 2013, qui réitérait le souhait et la demande de la Côte d’Ivoire de \ndevenir membre du Centre. Le gouvernement ivoirien espère pouvoir compter sur les acquis de l’expérience \nde  l’OCDE  pour  l’aider  à  atteindre  l’objectif  qu’il  s’est  fixé  de  faire  de  la  Côte  d’Ivoire  une  économie \némergente à l’horizon 2020. \n",
                          fragment_text[2])

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
        cotes.append("CONFIDENTIAL  CTPA/CFA/BP/M(2013)1/REV1/CONF \n")
        cotes.append("DAF/COMP/GF/WD(2014)7 \n")
        cotes.append("TAD/PR/II(2012)5/REV \n")
        cotes.append("DELSA/ELSA(2012)9 \n")
        cotes.append("NEA/COM(2012)4 \n")
        cotes.append("GOV/TDPC/URB/A(2012)1 \n")
        cotes.append("EXD/OPS/IMSD/DOC(2012)229 \n")
        for cote in cotes:
            print 'Testing cote:{cote}'.format(cote=cote)
            self.assertTrue(extractor.is_cote(cote), 'Cote not correctly identified: [{cote}]'.format(cote=cote))

        self.assertFalse(extractor.is_cote("This is not a cote"))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
    unittest.main()
