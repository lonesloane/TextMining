import logging
import logging.config


class SortBy:
    """

    """
    PROXIMITY_SCORE = 0
    NB_HIGH_MATCHES = 1
    TOTAL_MATCHES = 2

    def __init__(self):
        pass


class ProximityScore:
    """

    """
    H_H = 10000
    N_N = 100
    H_N = N_H = 1

    def __init__(self):
        pass


class ProximityFinder:
    """

    """

    def __init__(self, topics_index, topics_occurrences_index, files_index=None):
        logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        self.topics_index = topics_index
        self.topics_occurrences_index = topics_occurrences_index
        if files_index is not None:
            self.files_index = files_index

        self.proximity_results = {}
        self.raw_results = []

    def build_proximity_results(self, semantic_signature, sort_criteria=None, minimum_hrt_match_number=0,
                                    required_topics=None, ignored_files=None):
        """

        :param required_topics:
        :param semantic_signature:
        :param sort_criteria:
        :param ignored_files:
        :param minimum_hrt_match_number:
        :return:
        """
        self.proximity_results = {}

        for target_topic, target_relevance in semantic_signature:
            target_topic_lbl_en, target_topic_lbl_fr = self.topics_index.get_labels_for_topic_id(target_topic)
            relevant_files = self.topics_occurrences_index.get_files_for_topic(target_topic)
            if required_topics is not None:
                relevant_files = self._trim_matching_files(relevant_files, required_topics)
            self.logger.debug("Matching files found for topic %s: %s", target_topic, relevant_files)
            for matching_file, relevance in relevant_files:
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

        if sort_criteria is not None:
            self._sort_results(sort_criteria)

        return self

    def _trim_matching_files(self, relevant_files, required_topics):
        trimmed_files = []
        for relevant_file in relevant_files:
            ok = True
            for topic in required_topics:
                if not self._contains_topic(relevant_file, topic):
                    ok = False
                    break
            if ok:
                trimmed_files.append(relevant_file)
        return trimmed_files

    def _contains_topic(self, relevant_file, topic):
        assert self.files_index is not None
        self.logger.debug('Looking for topic:%s in file:%s', topic, relevant_file)
        self.logger.debug('self.files_index.index[f]:%s', self.files_index.index[relevant_file[0]])

        return topic in [t for t, _ in self.files_index.index[relevant_file[0]]]

    def _trim_results(self, ignored_files, minimum_hrt_match_number):
        """
        Removes unwanted files from proximity_results.

        :param ignored_files: list of files to ignore (i.e. files for which the proximity is computed)
        :param minimum_hrt_match_number: minimum number of highly relevant terms match required
        :return:
        """
        if ignored_files is None or len(ignored_files) == 0:
            ignored_files = []
        self.proximity_results = dict((target_file, scored_topic)
                                      for target_file, scored_topic in self.proximity_results.items()
                                      if target_file not in ignored_files and
                                      self._has_minimum_hrt_matches(scored_topic, minimum_hrt_match_number))
        return self

    @staticmethod
    def _has_minimum_hrt_matches(scored_topic, minimum_hrt_match_number):
        """

        :param scored_topic:
        :param minimum_hrt_match_number:
        :return:
        """
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
        if sort_criteria == SortBy.PROXIMITY_SCORE:
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

        self.logger.info("Results sorted by %s", sorting_label)

        return self

    @staticmethod
    def get_proximity_score(matching_file_info):
        """

        :param matching_file_info:
        :return:
        """
        return sum([score for topic, lbl_en, lbl_fr, score in matching_file_info])

    def sort_results_by_proximity_score(self):
        """

        :return:
        """
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
        """

        :param target_relevance:
        :param relevance:
        :return:
        """
        # H/H
        if target_relevance == relevance and target_relevance == 'H':
            return ProximityScore.H_H
        # N/N
        if target_relevance == relevance and target_relevance == 'N':
            return ProximityScore.N_N
        # H/N or N/H
        return ProximityScore.H_N


def get_total_proximity_score(scored_topics, semantic_signature=None):
    result = 0
    for _, _, _, score in scored_topics:
        result += score
    if semantic_signature is None:
        return result
    else:
        max_possible_score = get_max_score(semantic_signature)
        return result*100/max_possible_score


def get_max_score(semantic_signature):
    total = 0
    for topic, relevance in semantic_signature:
        if relevance == 'N':
            total += ProximityScore.N_N
        if relevance == 'H':
            total += ProximityScore.H_H
    return total


if __name__ == '__main__':
    logging.basicConfig(filename="proximity_finder.log", filemode="w",
                        level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
