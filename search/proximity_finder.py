import logging
import logging.config
from index.loader import TopicsOccurrencesIndex, TopicsIndex


class SortBy:
    PROXIMITY_SCORE = 0
    NB_HIGH_MATCHES = 1
    TOTAL_MATCHES = 2

    def __init__(self):
        pass


class ProximityScore:
    H_H = 10000
    N_N = 100
    H_N = N_H = 1

    def __init__(self):
        pass


class ProximityFinder:
    """

    """
    TOPICS_INDEX_FILENAME_DEFAULT = "../output/Topics_Index"
    TOPICS_OCCURRENCES_INDEX_FILENAME_DEFAULT = "../output/Topics_Occurrences_Index"

    def __init__(self, topics_index_filename=None, topics_occurrences_index_filename=None):
        """

        :param topics_occurrences_index_filename:
        :return:
        """
        logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
        # logging.config.fileConfig('logging.conf')
        self.logger = logging.getLogger(__name__)

        self.proximity_results = {}
        self.raw_results = []

        if topics_index_filename is None:
            topics_index_filename = ProximityFinder.TOPICS_INDEX_FILENAME_DEFAULT
        self.topics_index = TopicsIndex(topics_index_filename)

        if topics_occurrences_index_filename is None:
            topics_occurrences_index_filename = ProximityFinder.TOPICS_OCCURRENCES_INDEX_FILENAME_DEFAULT
        self.topics_occurrences_index = TopicsOccurrencesIndex(topics_occurrences_index_filename)

    def build_proximity_results(self, semantic_signature, sort_criteria=None, minimum_hrt_match_number=0,
                                ignored_files=None):
        """

        :param semantic_signature:
        :param sort_criteria:
        :param ignored_files:
        :param minimum_hrt_match_number:
        :return:
        """
        self.proximity_results = {}

        for target_topic, target_relevance in semantic_signature:
            target_topic_lbl_en, target_topic_lbl_fr = self.topics_index.get_labels_for_topic_id(target_topic)
            matching_files = self.topics_occurrences_index.get_files_for_topic(target_topic)
            self.logger.debug("Matching files found for topic %s: %s", target_topic, matching_files)
            for matching_file, relevance in matching_files:
                if matching_file in self.proximity_results:
                    self.proximity_results[matching_file].append((target_topic,
                                                                  target_topic_lbl_en,
                                                                  target_topic_lbl_fr,
                                                                  self.compute_proximity_score(target_relevance,
                                                                                               relevance)))
                else:
                    self.proximity_results[matching_file] = [(target_topic,
                                                              target_topic_lbl_en,
                                                              target_topic_lbl_fr,
                                                              self.compute_proximity_score(target_relevance,
                                                                                           relevance))]

        self.logger.debug("proximity table %s successfully built for %s", self.proximity_results, semantic_signature)

        if ignored_files is not None or minimum_hrt_match_number != 0:
            self.logger.info('Keeping only files with at least %s high relevancy match.'
                             ' Ignoring files: %s', minimum_hrt_match_number, ignored_files)
            self._trim_results(ignored_files, minimum_hrt_match_number)

        self._sort_results(sort_criteria)

        return self

    def _trim_results(self, ignored_files, minimum_hrt_match_number):
        if ignored_files is None or len(ignored_files) == 0:
            ignored_files = []
        self.proximity_results = dict((target_file, scored_topic)
                                      for target_file, scored_topic in self.proximity_results.items()
                                      if target_file not in ignored_files and
                                      self._has_minimum_hrt_matches(scored_topic, minimum_hrt_match_number))
        return self

    @staticmethod
    def _has_minimum_hrt_matches(scored_topic, minimum_hrt_match_number):
        nb_high_match = 0
        for topic, _, _, score in scored_topic:
            if score == ProximityScore.H_H:
                nb_high_match += 1
            if nb_high_match >= minimum_hrt_match_number:
                return True
        return False

    def _sort_results(self, sort_criteria):
        """

        :param sort_criteria:
        :return:
        """
        sorting_label = ""
#        self.logger.info("[_sort_results] building results dictionary with minimum match: %s", minimum_match_number)
#        self.proximity_results = dict((k, v) for k, v in self.proximity_results.items()
#                                      if len(v) >= minimum_match_number)
#        self.logger.debug("[_sort_results] results dictionary: %s", self.proximity_results)

        if sort_criteria is None:
            self.logger.info("[_sort_results] No sorting criteria provided, leaving dictionary unordered.")
            self.proximity_results = list(self.proximity_results.iteritems())
        elif sort_criteria == SortBy.PROXIMITY_SCORE:
            sorting_label = "proximity score"
            self.proximity_results = self.sort_results_by_proximity_score()
        elif sort_criteria == SortBy.TOTAL_MATCHES:
            sorting_label = "total number of matches"
            self.proximity_results = self.sort_results_by_number_match()
        elif sort_criteria == SortBy.NB_HIGH_MATCHES:
            sorting_label = "number of highly relevant matches"
            self.proximity_results = self.sort_results_by_number_high()
        else:
            raise Exception("invalid sorting criteria: %s", sort_criteria)

        if sort_criteria is not None:
            self.logger.info("Results sorted by %s", sorting_label)

        return self

    @staticmethod
    def get_proximity_score(matching_file_info):
        return sum([score for topic, lbl_en, lbl_fr, score in matching_file_info])

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
        return len([topic for topic, lbl_en, lbl_fr, relevance in matching_file_info
                    if relevance == ProximityScore.H_H])

    def sort_results_by_number_high(self):
        """

        :return:
        """
        sorted_keys = sorted(self.proximity_results.iteritems(), key=lambda (k, v): self.get_number_high(v),
                             reverse=True)
        return sorted_keys

    @staticmethod
    def compute_proximity_score(target_relevance, relevance):
        # H/H
        if target_relevance == relevance and target_relevance == 'H':
            return ProximityScore.H_H
        # N/N
        if target_relevance == relevance and target_relevance == 'N':
            return ProximityScore.N_N
        # H/N or N/H
        return ProximityScore.H_N


if __name__ == '__main__':
    logging.basicConfig(filename="proximity_finder.log", filemode="w",
                        level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
