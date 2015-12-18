# region imports

# end region
import logging
import shelve

LOG_LEVEL = logging.INFO


class QueryProcessor:
    _files_index_filename_default = "../output/Files_Index"
    _topics_occurrences_index_filename_default = "../output/Topics_Occurrences_Index"
    _topics_labels_index_filename_default = "../output/Topics_Labels_Index"

    def __init__(self, files_index_filename=None, topics_occurrences_index_filename=None,
                 topics_labels_index_filename=None):
        """
        :param files_index_filename: file containing the index of topics per file. Default 'output/Files_Index'
        :param topics_occurrences_index_filename: file containing the index of files per topic. Default
        'output/Topics_Occurrences_Index'
        :param topics_labels_index_filename: file containing the index of topic ids per topic label. Default
        'output/Topics_Labels_Index'
        """
        self._topics_occurrences_index = None
        self._files_index = None
        self._topics_labels_index = None

        logging.basicConfig(level=LOG_LEVEL, format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        self._files_index_filename = files_index_filename if files_index_filename is not None \
            else QueryProcessor._files_index_filename_default
        self.logger.debug("Files Index: %s", self._files_index_filename)

        self._topics_occurrences_index_filename = topics_occurrences_index_filename \
            if topics_occurrences_index_filename is not None \
            else QueryProcessor._topics_occurrences_index_filename_default
        self.logger.debug("Topics Occurrences Index: %s", self._topics_occurrences_index_filename)

        self._topics_labels_index_filename = topics_labels_index_filename \
            if topics_labels_index_filename is not None \
            else QueryProcessor._topics_labels_index_filename_default

        self.load_files_index()
        self.load_topics_occurrences_index()
        self.load_topics_labels_index()

    def load_files_index(self):
        self.logger.info("Loading files index from %s", self._files_index_filename)

        d = shelve.open(self._files_index_filename)
        self._files_index = d["Corpus"]
        d.close()

    def load_topics_labels_index(self):
        self.logger.info("Loading topics labels index from %s", self._topics_labels_index_filename)

        d = shelve.open(self._topics_labels_index_filename)
        self._topics_labels_index = d["Corpus"]
        d.close()

    def load_topics_occurrences_index(self):
        self.logger.info("Loading topics index from %s", self._topics_occurrences_index_filename)

        d = shelve.open(self._topics_occurrences_index_filename)
        self._topics_occurrences_index = d["Corpus"]
        d.close()

    def _get_files_for_topic(self, topic):
        return [f for f, _ in self._topics_occurrences_index[topic]]

    def _get_topics_for_files(self, files, ignored_topic):
        result_topics = []
        for target_file in files:
            result_topics.extend([int(f) for f, _ in self._files_index[target_file] if f not in ignored_topic])
        return sorted(list(set(result_topics)))

    def get_topic_id_from_label(self, topic_label):
        try:
            return self._topics_labels_index[topic_label]
        except:
            return None

    def execute(self, topics):
        """

        :rtype: Tuple[list, list]
        :param topics: List of topics for which to search files and co_occurring topics
        :return: list of files matching the topics and list of topics found in these files (minus topics)
        """
        result_files = set()
        topic_list = topics.split('-')
        for topic in topic_list:
            single_topic_files = set(self._get_files_for_topic(topic))
            if len(result_files) == 0:
                result_files = result_files.union(single_topic_files)
            else:
                result_files = result_files.intersection(single_topic_files)

        result_topics = self._get_topics_for_files(result_files, topic_list)

        return list(result_files), result_topics


def main():
    pass


if __name__ == '__main__':
    main()
