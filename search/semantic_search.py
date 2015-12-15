# region imports

# end region
import logging
import shelve

LOG_LEVEL = logging.INFO


class QueryProcessor:
    _files_index_filename_default = "../output/Files_Index"
    _topics_occurrences_index_filename_default = "../output/Topics_Occurrences_Index"
    """

    """
    def __init__(self, files_index_filename=None, topics_occurrences_index_filename=None):

        self._topics_occurrences_index = None
        self._files_index = None

        logging.basicConfig(level=LOG_LEVEL, format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        self._files_index_filename = files_index_filename if files_index_filename is not None \
            else QueryProcessor._files_index_filename_default
        self.logger.debug("Files Index: %s", self._files_index_filename)

        self._topics_occurrences_index_filename = topics_occurrences_index_filename \
            if topics_occurrences_index_filename is not None \
            else QueryProcessor._topics_occurrences_index_filename_default
        self.logger.debug("Topics Occurrences Index: %s", self._topics_occurrences_index_filename)

        self.load_files_index()
        self.load_topics_occurrences_index()

    def load_files_index(self):
        self.logger.info("Loading files index from %s", self._files_index_filename)

        d = shelve.open(self._files_index_filename)
        self._files_index = d["Corpus"]
        d.close()


    def load_topics_occurrences_index(self):
        self.logger.info("Loading topics index from %s", self._topics_occurrences_index_filename)

        d = shelve.open(self._topics_occurrences_index_filename)
        self._topics_occurrences_index = d["Corpus"]
        d.close()
