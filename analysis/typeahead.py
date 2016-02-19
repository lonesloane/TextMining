import logging
import shelve

from indexfiles.loader import TopicsIndex


class IndexBuilder:
    """Class used to build an index of N-grams required to provide type-ahead functionality

    """
    LOG_LEVEL_DEFAULT = logging.INFO

    def __init__(self, input_index_filename=None):
        """

        :param input_index_filename: Index containing the labels used to build the N-grams
        :return:
        """
        logging.basicConfig(level=IndexBuilder.LOG_LEVEL_DEFAULT,
                            format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        self._topics_index = None
        if input_index_filename is not None:
            self._topics_index = TopicsIndex(input_index_filename).index
        self._typeahead_index = dict()

    def build(self, topics_index=None, ignored_topics_ids=None):
        """Processes all english topic labels found in the index.

        Splits compound terms. Parses all individual letters and builds the index
        of all N-grams associated with the topic label

        :param topics_index:
        :param ignored_topics_ids:
        :return:
        """
        if topics_index is not None:
            self._topics_index = topics_index
        else:
            if self._topics_index is None:
                raise Exception('Invalid usage. No topics index available. Either provide an index or specify the file'
                                ' where the index is located.')

        if ignored_topics_ids is None:
            ignored_topics_ids = list()

        self.logger.info('Start building type ahead index')
        for uri, labels in self._topics_index.iteritems():

            if uri in ignored_topics_ids:
                self.logger.debug('Ignoring: %s', uri)
                continue

            lbl_en = labels[0]
            lbl_fr = labels[1]
            self.logger.debug('Processing: %s', lbl_en)
            compound = ''

            for word in lbl_en.split(' '):
                root = ''

                for letter in word:
                    root += letter

                    if root in self._typeahead_index:
                        self._typeahead_index[root].append((uri, lbl_en, lbl_fr))
                    else:
                        self._typeahead_index[root] = [(uri, lbl_en, lbl_fr)]

                    if compound != '':
                        if compound+root in self._typeahead_index:
                            self._typeahead_index[compound+root].append((uri, lbl_en, lbl_fr))
                        else:
                            self._typeahead_index[compound+root] = [(uri, lbl_en, lbl_fr)]

                compound += word+' '

        self.logger.info('Finished building type ahead index')
        return self._typeahead_index

    @staticmethod
    def extract_n_grams(labels, ignored_labels=None):
        """

        :param labels:
        :param ignored_labels:
        :return:
        """
        if ignored_labels is None:
            ignored_labels = list()
        typeahead_index = {}
        logging.getLogger(__name__).info('Start building type ahead index')

        for lbl_en in labels:

            if lbl_en in ignored_labels:
                logging.getLogger(__name__).debug('Ignoring: %s', lbl_en)
                continue

            logging.getLogger(__name__).debug('Processing: %s', lbl_en)
            compound = ''
            for word in lbl_en.split(' '):
                root = ''
                for letter in word:
                    root += letter.lower()

                    if root in typeahead_index:
                        typeahead_index[root].append(lbl_en)
                    else:
                        typeahead_index[root] = [lbl_en]

                    if compound != '':
                        if compound+root in typeahead_index:
                            typeahead_index[compound+root].append(lbl_en)
                        else:
                            typeahead_index[compound+root] = [lbl_en]
                compound += word.lower()+' '

        logging.getLogger(__name__).info('Finished building type ahead index')

        return typeahead_index

    def shelve_index(self, output_index_filename):
        """Save the index on the file system.

        :param output_index_filename:
        :return:
        """
        self.logger.info("Shelving %s", output_index_filename)
        d = shelve.open(output_index_filename)
        d["Corpus"] = self._typeahead_index
        d.close()


def main():
    """

    :return:
    """
    logging.basicConfig(filename="../output/typeahead_index_builder.log", filemode="w",
                        level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#    topics_index_filename = '../output/Topics_Index_H'
#    topics_typeahead_index_filename = '../output/Topics_Typeahead_Index_H'
    topics_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Index_H'
    topics_typeahead_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Typeahead_Index_H'
    index_builder = IndexBuilder(input_index_filename=topics_index_filename,)
    index_builder.build()
    index_builder.shelve_index(topics_typeahead_index_filename)


if __name__ == '__main__':
    main()
