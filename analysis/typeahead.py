import logging
import shelve

from index.loader import TopicsIndex


class IndexBuilder:
    """Class used to build an index of N-grams required to provide type-ahead functionality

    Usage::

        >>> from analysis.typeahead import IndexBuilder
        >>> index_builder = IndexBuilder(input_index_filename, output_index_filename)
        >>> index = index_builder.build().index
    """
    LOG_LEVEL_DEFAULT = logging.INFO

    def __init__(self, input_index_filename, output_index_filename):
        """

        :param input_index_filename: Index containing the labels used to build the N-grams
        :param output_index_filename: Complete file name where the type-ahead index will be saved
        :return:
        """
        logging.basicConfig(level=IndexBuilder.LOG_LEVEL_DEFAULT,
                            format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        self._topics_index = TopicsIndex(input_index_filename).index
        self._typeahead_index_filename = output_index_filename
        self._typeahead_index = dict()

    @property
    def index(self):
        return self._typeahead_index

    def build(self):
        """
        Processes all english topic labels found in the index.
        Splits compound terms. Parses all individual letters and builds the index
        of all N-grams associated with the topic label

        :return:
        """
        self.logger.info('Start building type ahead index')
        for lbl_en, _ in self._topics_index.values():
            self.logger.debug('Processing: %s', lbl_en)
            compound = ''
            for word in lbl_en.split(' '):
                root = ''
                for letter in word:
                    root += letter
                    if root in self._typeahead_index:
                        self._typeahead_index[root].append(lbl_en)
                    else:
                        self._typeahead_index[root] = [lbl_en]
                    if compound != '':
                        if compound+root in self._typeahead_index:
                            self._typeahead_index[compound+root].append(lbl_en)
                        else:
                            self._typeahead_index[compound+root] = [lbl_en]
                compound += word+' '

        self.logger.info('Finished building type ahead index')
        return self

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

    def shelve_index(self):
        """
        Save the index on the file system.

        :return:
        """
        self.logger.info("Shelving %s", self._typeahead_index_filename)
        d = shelve.open(self._typeahead_index_filename)
        d["Corpus"] = self._typeahead_index
        d.close()


def main():
    logging.basicConfig(filename="../output/typeahead_index_builder.log", filemode="w",
                        level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#     topics_index_filename = '../output/Topics_Index'
#     topics_typeahead_index_filename = '../output/Topics_Typeahead_Index'
    topics_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Index'
    topics_typeahead_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Typeahead_Index'
    IndexBuilder(input_index_filename=topics_index_filename,
                 output_index_filename=topics_typeahead_index_filename).build().shelve_index()


if __name__ == '__main__':
    main()
