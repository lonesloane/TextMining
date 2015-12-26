import shelve
import logging

LOG_LEVEL = logging.INFO


class Index:
    def __init__(self, index_filename):
        logging.basicConfig(level=LOG_LEVEL, format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        self._index = None
        if index_filename is None or len(index_filename) == 0:
            raise Exception("No valid index filename provided. Cannot load index")
        self._index_filename = index_filename

        self._load_index()

    def _load_index(self):
        self.logger.info("Loading index %s", self._index_filename)
        d = shelve.open(self._index_filename)
        self._index = d["Corpus"]
        d.close()
        self.logger.info("Index loaded successfully")


class FilesIndex(Index):
    default_index_filename = "../output/Files_Index"

    def __init__(self, index_filename=None):
        if index_filename is None:
            index_filename = FilesIndex.default_index_filename
        Index.__init__(self, index_filename)

    def get_topics_for_files(self, target_file):
        self.logger.debug("Looking for topics in file: %s" % target_file)
        result_topics = []
        result_topics.extend([t for t, _ in self._index[target_file]])
        return sorted(result_topics)

    def get_enrichment_for_files(self, target_file):
        self.logger.debug("Looking for semantic enrichment in file: %s" % target_file)
        return self._index[target_file]


class TopicsIndex(Index):
    default_index_filename = "../output/Topics_Index"

    def __init__(self, index_filename=None):
        if index_filename is None:
            index_filename = TopicsIndex.default_index_filename
        Index.__init__(self, index_filename)

    def get_labels_for_topic_id(self, topic_id):
        return self._index[topic_id]


class TopicsOccurrencesIndex(Index):
    default_index_filename = "../output/Topics_Occurrences_Index"

    def __init__(self, index_filename=None):
        if index_filename is None:
            index_filename = TopicsOccurrencesIndex.default_index_filename
        Index.__init__(self, index_filename)

    def get_files_for_topic(self, topic):
        return self._index[topic]


class TopicsLabelsIndex(Index):
    default_index_filename = "../output/Topics_Labels_Index"

    def __init__(self, index_filename=None):
        if index_filename is None:
            index_filename = TopicsLabelsIndex.default_index_filename
        Index.__init__(self, index_filename)

    def get_topic_id_for_label(self, target_topic):
        return self._index[target_topic]