import logging
import logging.config
from index.loader import TopicsOccurrencesIndex


class ProximityFinder:
    """

    """
    TOPICS_OCCURRENCES_INDEX_FILENAME_DEFAULT = "../output/Topics_Occurrences_Index"
    PROXIMITY_SCORE = 0
    NB_HIGH_MATCHES = 1
    TOTAL_MATCHES = 2

    def __init__(self, topics_occurrences_index_filename=None):
        """

        :param topics_occurrences_index_filename:
        :return:
        """
        logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
        # logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger(__name__)

        self.proximity_results = {}
        self.raw_results = []
        self.topics_occurrences_index_filename = topics_occurrences_index_filename \
            if topics_occurrences_index_filename is not None \
            else ProximityFinder.TOPICS_OCCURRENCES_INDEX_FILENAME_DEFAULT
        self.topics_occurrences_index = TopicsOccurrencesIndex(self.topics_occurrences_index_filename)

    def build_proximity_results(self, semantic_signature, sort_criteria=None, minimum_match_number=0,
                                ignored_files=None):
        """

        :param ignored_files:
        :param semantic_signature:
        :param sort_criteria:
        :param minimum_match_number:
        :return:
        """
        self.proximity_results = {}
        if self.topics_occurrences_index is None:
            self.topics_occurrences_index = TopicsOccurrencesIndex(self.topics_occurrences_index_filename)

        for target_topic, target_relevance in semantic_signature:
            matching_files = self.topics_occurrences_index.get_files_for_topic(target_topic)
            self.logger.debug("Matching files found for topic %s: %s", target_topic, matching_files)
            for matching_file, relevance in matching_files:
                if matching_file not in self.proximity_results:
                    self.proximity_results[matching_file] = [(target_topic,
                                                              self.compute_proximity_score(target_relevance,
                                                                                           relevance))]
                else:
                    matching_file_info = self.proximity_results[matching_file]
                    matching_file_info.append((target_topic,
                                               self.compute_proximity_score(target_relevance, relevance)))

        self.logger.info("proximity table %s successfully built for %s", self.proximity_results, semantic_signature)

        if ignored_files is not None:
            self.logger.info('Trimming files: %s', ignored_files)
            self.proximity_results = self._trim_results(ignored_files)

        self._sort_results(sort_criteria, minimum_match_number)

        return self

    def _trim_results(self, ignored_files):
        result = dict((target_file, scored_topic) for target_file, scored_topic in self.proximity_results.items()
                      if target_file not in ignored_files)
        return result

    def _sort_results(self, sort_criteria, minimum_match_number):
        """

        :param sort_criteria:
        :param minimum_match_number:
        :return:
        """
        sorting_label = ""
        self.logger.info("[_sort_results] building results dictionary with minimum match: %s", minimum_match_number)
        self.proximity_results = dict((k, v) for k, v in self.proximity_results.items()
                                      if len(v) >= minimum_match_number)
        self.logger.debug("[_sort_results] results dictionary: %s", self.proximity_results)

        if sort_criteria is None:
            self.logger.info("[_sort_results] No sorting criteria provided, leaving dictionary unordered.")
            self.proximity_results = list(self.proximity_results.iteritems())
        elif sort_criteria == ProximityFinder.PROXIMITY_SCORE:
            sorting_label = "proximity score"
            self.proximity_results = self.sort_results_by_proximity_score()
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
    def get_proximity_score(matching_file_info):
        return sum([score for topic, score in matching_file_info])

    def sort_results_by_proximity_score(self):
        sorted_keys = sorted(self.proximity_results.iteritems(), key=lambda (k, v): self.get_proximity_score(v),
                             reverse=True)
        return sorted_keys

    @staticmethod
    def get_number_matches(matching_file_info):
        """

        :param matching_file_info:
        :return:
        """
        return len(matching_file_info)

    def sort_results_by_number_match(self):
        """

        :return:
        """
        sorted_keys = sorted(self.proximity_results.iteritems(), key=lambda (k, v): self.get_number_matches(v),
                             reverse=True)
        return sorted_keys

    @staticmethod
    def get_number_high(matching_file_info):
        """

        :param matching_file_info:
        :return:
        """
        return len([topic for topic, relevance in matching_file_info if relevance == 10000])

    def sort_results_by_number_high(self):
        """

        :return:
        """
        sorted_keys = sorted(self.proximity_results.iteritems(), key=lambda (k, v): self.get_number_high(v),
                             reverse=True)
        return sorted_keys

    @classmethod
    def compute_proximity_score(cls, target_relevance, relevance):
        # H/H
        if target_relevance == relevance and target_relevance == 'H':
            return 10000
        # N/N
        if target_relevance == relevance and target_relevance == 'N':
            return 100
        # H/N or N/H
        return 1


if __name__ == '__main__':
    logging.basicConfig(filename="proximity_finder.log", filemode="w",
                        level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
