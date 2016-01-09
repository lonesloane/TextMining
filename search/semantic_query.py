import logging

from index.loader import FilesIndex, TopicsOccurrencesIndex, TopicsLabelsIndex

LOG_LEVEL = logging.INFO


class QueryProcessor:

    def __init__(self, files_index, topics_occurrences_index, topics_labels_index):
        self._files_index = files_index
        self._topics_occurrences_index = topics_occurrences_index
        self._topics_labels_index = topics_labels_index

        logging.basicConfig(level=LOG_LEVEL, format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def _get_files_for_topic(self, topic):
        """

        :param topic:
        :return:
        """
        return [f for f, _ in self._topics_occurrences_index.get_files_for_topic(topic)]

    def _get_topics_for_files(self, files, ignored_topic):
        """

        :param files:
        :param ignored_topic:
        :return:
        """
        result_topics = []
        for target_file in files:
            result_topics.extend([int(f) for f, _ in self._files_index.get_enrichment_for_files(target_file)
                                  if f not in ignored_topic])
        return sorted(list(set(result_topics)))

    def get_topic_id_from_label(self, topic_label):
        """

        :param topic_label: label of the topic for which to find the topic_id
        :return: topic_id or None if no topic was found with label "topic_label"
        """
        try:
            return self._topics_labels_index.get_topic_id_for_label(topic_label)
        except:
            return None

    def execute(self, topics):
        """

        :rtype: Tuple[list, list]
        :param topics: List of topics for which to search files and co_occurring topics
        :return: list of files matching the topics and list of topics found in these files (minus topics)
        """
        result_files = set()
        for topic in topics:
            single_topic_files = set(self._get_files_for_topic(topic))
            if len(result_files) == 0:
                result_files = result_files.union(single_topic_files)
            else:
                result_files = result_files.intersection(single_topic_files)

        result_topics = self._get_topics_for_files(result_files, topics)

        return list(result_files), result_topics


def main():
    pass


if __name__ == '__main__':
    main()
