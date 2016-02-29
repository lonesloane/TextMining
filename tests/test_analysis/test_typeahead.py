import logging
import os
import unittest

from analysis.typeahead import IndexBuilder
from indexfiles.loader import TopicsIndex


class IndexBuilderTestCase(unittest.TestCase):
    project_folder = os.path.abspath('/home/stephane/Playground/PycharmProjects/TextMining')

    def tearDown(self):
        typeahead_index_filename = os.path.join(IndexBuilderTestCase.project_folder,
                                                'tests/testOutput/Test_TypeAhead_Index')
        if os.path.exists(typeahead_index_filename):
            os.remove(typeahead_index_filename)

    def test_create(self):
        input_index_filename = os.path.join(IndexBuilderTestCase.project_folder,
                                            'tests/testOutput/Test_Topics_Index')
        typeahead_index_builder = IndexBuilder(input_index_filename=input_index_filename)
        self.assertTrue(isinstance(typeahead_index_builder, IndexBuilder))
        self.assertIsNotNone(typeahead_index_builder._topics_index)
        self.assertIsNotNone(typeahead_index_builder._typeahead_index)
        self.assertTrue(len(typeahead_index_builder._typeahead_index) == 0)

    def test_extract_n_grams(self):
        labels = ['Montaigne', 'Balzac', 'Rousseau', 'Baudelaire', 'Hugo',
                  'Zola', 'Flaubert', 'Chateaubriand', 'Camus']

        typeahead_index = IndexBuilder.extract_n_grams(labels)
        self.assertTrue('c' in typeahead_index)
        self.assertTrue('ca' in typeahead_index)
        self.assertTrue('cam' in typeahead_index)
        self.assertTrue('camu' in typeahead_index)
        self.assertTrue('camus' in typeahead_index)
        self.assertTrue('bal' in typeahead_index)
        self.assertTrue('bau' in typeahead_index)
        self.assertEquals(['Camus'], typeahead_index['camu'])
        self.assertEquals(['Balzac'], typeahead_index['bal'])
        self.assertEquals(['Baudelaire'], typeahead_index['bau'])

        ignored_labels = ['Camus']
        typeahead_index = IndexBuilder.extract_n_grams(labels, ignored_labels)

        self.assertTrue('c' in typeahead_index)
        self.assertFalse('ca' in typeahead_index)
        self.assertFalse('cam' in typeahead_index)
        self.assertFalse('camu' in typeahead_index)
        self.assertFalse('camus' in typeahead_index)

        self.assertTrue('b' in typeahead_index)
        self.assertTrue('ba' in typeahead_index)
        self.assertTrue('bal' in typeahead_index)
        self.assertTrue('bau' in typeahead_index)

        ignored_labels = ['Camus', 'Balzac']
        typeahead_index = IndexBuilder.extract_n_grams(labels, ignored_labels)

        self.assertTrue('b' in typeahead_index)
        self.assertTrue('ba' in typeahead_index)
        self.assertFalse('bal' in typeahead_index)
        self.assertTrue('bau' in typeahead_index)

    def test_build_missing_topics_index(self):
        index_builder = IndexBuilder()
        self.assertRaises(Exception, index_builder.build)

    def test_build_typeahead_index(self):
        input_index_filename = os.path.join(IndexBuilderTestCase.project_folder,
                                            'tests/testOutput/Topics_Index')
        typeahead_index_builder = IndexBuilder(input_index_filename=input_index_filename)

        typeahead_index = typeahead_index_builder.build()
        self.assertFalse(len(typeahead_index_builder._typeahead_index) == 0)

        # genetically modified organisms
        self.assertTrue('g' in typeahead_index)
        self.assertTrue('ge' in typeahead_index)
        self.assertTrue('gen' in typeahead_index)
        self.assertTrue('gene' in typeahead_index)
        self.assertTrue('genet' in typeahead_index)
        self.assertTrue('geneti' in typeahead_index)
        self.assertTrue('genetic' in typeahead_index)
        self.assertTrue('genetica' in typeahead_index)
        self.assertTrue('genetical' in typeahead_index)
        self.assertTrue('geneticall' in typeahead_index)
        self.assertTrue('genetically' in typeahead_index)

        self.assertTrue('m' in typeahead_index)
        self.assertTrue('mo' in typeahead_index)
        self.assertTrue('mod' in typeahead_index)
        self.assertTrue('modi' in typeahead_index)
        self.assertTrue('modi' in typeahead_index)
        self.assertTrue('modifi' in typeahead_index)
        self.assertTrue('modifie' in typeahead_index)
        self.assertTrue('modified' in typeahead_index)

        self.assertTrue('o' in typeahead_index)
        self.assertTrue('or' in typeahead_index)
        self.assertTrue('org' in typeahead_index)
        self.assertTrue('orga' in typeahead_index)
        self.assertTrue('organ' in typeahead_index)
        self.assertTrue('organi' in typeahead_index)
        self.assertTrue('organis' in typeahead_index)
        self.assertTrue('organism' in typeahead_index)
        self.assertTrue('organisms' in typeahead_index)

        actual = typeahead_index['gen']
        expected = [('5848', 'general services support estimate',
                     u"estimation du soutien aux services d'int\xe9r\xeat g\xe9n\xe9ral"),
                    ('6434', 'generally accepted accounting principles',
                     u'principes comptables g\xe9n\xe9ralement admis'),
                    ('5078', 'gender relations', 'relations entre les sexes'),
                    ('5079', 'genetic resources', u'ressources g\xe9n\xe9tiques'),
                    ('5076', 'gender analysis', u'analyse des r\xf4les sexuels'),
                    ('5077', 'gender equality', u'\xe9galit\xe9 des sexes'),
                    ('979', 'gender discrimination', u'discrimination fond\xe9e sur le sexe'),
                    ('2073', 'power generation', u"production d'\xe9nergie"),
                    ('3204', 'gender roles', u'r\xf4les sexuels'), ('3816', 'conflict of generations',
                                                                    u'conflit de g\xe9n\xe9rations'),
                    ('1206', 'genealogy', u'g\xe9n\xe9alogie'), ('5103', 'income generation',
                                                                 u'cr\xe9ation de revenu'),
                    ('6053', 'gender mainstreaming', u"int\xe9gration des questions d'\xe9galit\xe9 hommes-femmes"),
                    ('6605', 'electricity generation', u"production d'\xe9lectricit\xe9"),
                    ('4694', 'genes', u'g\xe8nes'), ('5951', 'general administrative management',
                                                     u'gestion administrative g\xe9n\xe9rale'),
                    ('1632', 'genetic improvement', u'am\xe9lioration g\xe9n\xe9tique'),
                    ('5626', 'waste generation', u'production de d\xe9chets'),
                    ('1628', 'plant genetics', u'phytog\xe9n\xe9tique'),
                    ('1318', 'general education', u'enseignement g\xe9n\xe9ral'),
                    ('4078', 'human genetics', u'g\xe9n\xe9tique humaine'), ('1732', 'animal genetics',
                                                                             u'g\xe9n\xe9tique animale'),
                    ('3184', 'genetic engineering', u'g\xe9nie g\xe9n\xe9tique'), ('3183', 'genetics',
                                                                                   u'g\xe9n\xe9tique'),
                    ('6300', 'gender inequality', u'in\xe9galit\xe9 des sexes'),
                    ('5525', 'general equilibrium models', u"mod\xe8les d'\xe9quilibre g\xe9n\xe9ral"),
                    ('6152', 'gender pay gap', u'in\xe9galit\xe9 de revenus salariaux entre hommes et femmes'),
                    ('6341', 'general practitioners', u'm\xe9decins g\xe9n\xe9ralistes'),
                    ('6380', 'combined heat and power generation',
                     u"production conjointe de chaleur et d'\xe9lectricit\xe9"),
                    ('4686', 'generations', u'g\xe9n\xe9rations'), ('4688', 'genocide', u'g\xe9nocide'),
                    ('6583', 'genetically modified organisms', u'organismes g\xe9n\xe9tiquement modifi\xe9s')]
        self.assertItemsEqual(expected, actual)
        self.assertTrue(('6583', 'genetically modified organisms', u'organismes g\xe9n\xe9tiquement modifi\xe9s')
                        in actual)

        actual = typeahead_index['mod']
        expected = [('2031', 'modular construction', 'construction modulaire'), ('796', 'growth models',
                                                                                 u'mod\xe8les de croissance'),
                    ('5937', 'financial modelling', u'mod\xe9lisation financi\xe8re'), ('880', 'modes of production',
                                                                                        'modes de production'),
                    ('765', 'economic models', u'mod\xe8les \xe9conomiques'),
                    ('5851', 'policy evaluation model', u"mod\xe8le d'\xe9valuation des politiques"),
                    ('5996', 'aid modalities', u"modalit\xe9s de l'aide"),
                    ('785', 'global models', u'mod\xe8les mondiaux'), ('787', 'national models',
                                                                       u'mod\xe8les nationaux'),
                    ('2479', 'modes of transport', 'modes de transport'),
                    ('5525', 'general equilibrium models', u"mod\xe8les d'\xe9quilibre g\xe9n\xe9ral"),
                    ('5475', 'economic modelling', u'mod\xe9lisation \xe9conomique'),
                    ('4096', 'modern languages', 'langues vivantes'), ('613', 'modernisation', 'modernisation'),
                    ('770', 'econometric models', u'mod\xe8les \xe9conom\xe9triques'),
                    ('3559', 'mathematical models', u'mod\xe8les math\xe9matiques'),
                    ('6583', 'genetically modified organisms', u'organismes g\xe9n\xe9tiquement modifi\xe9s'),
                    ('5497', 'environmental modelling', u'mod\xe9lisation environnementale')]
        self.assertItemsEqual(expected, actual)
        self.assertTrue(('6583', 'genetically modified organisms', u'organismes g\xe9n\xe9tiquement modifi\xe9s')
                        in actual)

        actual = typeahead_index['org']
        self.assertTrue(('6583', 'genetically modified organisms', u'organismes g\xe9n\xe9tiquement modifi\xe9s')
                        in actual)

        actual = typeahead_index['anim']
        self.assertTrue(('3562', 'animal research', u'recherche animali\xe8re') in actual)
        actual = typeahead_index['resea']
        self.assertTrue(('3562', 'animal research', u'recherche animali\xe8re') in actual)

    def test_ignore_uris(self):
        input_index_filename = os.path.join(IndexBuilderTestCase.project_folder,
                                            'tests/testOutput/Topics_Index')
        topics_index = TopicsIndex(input_index_filename).index
        typeahead_index_builder = IndexBuilder(input_index_filename=input_index_filename)

        typeahead_index = typeahead_index_builder.build(topics_index=topics_index,
                                                        ignored_topics_ids=['6583', '1632'])
        self.assertFalse(len(typeahead_index_builder._typeahead_index) == 0)

        actual = typeahead_index['gen']
        expected = [('5848', 'general services support estimate',
                     u"estimation du soutien aux services d'int\xe9r\xeat g\xe9n\xe9ral"),
                    ('6434', 'generally accepted accounting principles',
                     u'principes comptables g\xe9n\xe9ralement admis'),
                    ('5078', 'gender relations', 'relations entre les sexes'),
                    ('5079', 'genetic resources', u'ressources g\xe9n\xe9tiques'),
                    ('5076', 'gender analysis', u'analyse des r\xf4les sexuels'),
                    ('5077', 'gender equality', u'\xe9galit\xe9 des sexes'),
                    ('979', 'gender discrimination', u'discrimination fond\xe9e sur le sexe'),
                    ('2073', 'power generation', u"production d'\xe9nergie"),
                    ('3204', 'gender roles', u'r\xf4les sexuels'), ('3816', 'conflict of generations',
                                                                    u'conflit de g\xe9n\xe9rations'),
                    ('1206', 'genealogy', u'g\xe9n\xe9alogie'), ('5103', 'income generation',
                                                                 u'cr\xe9ation de revenu'),
                    ('6053', 'gender mainstreaming', u"int\xe9gration des questions d'\xe9galit\xe9 hommes-femmes"),
                    ('6605', 'electricity generation', u"production d'\xe9lectricit\xe9"),
                    ('4694', 'genes', u'g\xe8nes'), ('5951', 'general administrative management',
                                                     u'gestion administrative g\xe9n\xe9rale'),
                    ('5626', 'waste generation', u'production de d\xe9chets'),
                    ('1628', 'plant genetics', u'phytog\xe9n\xe9tique'),
                    ('1318', 'general education', u'enseignement g\xe9n\xe9ral'),
                    ('4078', 'human genetics', u'g\xe9n\xe9tique humaine'), ('1732', 'animal genetics',
                                                                             u'g\xe9n\xe9tique animale'),
                    ('3184', 'genetic engineering', u'g\xe9nie g\xe9n\xe9tique'), ('3183', 'genetics',
                                                                                   u'g\xe9n\xe9tique'),
                    ('6300', 'gender inequality', u'in\xe9galit\xe9 des sexes'),
                    ('5525', 'general equilibrium models', u"mod\xe8les d'\xe9quilibre g\xe9n\xe9ral"),
                    ('6152', 'gender pay gap', u'in\xe9galit\xe9 de revenus salariaux entre hommes et femmes'),
                    ('6341', 'general practitioners', u'm\xe9decins g\xe9n\xe9ralistes'),
                    ('6380', 'combined heat and power generation',
                     u"production conjointe de chaleur et d'\xe9lectricit\xe9"),
                    ('4686', 'generations', u'g\xe9n\xe9rations'), ('4688', 'genocide', u'g\xe9nocide')]
        self.assertItemsEqual(expected, actual)
        self.assertFalse(('6583', 'genetically modified organisms', u'organismes g\xe9n\xe9tiquement modifi\xe9s')
                         in actual)
        self.assertFalse(('1632', 'genetic improvement', u'am\xe9lioration g\xe9n\xe9tique') in actual)

    def test_compound_words(self):
        input_index_filename = os.path.join(IndexBuilderTestCase.project_folder,
                                            'tests/testOutput/Topics_Index')
        typeahead_index_builder = IndexBuilder(input_index_filename=input_index_filename)

        typeahead_index = typeahead_index_builder.build()
        # gross domestic expenditure on research and development
        actual = typeahead_index['gros']
        expected = ('6622', 'gross domestic expenditure on research and development',
                    u'd\xe9pense int\xe9rieure brute de recherche et d\xe9veloppement')
        self.assertTrue(expected in actual)
        actual = typeahead_index['domes']
        self.assertTrue(expected in actual)
        actual = typeahead_index['expen']
        self.assertTrue(expected in actual)
        actual = typeahead_index['resea']
        self.assertTrue(expected in actual)
        actual = typeahead_index['devel']
        self.assertTrue(expected in actual)
        actual = typeahead_index['gross dom']
        self.assertTrue(expected in actual)

    def test_shelve_index(self):
        input_index_filename = os.path.join(IndexBuilderTestCase.project_folder,
                                            'tests/testOutput/Test_Topics_Index')
        output_index_filename = os.path.join(IndexBuilderTestCase.project_folder,
                                             'tests/testOutput/Test_TypeAhead_Index')

        self.assertFalse(os.path.isfile(output_index_filename))
        IndexBuilder(input_index_filename=input_index_filename).shelve_index(output_index_filename)
        self.assertTrue(os.path.isfile(output_index_filename))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
    unittest.main()
