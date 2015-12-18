import shelve
import logging
import logging.config

LOG_LEVEL = logging.INFO
HASH_TABLE_FILENAME = "Topics_Index"


class ProximityFinder:

    NB_HIGH_MATCHES = 0
    TOTAL_MATCHES = 1

    def __init__(self, hash_table_filename=None):
        logging.basicConfig(level=logging.DEBUG, format='%(name)s - %(levelname)s - %(message)s')
        # logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger(__name__)

        self.proximity_results = {}
        self.raw_results = []
        self.hash_table_filename = hash_table_filename if hash_table_filename is not None else HASH_TABLE_FILENAME
        self.corpus_table = None

    def _load_corpus_table(self):
        self.logger.info("Loading corpus hash table from %s", self.hash_table_filename)

        d = shelve.open(self.hash_table_filename)
        self.corpus_table = d["Corpus"]
        d.close()

    def build_proximity_results(self, semantic_signature, sort_criteria=None, minimum_match_number=0):
        self.proximity_results = {}
        if self.corpus_table is None:
            self._load_corpus_table()

        for topic in semantic_signature:
            matching_files = self.corpus_table[topic]
            for matching_file, relevance in matching_files:
                if matching_file not in self.proximity_results:
                    self.proximity_results[matching_file] = [{"total_match": 1,
                                                              "normal_match": 1 if relevance == "N" else 0,
                                                              "high_match": 1 if relevance == "H" else 0},
                                                             [(topic, relevance)]]
                else:
                    matching_file_info = self.proximity_results[matching_file]
                    matching_file_info[1].append((topic, relevance))
                    matching_file_info[0]["total_match"] += 1
                    if relevance == "N":
                        matching_file_info[0]["normal_match"] += 1
                    else:
                        matching_file_info[0]["high_match"] += 1

        self.logger.info("proximity table successfully built for %s", semantic_signature)
        self._sort_results(sort_criteria, minimum_match_number)
        return self

    def _sort_results(self, sort_criteria, minimum_match_number):
        sorting_label = ""
        self.proximity_results = dict((k, v) for k, v in self.proximity_results.items()
                                      if v[0]["total_match"] >= minimum_match_number)
        if sort_criteria is None:
            self.proximity_results = list(self.proximity_results.iteritems())
        elif sort_criteria == ProximityFinder.TOTAL_MATCHES:
            sorting_label = "total number of matches"
            self.proximity_results = self.sort_results_by_number_match()
        elif sort_criteria == ProximityFinder.NB_HIGH_MATCHES:
            sorting_label = "number of highly relevant matches"
            self.proximity_results = self.sort_results_by_number_high()
        else:
            raise Exception("invalid sorting criteria: %s", sort_criteria)

        if sort_criteria is not None:
            self.logger.info("Results sorted by %s", sorting_label)

        return self

    @staticmethod
    def get_number_high(matching_file_info):
        return matching_file_info[0]["high_match"]

    @staticmethod
    def get_number_matches(matching_file_info):
        return matching_file_info[0]["total_match"]

    def sort_results_by_number_match(self):
        sorted_keys = sorted(self.proximity_results.iteritems(), key=lambda (k, v): self.get_number_matches(v),
                             reverse=True)
        return sorted_keys

    def sort_results_by_number_high(self):
        sorted_keys = sorted(self.proximity_results.iteritems(), key=lambda (k, v): self.get_number_high(v),
                             reverse=True)
        return sorted_keys


if __name__ == '__main__':
    LOG_LEVEL = logging.WARNING
    logging.basicConfig(filename="proximity_finder.log", filemode="w",
                        level=LOG_LEVEL, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
