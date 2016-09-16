import shelve
import logging

TOPICS_OCCURRENCES_INDEX_FILENAME = "Topics_Occurrences_Index"
TOPICS_COOCCURRENCES_INDEX_FILENAME = "Topics_CoOccurrences_Index"
FILES_INDEX_FILENAME = "Files_Index"
LOG_LEVEL = logging.INFO


class CoOccurrenceExtractor:
    """Use this class to extract all co-occurrences of topics in the corpus, using the index of occurrences.

    Updates the index of topics and creates the co-occurrence index.

    :param topics_occurrences_index_filename: name of the file containing the index of files per topic
    :param files_index_filename: name of the file containing the index of topics per file

    """
    def __init__(self, topics_occurrences_index_filename=None, files_index_filename=None, depth=15):
        logging.basicConfig(filename="corpus_analyzer.log", filemode="w",
                            level=LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        # logging.basicConfig(level=LOG_LEVEL, format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        if topics_occurrences_index_filename is not None:
            self._topics_occurrences_index_filename = topics_occurrences_index_filename
        else:
            self._topics_occurrences_index_filename = TOPICS_OCCURRENCES_INDEX_FILENAME

        if files_index_filename is not None:
            self._files_index_filename = files_index_filename
        else:
            self._files_index_filename = FILES_INDEX_FILENAME

        self._topics_occurrences_table = {}
        self._topics_cooccurrences_table = {}
        self._files_table = {}

        self._load_topics_occurrences_table()
        self._load_files_table()

        self._depth = depth
        self._recursive_depth = 0

    def extract(self):
        """

        :return:
        """
        nb_files = len(self._files_table.keys())
        nb_file = 0
        for map_file in self._files_table.keys():
            nb_file += 1

            map_topics = sorted(int(topic) for topic, _ in self._files_table[map_file])

            self.logger.info("*"*1+" Processing file: %s (%s / %s)", map_file, nb_file, nb_files)
            self.logger.info("*"*1+" Found %s corresponding topics", len(map_topics))
            self.logger.debug("*"*1+" Corresponding topics: %s", map_topics)

            nb_topic = 0
            for topic in map_topics:
                nb_topic += 1

                co_topics = sorted([int(co_topic) for co_topic, _ in self._files_table[map_file]
                                    if int(co_topic) > int(topic)])

                self.logger.info("*"*2+" Processing topic: %s (%s / %s)", topic, nb_topic, len(map_topics))
                self.logger.info("*"*2+" Found %s corresponding co_topics", len(co_topics))
                self.logger.debug("*"*2+" Corresponding co_topics: %s", co_topics)

                nb_co_topic = 0
                for co_topic in co_topics:
                    nb_co_topic += 1
                    self.logger.info("*"*3+" Topic: %s File: %s Processing co_topic: %s (%s / %s)",
                                     topic, map_file, co_topic, nb_co_topic, len(co_topics))

                    self._fill_topic_cooccurrences(str(topic), str(co_topic))
                    self._fill_topic_occurrences(str(topic), str(co_topic), map_file)
                    root_topic = CoOccurrenceExtractor.build_composite_key(str(topic), str(co_topic))

                    # Start recursive calls to process all combinations based on topics found within map_file
                    self.extract_cooccurrences(root_topic, map_file)

        self._save_occurrences_table()
        self._save_cooccurrences_table()

    def extract_cooccurrences(self, root_topic, map_file):
        """

        :param root_topic:
        :param map_file:
        :return:
        """
        if root_topic in self._topics_occurrences_table.keys() \
                and map_file in self._topics_occurrences_table[root_topic]\
                and root_topic in self._topics_cooccurrences_table.keys():
            self.logger.debug("*"*4+" %s already extracted for file %s", root_topic, map_file)
            return

        self.logger.info("*"*4+" Extracting co_occurrences for: %s in file %s", root_topic, map_file)

        # target_co_topics = self._extract_topic_cooccurrences(root_topic, map_file)
        target_co_topics = sorted([int(co_topic) for co_topic, _ in self._files_table[map_file]
                                   if int(co_topic) > self._max_topic_from_root(root_topic)])

        if target_co_topics is None or len(target_co_topics) == 0:
            self.logger.debug("*"*5+" No co_occurrences found...")
            self.logger.debug("*"*50)
            return

        self.logger.debug("*"*5+" Topic: %s File: %s Corresponding topics: %s", root_topic, map_file, target_co_topics)

        for target_co_topic in target_co_topics:
            self._fill_topic_cooccurrences(root_topic, target_co_topic)
            self._fill_topic_occurrences(root_topic, target_co_topic, map_file)
            next_topic = CoOccurrenceExtractor.build_composite_key(root_topic, target_co_topic)

            if not self._is_final_leaf(root_topic):
                self.extract_cooccurrences(next_topic, map_file)

    def _extract_topic_cooccurrences(self, target_topic, target_file):
        """

        :param target_topic:
        :param target_file:
        :return:
        """
        co_occurrences = []
        co_topics = self._extract_topics_for_file(target_file, target_topic)

        for topic in co_topics:
            if not self.is_used_topic(target_topic, topic):
                if topic not in co_occurrences:
                    co_occurrences.append(topic)

        self.logger.debug("Cooccurrences for topic: %s are: %s", target_topic, co_occurrences)

        return co_occurrences

    def find_cooccurrences(self, target):
        """

        :param target: topic for which to find co_occurrences
        :return:
        """
        co_occurrences = {}
        corpus_files = self._topics_occurrences_table[target]
        for corpus_file, _ in corpus_files:
            co_topics = self._extract_topics_for_file(corpus_file, target)

            for topic in co_topics:
                if topic not in co_occurrences:
                    co_occurrences[topic] = 1
                else:
                    co_occurrences[topic] += 1

        return co_occurrences

    def _extract_topics_for_file(self, corpus_file, target_topic):
        """

        :param corpus_file:
        :param target_topic:
        :return:
        """
        target_list = target_topic.split('-')
        for target in target_list:
            assert target in [topic for topic, _ in self._files_table[corpus_file]]

        topics = [topic for topic, _ in self._files_table[corpus_file] if topic not in target_list]
        return sorted(topics)

    @property
    def topics_occurrences_table(self):
        return self._topics_occurrences_table

    def _load_topics_occurrences_table(self):
        """

        :return:
        """
        d = shelve.open(self._topics_occurrences_index_filename)
        self._topics_occurrences_table = d["Corpus"]
        d.close()

    def _load_files_table(self):
        """

        :return:
        """
        d = shelve.open(self._files_index_filename)
        self._files_table = d["Corpus"]
        d.close()

    def _fill_topic_occurrences(self, topic, co_topic, map_file):
        """

        :param topic:
        :param co_topic:
        :param map_file:
        :return:
        """
        root_topic = CoOccurrenceExtractor.build_composite_key(topic, co_topic)
        if root_topic in self._topics_occurrences_table:
            if (map_file, -1) not in self._topics_occurrences_table[root_topic]:
                self.logger.info("Add new file %s to topic %s", map_file, root_topic)
                self._topics_occurrences_table[root_topic].append((map_file, -1))
        else:
            self.logger.info("Add new (%s, %s) to topic index", root_topic, map_file)
            self._topics_occurrences_table[root_topic] = [(map_file, -1)]

    def _fill_topic_cooccurrences(self, topic, co_topic):
        """

        :param topic:
        :param co_topic:
        :return:
        """
        if topic in self._topics_cooccurrences_table:
            self.logger.info("Add co_topic %s to topic %s", co_topic, topic)
            self._topics_cooccurrences_table[topic].append(co_topic)
        else:
            self.logger.info("Add new (%s, %s) to index", co_topic, topic)
            self._topics_cooccurrences_table[topic] = [co_topic]

    @staticmethod
    def build_composite_key(root_topic, cooccurrence_topic):
        """Builds a new composite index key from a root and a cooccurrence topic

        :param root_topic: nb1-nb2-(...)-nbn
        :param cooccurrence_topic: nbx
        :return: nb1-nb2-(...-nbx-...)-nbn
        """
        root_topics_index = [int(topic) for topic in root_topic.split('-')]
        root_topics_index.append(int(cooccurrence_topic))

        index_key = "-".join([str(index) for index in sorted(root_topics_index)])
        return index_key

    def _is_final_leaf(self, topic):
        if len(topic.split('-')) >= self._depth:
            return True
        return False

    @staticmethod
    def is_used_topic(target_topic, topic):
        """

        :param target_topic:
        :param topic:
        :return:
        """
        used_topics = target_topic.split("-")
        if topic in used_topics:
            return True
        else:
            return False

    @staticmethod
    def _percent(idx, total):
        """

        :param idx:
        :param total:
        :return:
        """
        return (idx * 100) / total

    def _save_cooccurrences_table(self):
        """

        :return:
        """
        index_filename = "Full_Cooccurrences_Index"
        d = shelve.open(index_filename, flag='n')
        d["Corpus"] = self._topics_cooccurrences_table
        d.close()

    def _save_occurrences_table(self):
        """

        :return:
        """
        if len(self._topics_occurrences_table) == 0:
            return
        index_filename = "Full_Occurrences_Index"
        d = shelve.open(index_filename, flag='n')
        d["Corpus"] = self._topics_occurrences_table
        d.close()

    @staticmethod
    def _max_topic_from_root(root_topic):
        """

        :param root_topic:
        :return:
        """
        return max([int(topic) for topic in root_topic.split('-')])


def main():
    """

    :return:
    """
    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # target_topic = "2432"
    # extractor = CoOccurrenceExtractor(topics_occurrences_index_filename="../output/2015_Topics_Occurrences_Index",
    #                                files_index_filename="../output/2015_Files_Index")
    # extractor = CoOccurrenceExtractor("../tests/testOutput/Test_Topics_Occurrences_Index",
    #                                   "../tests/testOutput/Test_Files_Index", depth=15)
    # extractor = CoOccurrenceExtractor("../tests/testOutput/Test_Cooccurrence_Topics_Occurrences_Index",
    #                                "../tests/testOutput/Test_Cooccurrence_Files_Index", depth=5)
    extractor = CoOccurrenceExtractor("../tests/testOutput/Test_SingleFile_Topics_Occurrences_Index",
                                      "../tests/testOutput/Test_SingleFile_Files_Index", depth=15)
    print "hash table loaded with %d topics available" % len(extractor.topics_occurrences_table)
    extractor.extract()

if __name__ == "__main__":
    pass
    #main()
