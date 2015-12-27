import logging
import os
import shelve
import xml.etree.cElementTree as Et
from sys import exc_info
import datetime


def get_date_from_folder(folder):
    folder_elements = folder.split('/')
    day = int(folder_elements[-1])
    month = int(folder_elements[-2])
    year = int(folder_elements[-3])
    return datetime.date(year, month, day)


class CorpusAnalyzer:
    """Use this class to analyze the topics repartition across a given corpus
    or build the dictionary of files with their associated topics

    :param corpus_root_folder: Location of the corpus. All sub-folders are processed recursively. Defaults to ~/Corpus

    """

    # region --- default values ---
    CORPUS_ROOT_FOLDER_DEFAULT = "~/Corpus"
    TOPICS_OCCURRENCES_INDEX_FILENAME_DEFAULT = "Topics_Occurrences_Index"
    TOPICS_INDEX_FILENAME_DEFAULT = "Topics_Index"
    TOPICS_LABELS_INDEX_FILENAME_DEFAULT = "Topics_Labels_Index"
    FILES_INDEX_FILENAME_DEFAULT = "Files_Index"
    LOG_LEVEL_DEFAULT = logging.DEBUG
    # endregion

    def __init__(self, corpus_root_folder=None):
        logging.basicConfig(level=CorpusAnalyzer.LOG_LEVEL_DEFAULT, format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        self.topics_occurrences_hash = {}
        self.topics_hash = {}
        self.files_hash = {}
        self.processed_files = {}

        self.corpus_root_folder = corpus_root_folder if corpus_root_folder is not None \
            else CorpusAnalyzer.CORPUS_ROOT_FOLDER_DEFAULT

        self.logger.info("Initialized with corpus root folder: %s", self.corpus_root_folder)

    def extract_indexes(self, files_index_filename=None,
                        topics_occurrences_index_filename=None, topics_index_filename=None):

        if topics_occurrences_index_filename is None:
            topics_occurrences_index_filename = CorpusAnalyzer.TOPICS_OCCURRENCES_INDEX_FILENAME_DEFAULT

        if topics_index_filename is None:
            topics_index_filename = CorpusAnalyzer.TOPICS_INDEX_FILENAME_DEFAULT

        if files_index_filename is None:
            files_index_filename = CorpusAnalyzer.FILES_INDEX_FILENAME_DEFAULT

        idx = 0
        for root, dirs, files_list in os.walk(self.corpus_root_folder):
            for semantic_result_file in files_list:
                if os.path.isfile(os.path.join(root, semantic_result_file)):
                    self.logger.debug("processing: %s/%s", root, semantic_result_file)
                    self._process_enrichment_result(root, semantic_result_file)
                    idx += 1
                    if idx % 100 == 0:
                        self.logger.info("%s files processed...", idx)

        self.logger.info("Total nb files processed: %s", idx)
        self.logger.info("Nb subjects extracted: %s", len(self.topics_occurrences_hash.items()))

        self.shelve_index(index_filename=topics_occurrences_index_filename,
                          index_data=self.topics_occurrences_hash)
        self.shelve_index(index_filename=topics_index_filename,
                          index_data=self.topics_hash)
        self.shelve_index(index_filename=files_index_filename,
                          index_data=self.files_hash)

    def _process_enrichment_result(self, folder, result_file):
        # First of all, take care of potential duplicates in the corpus
        if result_file in self.processed_files:
            self.logger.info("File %s already processed.", result_file)
            if not self._is_posterior(result_file, folder):
                self.logger.info("A more recent version of %s was already processed, moving on", result_file)
                return
            else:
                # remove previous occurrences in various indexes to be replaced by this one
                self.logger.info("Removing previous occurrences of %s in various indexes to be replaced by this one",
                                 result_file)
                self._remove_file_from_topics_occurrences_hash(result_file)
                self._remove_file_from_files_hash(result_file)
        else:
            self.processed_files[result_file] = folder

        try:
            tree = Et.ElementTree(file=os.path.join(folder, result_file))
        except Exception, e:
            self.logger.error("Failed to load xml content for file: %s", result_file, exc_info=True)
            return
        root = tree.getroot()
        for subject in root.findall("./annotation/subject"):
            uri = self._strip_uri(subject.get('uri'))
            label_en = subject.get('label_en')
            label_fr = subject.get('label_fr')
            relevance = 'N' if subject.get('relevance') == 'normal' else 'H'
            self._process_file_topics(result_file, uri, relevance)
            self._process_topics_occurrences(result_file, uri, relevance)
            self._process_topics_dictionary(uri, label_en, label_fr)

    def _remove_file_from_files_hash(self, result_file):
        if result_file not in self.files_hash:
            self.logger.info("File %s not found in topics occurrences index. Nothing to remove.", result_file)
            return
        self.logger.info("Removing occurrence of %s in files index", result_file)
        del self.files_hash[result_file]

    def _remove_file_from_topics_occurrences_hash(self, result_file):
        if result_file not in self.files_hash:
            self.logger.info("File %s not found in topics occurrences index. Nothing to remove.", result_file)
            return
        for topic, _ in self.files_hash[result_file]:
            self.logger.debug("Before - Occurrences for topic %s: %s", topic, self.topics_occurrences_hash[topic])
            self.logger.info("Removing occurrence of %s for topic %s", result_file, topic)
            occurrences = self.topics_occurrences_hash[topic]
            del self.topics_occurrences_hash[topic]
            clean_occurrences = []
            for f, r in occurrences:
                if f != result_file:
                    clean_occurrences.append((f, r))
                else:
                    self.logger.info("%s removed for topic %s", result_file, topic)
            self.topics_occurrences_hash[topic] = clean_occurrences
            # self.topics_occurrences_hash[topic] = [(f, r) for f, r in occurrences if f is not result_file]
            self.logger.debug("After - Occurrences for topic %s: %s", topic, self.topics_occurrences_hash[topic])

    def _is_posterior(self, result_file, current_folder):
        """

        :param result_file:
        :param current_folder:
        :return: True if current_folder yields a date posterior to the date associated to already processed result_file
        """
        previous_folder = self.processed_files[result_file]

        previous_date = get_date_from_folder(previous_folder)
        current_date = get_date_from_folder(current_folder)

        if previous_date < current_date:
            return True
        else:
            return False

    def _process_file_topics(self, result_file, uri, relevance):
        if result_file in self.files_hash:
            self.files_hash[result_file].append((uri, relevance))
        else:
            self.files_hash[result_file] = [(uri, relevance)]

    def _process_topics_occurrences(self, result_file, uri, relevance):
        """
        Generates an index of [(file, relevance), (file, relevance), ...] for all topics
        :param result_file:
        :param uri:
        :param relevance:
        :return:
        """
        if uri in self.topics_occurrences_hash:
            # check if file not already present in list
            if result_file in [f for f, _ in self.topics_occurrences_hash[uri]]:
                raise Exception('{file} already added to list of files for topic {topic}'.format(file=result_file,
                                                                                                 topic=uri))
            self.topics_occurrences_hash[uri].append((result_file, relevance))
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
        logging.getLogger(__name__).info("Shelving %s", index_filename)
        d = shelve.open(index_filename)
        d["Corpus"] = index_data
        d.close()

    @staticmethod
    def extract_topics_labels_index(topics_index_filename=None, topics_labels_index_filename=None):
        """

        :param topics_index_filename: file containing the index of topics ids
        :param topics_labels_index_filename: file where the topics labels index will be saved
        :return:
        """
        if topics_index_filename is None:
            topics_index_filename = CorpusAnalyzer.TOPICS_INDEX_FILENAME_DEFAULT
        if topics_labels_index_filename is None:
            topics_labels_index_filename = CorpusAnalyzer.TOPICS_LABELS_INDEX_FILENAME_DEFAULT
        topics_labels_index = dict()

        topics_index = CorpusAnalyzer.load_topics_index(topics_index_filename)
        for topic, labels in topics_index.iteritems():
            topics_labels_index[labels[0]] = topic
            topics_labels_index[labels[1]] = topic

        # Save the index to the filesystem
        CorpusAnalyzer.shelve_index(topics_labels_index_filename, topics_labels_index)

    @staticmethod
    def load_topics_index(topics_index_filename):
        d = shelve.open(topics_index_filename)
        topics_index = d["Corpus"]
        d.close()
        return topics_index

    @staticmethod
    def duplicates_finder():
        idx = 0
        result_files = []
        duplicates = []
        for root, dirs, files_list in os.walk("/media/Data/OECD/Official Documents Enrichment/Documents"):
            for semantic_result in files_list:
                if os.path.isfile(os.path.join(root, semantic_result)):
                    if semantic_result in result_files:
                        print "%s already processed !" % semantic_result
                        duplicates.append((root, semantic_result))
                    else:
                        result_files.append(semantic_result)
                    idx += 1
                    if idx % 100 == 0:
                        print "%s files processed..." % idx

        print "Nb duplicates found: %s" % len(duplicates)
        return duplicates


def main():
    corpus_root = "/media/Data/OECD/Official Documents Enrichment/Documents"
    topics_occurrences_index = "Topics_Occurrences_Index"
    topics_index = "Topics_Index"
    files_index = "Files_Index"
    topics_labels_index = "Topics_Labels_Index"

    # corpus_root = "/media/Data/OECD/Official Documents Enrichment/2015/06/18"
    # topics_occurrences_index = "2015_06_18_Topics_Occurrences_Index"
    # _topics_index = "2015_06_18_Topics_Index"
    # files_index = "2015_06_18_Files_Index"

    # corpus_root = "../tests/testCooccurrence/"
    # topics_occurrences_index = "Test_Cooccurrence_Topics_Occurrences_Index"
    # _topics_index = "Test_Cooccurrence_Topics_Index"
    # files_index = "Test_Cooccurrence_Files_Index"

    # corpus_root = "../tests/testCorpus/"
    # topics_occurrences_index = "Test_Topics_Occurrences_Index"
    # _topics_index = "Test_Topics_Index"
    # files_index = "Test_Files_Index"

    # corpus_root = "../tests/testSingleFile/"
    # topics_occurrences_index = "SingleFile_Topics_Occurrences_Index"
    # _topics_index = "SingleFile_Topics_Index"
    # files_index = "SingleFile_Files_Index"

    logging.basicConfig(filename="../output/corpus_analyzer.log", filemode="w",
                        level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    analyzer = CorpusAnalyzer(corpus_root_folder=corpus_root)

    print "Begin extract indexes"
    analyzer.extract_indexes(topics_index_filename=topics_index,
                             topics_occurrences_index_filename=topics_occurrences_index,
                             files_index_filename=files_index)
    print "End extract indexes"

    print "Begin extract topics_labels index"
    CorpusAnalyzer.extract_topics_labels_index(topics_index_filename=topics_index,
                                               topics_labels_index_filename=topics_labels_index)
    print "End extract topics_labels index"


if __name__ == '__main__':
    main()
