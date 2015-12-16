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

    def _get_files(self, topic):
        return [f for f, _ in self._topics_occurrences_index[topic]]

    def _get_topics(self, files, ignored_topic):
        result_topics = []
        for target_file in files:
            result_topics.extend([int(f) for f,_ in self._files_index[target_file] if f not in ignored_topic])
        return sorted(list(set(result_topics)))

    def execute(self, topics):
        """

        :param topics:
        :return: Return the list of files matching the topics and the list of topics found in these files (minus topics)
        """
        result_files = set()
        result_topics = []
        topic_list = topics.split('-')
        for topic in topic_list:
            single_topic_files = set(self._get_files(topic))
            if len(result_files) == 0:
                result_files = result_files.union(single_topic_files)
            else:
                result_files = result_files.intersection(single_topic_files)

        result_topics = self._get_topics(result_files, topic_list)

        return list(result_files), result_topics


def main():
    pass

if __name__ == '__main__':
    main()