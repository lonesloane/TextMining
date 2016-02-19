import logging

LOG_LEVEL = logging.INFO


class QueryProcessor:

    def __init__(self, files_index, topics_occurrences_index, topics_labels_index, topics_index):
        """

        :param files_index:
        :param topics_occurrences_index:
        :param topics_labels_index:
        :return:
        """
        self._files_index = files_index
        self._topics_occurrences_index = topics_occurrences_index
        self._topics_labels_index = topics_labels_index
        self._topics_index = topics_index

        logging.basicConfig(level=LOG_LEVEL, format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

    def _get_files_for_topic(self, topic):
        """

        :param topic:
        :return:
        """
        return [f for f, _ in self._topics_occurrences_index.get_files_for_topic(topic)]

    def _get_topics_for_files(self, files, ignored_topic=None):
        """

        :param files:
        :param ignored_topic:
        :return:
        """
        if ignored_topic is None:
            ignored_topic = list()
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

    def get_topic_labels_from_id(self, topic_id):
        """

        :param topic_id:
        :return:
        """
        try:
            return self._topics_index.get_labels_for_topic_id(topic_id)
        except:
            return None

    def execute(self, topics, order_by_relevance=False):
        """

        :param order_by_relevance:
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

        result_files = list(result_files)
        if order_by_relevance:
            result_files = self.sort_result_files(result_files, topics)
        else:
            self.logger.debug('Leaving results unordered')

        result_topics = self._get_topics_for_files(result_files, topics)

        return result_files, result_topics

    def sort_result_files(self, result_files, topics):
        """

        :param result_files:
        :param topics:
        :return:
        """
        self.logger.debug('Sorting files: %s on topics: %s', result_files, topics)
        scored_files = []
        for f in result_files:
            score = 0
            f_topics = self._files_index.get_enrichment_for_files(f)
            self.logger.debug('File: %s has topics: %s', f, f_topics)
            for t, relevance in f_topics:
                if t in topics:
                    if relevance == 'N':
                        score += 100
                    if relevance == 'H':
                        score += 10000
            self.logger.debug('File: %s has score: %s', f, score)
            scored_files.append((f, score))
            scored_files.sort(key=lambda scored_file: scored_file[1], reverse=True)

        return [f for f, score in scored_files]

    def search_documents_by_topics(self, topics, order_by_relevance=False, hf=20, b=0):
        """

        :param topics:
        :param order_by_relevance:
        :param hf: number of hits per page
        :param b: base page number
        :return:
        """
        documents = list()
        result_files, result_topics = self.execute(topics, order_by_relevance)
        if hf != -1:  # hf=-1 means no pagination. Else, keep only 'hf' documents in the result list, starting from 'b'
            result_files = result_files[b:b+hf]
        for result_file in result_files:
            enrichment_result = self.get_enrichment_for_files(result_file)
            document = dict()
            semantic_signature = self.build_semantic_signature(enrichment_result)
            document['name'] = result_file
            document['semantic_signature'] = semantic_signature
            documents.append(document)

        result = dict()
        result['search_terms'] = self._get_topics_from_topic_ids(topics)
        result['documents'] = documents
        result['topics'] = result_topics
        return result

    def get_enrichment_for_files(self, target_file):
        """

        :param target_file:
        :return:
        """
        return self._files_index.get_enrichment_for_files(target_file=target_file)

    def build_semantic_signature(self, enrichment_result):
        """

        :param enrichment_result:
        :return:
        """
        semantic_signature = list()
        for item in enrichment_result:
            signature_item = dict()
            topic_id = item[0]
            relevance = item[1]
            topic_labels = self.get_topic_labels_from_id(topic_id)
            signature_item['id'] = topic_id
            signature_item['label'] = {'en': topic_labels[0], 'fr': topic_labels[1]}
            signature_item['relevance'] = relevance
            semantic_signature.append(signature_item)
        return semantic_signature

    def _get_topics_from_topic_ids(self, topic_ids):
        topics = list()
        try:
            for topic_id in topic_ids:
                topics.append(self._topics_index.get_topic_for_topic_id(topic_id))
            return topics
        except:
            return None


def main():
    pass


if __name__ == '__main__':
    main()
