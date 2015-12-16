import logging
import os
import shelve
import xml.etree.cElementTree as Et
from sys import exc_info

CORPUS_ROOT_FOLDER = "~/Corpus"
TOPICS_OCCURRENCES_INDEX_FILENAME = "Topics_Occurences_Index"
TOPICS_INDEX_FILENAME = "Topics_Index"
FILES_INDEX_FILENAME = "Files_Index"
LOG_LEVEL = logging.DEBUG


class CorpusAnalyzer:
    """Use this class to analyze the topics repartition accross a given corpus
    or build the dictionary of files with their associated topics

    :param corpus_root_folder: Location of the corpus. All subfolders are processed recursively. Defaults to ~/Corpus

    """
    def __init__(self, corpus_root_folder=None):

        logging.basicConfig(level=LOG_LEVEL, format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        self.topics_occurrences_hash = {}
        self.topics_hash = {}
        self.files_hash = {}

        self.corpus_root_folder = corpus_root_folder if corpus_root_folder is not None else CORPUS_ROOT_FOLDER

        self.logger.info("Initialized with corpus root folder: %s", self.corpus_root_folder)

    def extract_topics_indexes(self, topics_occurrences_index_filename=None, topics_index_filename=None):
        if topics_occurrences_index_filename is None:
            topics_occurrences_index_filename = TOPICS_OCCURRENCES_INDEX_FILENAME

        if topics_index_filename is None:
            topics_index_filename = TOPICS_INDEX_FILENAME

        idx = 0
        for root, dirs, files_list in os.walk(self.corpus_root_folder):
            for semantic_result in files_list:
                if os.path.isfile(os.path.join(root, semantic_result)):
                    self.logger.debug("%s/%s", root, semantic_result)
                    self._process_enrichment_result(root, semantic_result)
                    idx += 1
                    if idx % 100 == 0:
                        self.logger.info("%s files processed...", idx)

        self.logger.info("Nb subjects extracted: %s", len(self.topics_occurrences_hash.items()))

        self.shelve_index(index_filename=topics_occurrences_index_filename,
                          index_data=self.topics_occurrences_hash)
        self.shelve_index(index_filename=topics_index_filename,
                          index_data=self.topics_hash)

    def extract_files_index(self, topics_occurrences_index_filename, files_index_filename=None):
        """
        Creates an index of array of [(topic, relevance), (topic, relevance), ...] per file of the corpus
        :param topics_occurrences_index_filename:
        :param files_index_filename:
        :return:
        """
        if files_index_filename is None:
            files_index_filename = FILES_INDEX_FILENAME

        if self.topics_occurrences_hash is None or len(self.topics_occurrences_hash) == 0:
            self.logger.info("Loading topics index file")
            self.load_topics_occurrences_index(topics_occurrences_index_filename)
        idx = 0
        for topic, files in self.topics_occurrences_hash.iteritems():
            self.logger.debug("%s %s", topic, files)
            for result_file, relevance in files:
                if result_file in self.files_hash:
                    self.files_hash[result_file].append((topic, relevance))
                else:
                    self.files_hash[result_file] = [(topic, relevance)]
            idx += 1
            if idx % 100 == 0:
                self.logger.info("%s topics processed...", idx)
        self.logger.debug(self.files_hash)
        self.logger.info("Nb files extracted: %s", len(self.files_hash.items()))
        self.shelve_index(index_filename=files_index_filename, index_data=self.files_hash)

    def _process_enrichment_result(self, folder, result_file):
        try:
            tree = Et.ElementTree(file=os.path.join(folder, result_file))
        except Exception, e:
            self.logger.error("Failed to load xml content for file: %s", result_file, exc_info=True)
            return
        root = tree.getroot()
        # print root
        for subject in root.findall("./annotation/subject"):
            uri = self._strip_uri(subject.get('uri'))
            label_en = subject.get('label_en')
            label_fr = subject.get('label_fr')
            relevance = 'N' if subject.get('relevance') == 'normal' else 'H'
            # print uri, relevance
            self._process_topics_occurrences(result_file, uri, relevance)
            self._process_topics_dictionary(uri, label_en, label_fr)

    def _process_topics_occurrences(self, result_file, uri, relevance):
        """
        Generates an index of [(file, relevance), (file, relevance), ...] for all topics
        :param result_file:
        :param uri:
        :param relevance:
        :return:
        """
        if uri in self.topics_occurrences_hash:
            self.topics_occurrences_hash.get(uri).append((result_file, relevance))
        else:
            self.topics_occurrences_hash[uri] = [(result_file, relevance)]

    def _process_topics_dictionary(self, uri, label_en, label_fr):
        """
        Generates the index of (label_en, label_fr) for all topics
        :param uri:
        :param label_en:
        :param label_fr:
        :return:
        """
        if uri not in self.topics_hash:
            self.topics_hash[uri] = (label_en, label_fr)

    @staticmethod
    def _strip_uri(uri):
        """Extract "raw" topic identifier from uri

        :param uri: "http://kim.oecd.org/Taxonomy/Topics#T187"
        :return: 187
        """
        parts = uri.split("/")
        return parts[-1][8::]

    @staticmethod
    def shelve_index(index_filename, index_data):
        d = shelve.open(index_filename)
        d["Corpus"] = index_data
        d.close()

    def load_topics_occurrences_index(self, topics_occurrences_index_filename):
        self.logger.info("Loading corpus hash table from %s", topics_occurrences_index_filename)

        d = shelve.open(topics_occurrences_index_filename)
        self.topics_occurrences_hash = d["Corpus"]
        d.close()

def main():
    corpus_root = "/media/Data/OECD/Official Documents Enrichment/Documents"
    topics_occurrences_index = "Topics_Occurrences_Index"
    topics_index = "Topics_Index"
    files_index = "Files_Index"

    # corpus_root = "/media/Data/OECD/Official Documents Enrichment/2015/06/18"
    # topics_occurrences_index = "2015_06_18_Topics_Occurrences_Index"
    # topics_index = "2015_06_18_Topics_Index"
    # files_index = "2015_06_18_Files_Index"

    # corpus_root = "../tests/testCooccurrence/"
    # topics_occurrences_index = "Test_Cooccurrence_Topics_Occurrences_Index"
    # topics_index = "Test_Cooccurrence_Topics_Index"
    # files_index = "Test_Cooccurrence_Files_Index"

    # corpus_root = "../tests/testCorpus/"
    # topics_occurrences_index = "Test_Topics_Occurrences_Index"
    # topics_index = "Test_Topics_Index"
    # files_index = "Test_Files_Index"

    LOG_LEVEL = logging.INFO
    logging.basicConfig(filename="corpus_analyzer.log", filemode="w",
                        level=LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    analyzer = CorpusAnalyzer(corpus_root_folder=corpus_root)

    print "Begin extract files index"
    analyzer.extract_topics_indexes(topics_index_filename=topics_index,
                                    topics_occurrences_index_filename=topics_occurrences_index)
    print "End extract files index"
    print "Begin extract files index"
    analyzer.extract_files_index(topics_occurrences_index_filename=topics_occurrences_index,
                                 files_index_filename=files_index)
    print "End extract files index"

if __name__ == '__main__':
    main()