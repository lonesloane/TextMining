import shelve
import logging

LOG_LEVEL = logging.INFO


class Index:
    """Base class for all index objects.

    """
    def __init__(self, index_filename):
        """


        :param index_filename: Complete path to the file containing the index
        :return:
        """
        logging.basicConfig(level=LOG_LEVEL, format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        self._index = None
        if index_filename is None or len(index_filename) == 0:
            raise Exception("No valid index filename provided. Cannot load index")
        self._index_filename = index_filename

        self._load_index()

    def _load_index(self):
        """Loads index from file system.

        :return:
        """
        self.logger.info("Loading index %s", self._index_filename)
        d = shelve.open(self._index_filename)
        self._index = d["Corpus"]
        d.close()
        self.logger.info("Index loaded successfully")

    @property
    def index(self):
        """

        :return:
        """
        if self._index is None:
            self._load_index()
        return self._index


class FilesIndex(Index):
    """

    """
    default_index_filename = "../output/Files_Index"

    def __init__(self, index_filename=None):
        """

        :param index_filename:
        :return:
        """
        if index_filename is None:
            index_filename = FilesIndex.default_index_filename
        Index.__init__(self, index_filename)

    def get_topics_for_files(self, target_file):
        """

        :param target_file:
        :return: sorted list of topics
        """
        self.logger.debug("Looking for topics in file: %s" % target_file)
        result_topics = []
        result_topics.extend([t for t, _ in self._index[target_file]])
        return sorted(result_topics)

    def get_enrichment_for_files(self, target_file):
        """

        :param target_file:
        :return:
        """
        self.logger.debug("Looking for semantic enrichment in file: %s" % target_file)
        return self._index[target_file]


class FilesDatesIndex(Index):
    """

    """
    default_index_filename = "../output/Files_Dates_Index"

    def __init__(self, index_filename=None):
        if index_filename is None:
            index_filename = FilesDatesIndex.default_index_filename
        Index.__init__(self, index_filename)

    def get_date_for_file(self, target_file):
        """

        :param target_file:
        :return: sorted list of topics
        """
        self.logger.debug("Looking for date for file: %s" % target_file)
        return self.index[target_file]


class TopicsIndex(Index):
    """

    """
    default_index_filename = "../output/Topics_Index"

    def __init__(self, index_filename=None):
        logging.basicConfig(level=LOG_LEVEL, format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        if index_filename is None:
            index_filename = TopicsIndex.default_index_filename
        Index.__init__(self, index_filename)

    def get_labels_for_topic_id(self, topic_id):
        """

        :param topic_id:
        :return:
        """
        return self._index[topic_id]

    def get_topic_for_topic_id(self, topic_id):
        topic_labels = self._index[topic_id]
        topic = dict()
        topic['id'] = topic_id
        labels = dict()
        labels['en'] = topic_labels[0]
        labels['fr'] = topic_labels[1]
        topic['label'] = labels
        self.logger.debug('topic: %s', topic)
        return topic


class TopicsOccurrencesIndex(Index):
    """

    """
    default_index_filename = "../output/Topics_Occurrences_Index"

    def __init__(self, index_filename=None):
        if index_filename is None:
            index_filename = TopicsOccurrencesIndex.default_index_filename
        Index.__init__(self, index_filename)

    def get_files_for_topic(self, topic):
        """

        :param topic:
        :return:
        """
        return self._index[topic]


class TopicsLabelsIndex(Index):
    """

    """
    default_index_filename = "../output/Topics_Labels_Index"

    def __init__(self, index_filename=None):
        if index_filename is None:
            index_filename = TopicsLabelsIndex.default_index_filename
        Index.__init__(self, index_filename)

    def get_topic_id_for_label(self, target_topic):
        """

        :param target_topic:
        :return:
        """
        return self._index[target_topic]


class TopicsTypeAheadIndex(Index):
    """

    """
    default_index_filename = "../output/Topics_Typeahead_Index"

    def __init__(self, index_filename=None):
        if index_filename is None:
            index_filename = TopicsTypeAheadIndex.default_index_filename
        Index.__init__(self, index_filename)

    def auto_complete(self, root):
        """

        :param root:
        :return:
        """
        return self._index[root]


def main():
    pass

if __name__ == '__main__':
    main()
