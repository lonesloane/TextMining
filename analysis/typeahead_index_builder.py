import logging
import shelve

from index.loader import TopicsIndex


class TypeAheadIndexBuilder:
    LOG_LEVEL_DEFAULT = logging.INFO

    def __init__(self, input_index_filename, output_index_filename):
        logging.basicConfig(level=TypeAheadIndexBuilder.LOG_LEVEL_DEFAULT,
                            format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        self._topics_index = TopicsIndex(input_index_filename).index
        self._typeahead_index_filename = output_index_filename
        self._typeahead_index = dict()

    @property
    def index(self):
        return self._typeahead_index

    def build(self):
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

    def shelve_index(self):
        # save the index on the file system
        self.logger.info("Shelving %s", self._typeahead_index_filename)
        d = shelve.open(self._typeahead_index_filename)
        d["Corpus"] = self._typeahead_index
        d.close()


def main():
    logging.basicConfig(filename="../output/typeahead_index_builder.log", filemode="w",
                        level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    topics_index_filename = '../output/Topics_Index'
    topics_typeahead_index_filename = '../output/Topics_Typeahead_Index'
    TypeAheadIndexBuilder(input_index_filename=topics_index_filename,
                          output_index_filename=topics_typeahead_index_filename).build().shelve_index()


if __name__ == '__main__':
    main()