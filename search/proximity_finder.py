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
        """

        :param topics_index:
        :param topics_occurrences_index:
        :param files_index:
        :return:
        """
        logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        self.topics_index = topics_index
        self.topics_occurrences_index = topics_occurrences_index
        if files_index is not None:
            self.files_index = files_index

        self.proximity_results = {}

    def build_proximity_results(self, semantic_signature, sort_criteria=None, minimum_hrt_match_number=0,
                                required_topics=None, ignored_files=None, hf=None, b=0):
        """

        :param b:
        :param hf:
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

        if hf is not None:
            self._paginate(hf, b)

        if sort_criteria is not None:  # TODO: fix this!!!
            self._insert_global_proximity_score(semantic_signature)

        return self

    def _insert_global_proximity_score(self, semantic_signature):
        """

        :param semantic_signature:
        :return:
        """
        scored_results = list()
        for result in self.proximity_results:
            f = result[0]
            scored_topics = result[1]
            global_score = get_total_proximity_score(scored_topics, semantic_signature)
            scored_results.append((f, scored_topics, global_score))
        self.proximity_results = scored_results
        return self

    def _paginate(self, hf, b=0):
        """

        :param hf:
        :param b:
        :return:
        """
        self.proximity_results = self.proximity_results[b:b+hf]

    def _trim_matching_files(self, relevant_files, required_topics):
        """

        :param relevant_files:
        :param required_topics:
        :return:
        """
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
        """

        :param relevant_file:
        :param topic:
        :return:
        """
        assert self.files_index is not None
        self.logger.debug('Looking for topic:%s in file:%s', topic, relevant_file)
        self.logger.debug('self.files_index.index[f]:%s', self.files_index.index[relevant_file[0]])

        return topic in [t for t, _ in self.files_index.index[relevant_file[0]]]

    def _trim_results(self, ignored_files, minimum_hrt_match_number):
        """Removes unwanted files from proximity_results.

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
    """

    :param scored_topics:
    :param semantic_signature:
    :return:
    """
    scores = [score for _, _, _, score in scored_topics]
    return get_proximity_score(scores, semantic_signature)


def get_proximity_score(scores, semantic_signature=None):
    """

    :param scores:
    :param semantic_signature:
    :return:
    """
    result = 0
    for score in scores:
        result += score
    if semantic_signature is None:
        return result
    else:
        max_possible_score = get_max_score(semantic_signature)
        return result*100/max_possible_score


def get_max_score(semantic_signature):
    """

    :param semantic_signature:
    :return:
    """
    total = 0
    for topic, relevance in semantic_signature:
        if relevance == 'N':
            total += ProximityScore.N_N
        if relevance == 'H':
            total += ProximityScore.H_H
    return total


def jsonify(proximity_results):
    """

    :param proximity_results:
    :return:
    """
    jsonified_results = list()
    for elem in proximity_results:
        f = elem[0]
        details = elem[1]
        details = [dict(zip(['topic', 'lbl_en', 'lbl_fr', 'score'], tup)) for tup in details]
        proximity = elem[2]
        result = dict()
        result['filename'] = f
        result['semantic_signature'] = details
        result['proximity'] = proximity
        jsonified_results.append(result)

    return jsonified_results

if __name__ == '__main__':
    logging.basicConfig(filename="proximity_finder.log", filemode="w",
                        level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
