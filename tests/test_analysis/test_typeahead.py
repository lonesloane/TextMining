import os
import unittest

from analysis.typeahead import IndexBuilder


class IndexBuilderTestCase(unittest.TestCase):
    def tearDown(self):
        typeahead_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_TypeAhead_Index'
        if os.path.exists(typeahead_index_filename):
            os.remove(typeahead_index_filename)

    def test_create(self):
        input_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Index'
        output_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_TypeAhead_Index'
        typeahead_index_builder = IndexBuilder(input_index_filename=input_index_filename,
                                               output_index_filename=output_index_filename)
        self.assertTrue(isinstance(typeahead_index_builder, IndexBuilder))
        self.assertIsNotNone(typeahead_index_builder._topics_index)
        print typeahead_index_builder._topics_index
        self.assertIsNotNone(typeahead_index_builder.index)
        self.assertTrue(len(typeahead_index_builder.index) == 0)

    def test_extract_n_grams(self):
        labels = ['Montaigne', 'Balzac', 'Rousseau', 'Baudelaire', 'Hugo', 'Zola', 'Flaubert', 'Chateaubriand', 'Camus']

        typeahead_index = IndexBuilder.extract_n_grams(labels)
        self.assertTrue('c' in typeahead_index)
        self.assertTrue('ca' in typeahead_index)
        self.assertTrue('cam' in typeahead_index)
        self.assertTrue('camu' in typeahead_index)
        self.assertTrue('camus' in typeahead_index)
        self.assertTrue('bal' in typeahead_index)
        self.assertTrue('bau' in typeahead_index)

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

    def test_build_typeahead_index(self):
        input_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Topics_Index'
        output_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_TypeAhead_Index'
        typeahead_index_builder = IndexBuilder(input_index_filename=input_index_filename,
                                               output_index_filename=output_index_filename)

        typeahead_index_builder.build()
        self.assertFalse(len(typeahead_index_builder.index) == 0)

        # genetically modified organisms
        self.assertTrue('g' in typeahead_index_builder.index)
        self.assertTrue('ge' in typeahead_index_builder.index)
        self.assertTrue('gen' in typeahead_index_builder.index)
        self.assertTrue('gene' in typeahead_index_builder.index)
        self.assertTrue('genet' in typeahead_index_builder.index)
        self.assertTrue('geneti' in typeahead_index_builder.index)
        self.assertTrue('genetic' in typeahead_index_builder.index)
        self.assertTrue('genetica' in typeahead_index_builder.index)
        self.assertTrue('genetical' in typeahead_index_builder.index)
        self.assertTrue('geneticall' in typeahead_index_builder.index)
        self.assertTrue('genetically' in typeahead_index_builder.index)

        self.assertTrue('m' in typeahead_index_builder.index)
        self.assertTrue('mo' in typeahead_index_builder.index)
        self.assertTrue('mod' in typeahead_index_builder.index)
        self.assertTrue('modi' in typeahead_index_builder.index)
        self.assertTrue('modi' in typeahead_index_builder.index)
        self.assertTrue('modifi' in typeahead_index_builder.index)
        self.assertTrue('modifie' in typeahead_index_builder.index)
        self.assertTrue('modified' in typeahead_index_builder.index)

        self.assertTrue('o' in typeahead_index_builder.index)
        self.assertTrue('or' in typeahead_index_builder.index)
        self.assertTrue('org' in typeahead_index_builder.index)
        self.assertTrue('orga' in typeahead_index_builder.index)
        self.assertTrue('organ' in typeahead_index_builder.index)
        self.assertTrue('organi' in typeahead_index_builder.index)
        self.assertTrue('organis' in typeahead_index_builder.index)
        self.assertTrue('organism' in typeahead_index_builder.index)
        self.assertTrue('organisms' in typeahead_index_builder.index)

        actual = typeahead_index_builder.index['gen']
        expected = ['general services support estimate', 'generally accepted accounting principles',
                    'gender relations', 'genetic resources', 'gender analysis', 'gender equality',
                    'gender discrimination', 'power generation', 'gender roles', 'conflict of generations',
                    'genealogy', 'income generation', 'gender mainstreaming', 'electricity generation', 'genes',
                    'general administrative management', 'genetic improvement', 'waste generation', 'plant genetics',
                    'general education', 'human genetics', 'animal genetics', 'genetic engineering', 'genetics',
                    'gender inequality', 'general equilibrium models', 'gender pay gap', 'general practitioners',
                    'combined heat and power generation', 'generations', 'genocide', 'genetically modified organisms']
        self.assertItemsEqual(expected, actual)
        self.assertTrue('genetically modified organisms' in actual)

        actual = typeahead_index_builder.index['mod']
        expected = ['modular construction', 'growth models', 'financial modelling', 'modes of production',
                    'economic models', 'policy evaluation model', 'aid modalities', 'global models', 'national models',
                    'modes of transport', 'general equilibrium models', 'economic modelling', 'modern languages',
                    'modernisation', 'econometric models', 'mathematical models', 'genetically modified organisms',
                    'environmental modelling']
        self.assertItemsEqual(expected, actual)
        self.assertTrue('genetically modified organisms' in actual)

        actual = typeahead_index_builder.index['org']
        expected = ['American organisations', 'European organisations', 'organisation of learning',
                    'intergovernmental organisations', 'international nongovernmental organisations',
                    'learning organisations', 'Arab organisations', 'Asian organisations', 'business organisation',
                    'organisational effectiveness', 'organic food production', 'organic food consumption',
                    'voluntary organisations', 'youth organisations', 'nonprofit organisations',
                    'volatile organic compounds', 'multilateral organisations', 'factory organisation',
                    'organisational change', 'organisational structure', 'environmental non-governmental organisations',
                    'organisational development', 'civil society organisations enabling environment',
                    'civil society organisations', 'organisation of research', 'occupational organisations',
                    'organic farming', 'organic chemistry', 'international organisations',
                    'nongovernmental organisations', 'organisation theory', "employers' organisations",
                    "women's organisations", 'regional organisations', 'work organisation', 'organic compounds',
                    'organic foods', 'commodity organisations', 'neighbourhood organisations', 'organised crime',
                    'African organisations', 'genetically modified organisms', "workers' organisations",
                    'peasant organisations']
        self.assertItemsEqual(expected, actual)
        self.assertTrue('genetically modified organisms' in actual)

        actual = typeahead_index_builder.index['anim']
        self.assertTrue('animal research' in actual)
        actual = typeahead_index_builder.index['resea']
        self.assertTrue('animal research' in actual)

    def test_compound_words(self):
        input_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Topics_Index'
        output_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_TypeAhead_Index'
        typeahead_index_builder = IndexBuilder(input_index_filename=input_index_filename,
                                               output_index_filename=output_index_filename)

        typeahead_index_builder.build()
        # gross domestic expenditure on research and development
        actual = typeahead_index_builder.index['gros']
        self.assertTrue('gross domestic expenditure on research and development' in actual)
        actual = typeahead_index_builder.index['domes']
        self.assertTrue('gross domestic expenditure on research and development' in actual)
        actual = typeahead_index_builder.index['expen']
        self.assertTrue('gross domestic expenditure on research and development' in actual)
        actual = typeahead_index_builder.index['resea']
        self.assertTrue('gross domestic expenditure on research and development' in actual)
        actual = typeahead_index_builder.index['devel']
        self.assertTrue('gross domestic expenditure on research and development' in actual)
        actual = typeahead_index_builder.index['gross dom']
        self.assertTrue('gross domestic expenditure on research and development' in actual)

    def test_shelve_index(self):
        self.assertFalse(os.path.isfile('/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_TypeAhead_Index'))
        input_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Index'
        output_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_TypeAhead_Index'
        IndexBuilder(input_index_filename=input_index_filename,
                     output_index_filename=output_index_filename).shelve_index()
        self.assertTrue(os.path.isfile('/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_TypeAhead_Index'))


if __name__ == '__main__':
    unittest.main()
