"""Use this module to process Temis semantic enrichment files and generate
the various index files which are used by the Rest API and the web-client applications"""
import ConfigParser
import logging
import os
import shelve
import lxml.etree
from sys import exc_info
import datetime


def get_date_from_folder(folder):
    """Extract date from folder name.

    Assumes folder ends with xxx/year/month/day

    :param folder:
    :return: date (YYYY-MM-DD)
    """
    folder_elements = folder.split('/')
    day = int(folder_elements[-1])
    month = int(folder_elements[-2])
    year = int(folder_elements[-3])
    return datetime.date(year, month, day)


class Analyzer:
    """Use this class to analyze the topics repartition across the given corpus.

    Builds the various dictionaries for the files and their associated topics
    """

    # region --- default values ---
    CORPUS_ROOT_FOLDER_DEFAULT = "~/Corpus"
    LOG_LEVEL_DEFAULT = logging.DEBUG
    # endregion

    def __init__(self, corpus_root_folder=None):
        """

        :param corpus_root_folder: path to the root of the corpus.
        :type corpus_root_folder: str
        :return:
        """
        self.logger = logging.getLogger(__name__)

        self.process_topics_occurrences_index = False
        self.process_topics_index = False
        self.process_files_index = False
        self.process_files_dates_index = False
        self.topics_occurrences_index = {}
        self.topics_index = {}
        self.files_index = {}
        self.files_dates_index = {}
        self.processed_files = {}

        self.corpus_root_folder = corpus_root_folder if corpus_root_folder is not None \
            else Analyzer.CORPUS_ROOT_FOLDER_DEFAULT

        self.logger.info("Initialized with corpus root folder: %s", self.corpus_root_folder)

    def extract_indexes(self, files_index_filename=None, files_dates_index_filename=None,
                        topics_occurrences_index_filename=None, topics_index_filename=None,
                        only_highly_relevant=False):
        """Analyze the corpus, builds and saves index files

        This function saves the following indexes:

        * files index: for each file (i.e. JT000XXX.xml), list of (topic, relevance)
        * topics occurrences index: for each topic, list of (file, relevance)
        * topics index: for each topic, (english label, french label)
        * file dates index: for each file, the date of publication

        :param only_highly_relevant: set to true to extract only highly relevant topics
        :type only_highly_relevant: bool
        :param topics_index_filename: name of the file for the topics index
        :type topics_index_filename: str
        :param topics_occurrences_index_filename: name of the file for the topics occurrences index
        :type topics_occurrences_index_filename: str
        :param files_dates_index_filename: name of the file for the file dates index
        :type files_dates_index_filename: str
        :param files_index_filename: name of the file for the files index
        :type files_index_filename: str

        :return: self

        """

        if topics_occurrences_index_filename is not None:
            self.process_topics_occurrences_index = True
        if topics_index_filename is not None:
            self.process_topics_index = True
        if files_index_filename is not None:
            self.process_files_index = True
        if files_dates_index_filename is not None:
            self.process_files_dates_index = True

        idx = 0
        for root, dirs, files_list in os.walk(self.corpus_root_folder):
            for semantic_result_file in files_list:
                if os.path.isfile(os.path.join(root, semantic_result_file)):
                    self.logger.debug("processing: %s/%s", root, semantic_result_file)
                    self._process_enrichment_result(root, semantic_result_file, only_highly_relevant)
                    idx += 1
                    if idx % 100 == 0:
                        self.logger.info("%s files processed...", idx)

        self.logger.info("Total nb files processed: %s", idx)
        self.logger.info("Nb subjects extracted: %s", len(self.topics_occurrences_index.items()))

        if self.process_topics_occurrences_index:
            self.shelve_index(index_filename=topics_occurrences_index_filename,
                              index_data=self.topics_occurrences_index)
        if self.process_topics_index:
            self.shelve_index(index_filename=topics_index_filename,
                              index_data=self.topics_index)
        if self.process_files_index:
            self.shelve_index(index_filename=files_index_filename,
                              index_data=self.files_index)
        if self.process_files_dates_index:
            self.shelve_index(index_filename=files_dates_index_filename,
                              index_data=self.files_dates_index)

        return self

    def _process_enrichment_result(self, folder, result_file, only_highly_relevant=False):
        """Parse xml file generated by Temis semantic enrichment service.

        For each topic found, extracts its english label, its french label and its relevance
        and then feed it into the corresponding indexes.

        :param folder:
        :param result_file:
        :return:
        """
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
                self._remove_file_from_topics_occurrences_index(result_file)
                self._remove_file_from_files_index(result_file)
                self._remove_file_from_files_dates_index(result_file)
        else:
            self.processed_files[result_file] = folder

        if self.process_files_dates_index:
            self._process_file_date(result_file)

        try:
            doc = lxml.etree.parse(os.path.join(folder, result_file))
        except Exception, e:
            self.logger.error("Failed to load xml content for file: %s", result_file, exc_info=True)
            return
        root = doc.getroot()
        for subject in root.findall("./annotation/subject"):
            uri = self._strip_uri(subject.get('uri'))
            label_en = subject.get('label_en')
            label_fr = subject.get('label_fr')
            relevance = 'N' if subject.get('relevance') == 'normal' else 'H'

            if self.process_files_index:
                self._process_file_topics(result_file, uri, relevance)
            if self.process_topics_occurrences_index:
                self._process_topics_occurrences(result_file, uri, relevance)
            if self.process_topics_index:
                if relevance == 'H' or not only_highly_relevant:
                    self._process_topics_index(uri, label_en, label_fr)

    def _remove_file_from_files_index(self, result_file):
        """Remove any existing occurrence of result file from the files index.

        :param result_file:
        :return:
        """
        if result_file not in self.files_index:
            self.logger.info("File %s not found in topics occurrences index. Nothing to remove.", result_file)
            return
        self.logger.info("Removing occurrence of %s in files index", result_file)
        del self.files_index[result_file]

    def _remove_file_from_files_dates_index(self, result_file):
        if result_file not in self.files_dates_index:
            self.logger.info("File %s not found in topics occurrences index. Nothing to remove.", result_file)
            return
        self.logger.info("Removing occurrence of %s in files index", result_file)
        del self.files_dates_index[result_file]

    def _remove_file_from_topics_occurrences_index(self, result_file):
        """Remove any existing occurrence of result file from any of the topics.

        :param result_file:
        :return:
        """
        if result_file not in self.files_index:
            self.logger.info("File %s not found in topics occurrences index. Nothing to remove.", result_file)
            return
        for topic, _ in self.files_index[result_file]:
            self.logger.debug("Before - Occurrences for topic %s: %s", topic, self.topics_occurrences_index[topic])
            self.logger.info("Removing occurrence of %s for topic %s", result_file, topic)
            occurrences = self.topics_occurrences_index[topic]
            del self.topics_occurrences_index[topic]
            clean_occurrences = []
            for f, r in occurrences:
                if f != result_file:
                    clean_occurrences.append((f, r))
                else:
                    self.logger.info("%s removed for topic %s", result_file, topic)
            self.topics_occurrences_index[topic] = clean_occurrences
            self.logger.debug("After - Occurrences for topic %s: %s", topic, self.topics_occurrences_index[topic])

    def _is_posterior(self, result_file, current_folder):
        """Compares the date built from the folder of result file to the date built from 'current_folder'

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
        """Insert (uri, relevance) instance into files index for result_file.

        :param result_file:
        :param uri:
        :param relevance:
        :return:
        """
        if result_file in self.files_index:
            self.files_index[result_file].append((uri, relevance))
        else:
            self.files_index[result_file] = [(uri, relevance)]

    def _process_file_date(self, result_file):
        """

        :param result_file:
        :return:
        """
        self.logger.debug('Processing date for file %s', result_file)
        file_date = get_date_from_folder(self.processed_files[result_file])
        if result_file in self.files_dates_index:
            raise Exception('File %s already added to the index', result_file)
        else:
            self.logger.debug('Date %s found for file %s', file_date, result_file)
            self.files_dates_index[result_file] = file_date

    def _process_topics_occurrences(self, result_file, uri, relevance):
        """Generates an index of [(file, relevance), (file, relevance), ...] for all topics.

        :param result_file:
        :param uri:
        :param relevance:
        :return:
        """
        if uri in self.topics_occurrences_index:
            # check if file not already present in list
            if result_file in [f for f, _ in self.topics_occurrences_index[uri]]:
                raise Exception('{file} already added to list of files for topic {topic}'.format(file=result_file,
                                                                                                 topic=uri))
            self.topics_occurrences_index[uri].append((result_file, relevance))
        else:
            self.topics_occurrences_index[uri] = [(result_file, relevance)]

    def _process_topics_index(self, uri, label_en, label_fr):
        """Generates the index of (label_en, label_fr) for all topics.

        :param uri:
        :param label_en:
        :param label_fr:
        :return:
        """
        if uri not in self.topics_index:
            self.topics_index[uri] = (label_en, label_fr)

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
        """Saves the index to the file system.

        :param index_filename:
        :param index_data:
        :return:
        """
        logging.getLogger(__name__).info("Shelving %s", index_filename)
        d = shelve.open(index_filename)
        d["Corpus"] = index_data
        d.close()

    @staticmethod
    def extract_topics_labels_index(topics_index_filename, topics_labels_index_filename):
        """Builds an index of (label_english, label_french) for all topics from the data found in topics_index_filename

        :param topics_index_filename: file containing the index of topics ids
        :param topics_labels_index_filename: file where the topics labels index will be saved
        :return:
        """
        assert os.path.isfile(topics_index_filename)
        topics_labels_index = dict()

        topics_index = Analyzer.load_topics_index(topics_index_filename)
        for topic, labels in topics_index.iteritems():
            topics_labels_index[labels[0]] = topic
            topics_labels_index[labels[1]] = topic

        # Save the index to the filesystem
        Analyzer.shelve_index(topics_labels_index_filename, topics_labels_index)

    @staticmethod
    def load_topics_index(topics_index_filename):
        """Loads index from file system

        :param topics_index_filename:
        :return:
        """
        d = shelve.open(topics_index_filename)
        topics_index = d["Corpus"]
        d.close()
        return topics_index

    @staticmethod
    def duplicates_finder():
        """

        :return:
        """
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


def extract_indexes(corpus_root, topics_occurrences_index, topics_index, files_index, files_dates_index):
    """

    :return:
    """
    analyzer = Analyzer(corpus_root_folder=corpus_root)
    logging.getLogger(__name__).info('Begin extract indexes')
    analyzer.extract_indexes(files_dates_index_filename=files_dates_index)
    # analyzer.extract_indexes(files_index_filename=files_index,
    #                          topics_occurrences_index_filename=topics_occurrences_index,
    #                          topics_index_filename=topics_index)
    logging.getLogger(__name__).info('End extract indexes')


def extract_topics_labels_index(topics_index, topics_labels_index):
    """

    :return:
    """
    print "Begin extract topics_labels index"
    Analyzer.extract_topics_labels_index(topics_index_filename=topics_index,
                                         topics_labels_index_filename=topics_labels_index)
    print "End extract topics_labels index"


def main():
    """

    :return:
    """
    # Get configuration parameters
    basedir = os.path.abspath(os.path.dirname(__file__))
    config = ConfigParser.SafeConfigParser()
    # config.read(os.path.join(basedir, 'corpus.conf'))
    config.read(os.path.join(basedir, 'corpus_test.conf'))

    # Set appropriate logging level
    numeric_level = getattr(logging, config.get('LOGGING', 'level').upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError('Invalid log level: %s' % config.get('LOGGING', 'level'))
    logger = logging.getLogger(__name__)
    logger.setLevel(numeric_level)
    # create file handler which logs even debug messages
    fh = logging.FileHandler(config.get('LOGGING', 'log_file'), mode='w')
    fh.setLevel(logging.DEBUG)
    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    # create formatter and add it to the handlers
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)

    corpus_root = config.get('MAIN', 'corpus_root')
    output_dir = config.get('MAIN', 'output_dir')
    topics_occurrences_index = os.path.join(output_dir, config.get('MAIN', 'topics_occurrences_index_filename'))
    topics_index = os.path.join(output_dir, config.get('MAIN', 'topics_index_filename'))
    files_index = os.path.join(output_dir, config.get('MAIN', 'files_index_filename'))
    files_dates_index = os.path.join(output_dir, config.get('MAIN', 'files_dates_index_filename'))
    topics_labels_index = os.path.join(output_dir, config.get('MAIN', 'topics_labels_index_filename'))

    extract_indexes(corpus_root=corpus_root, topics_occurrences_index=topics_occurrences_index,
                    topics_index=topics_index, files_index=files_index, files_dates_index=files_dates_index)
    # extract_topics_labels_index(topics_index=topics_index, topics_labels_index=topics_labels_index)


if __name__ == '__main__':
    main()
