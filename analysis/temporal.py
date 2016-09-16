import ConfigParser
import logging
import os
import shelve

from indexfiles.loader import FilesDatesIndex, TopicsOccurrencesIndex, TopicsIndex


def average(_list):
    return sum(_list)/len(_list)


class Frequency:
    def __init__(self):
        pass

    ANNUAL = 'annual'
    MONTHLY = 'monthly'


class TopicsFrequencyExtractor:

    def __init__(self, topics_occurrences_index_filename, files_dates_index_filename,
                 topics_index_filename, highly_relevant_only=True):
        self.logger = logging.getLogger(__name__)

        self._highly_relevant_only = highly_relevant_only
        self._min_year = 0
        self._max_year = 0
        self._topics_frequency_index = {}
        self._topics_annual_frequencies = {}
        self._topics_monthly_frequencies = {}
        self._topics_occurrences_index = TopicsOccurrencesIndex(topics_occurrences_index_filename).index
        self._files_dates_index = FilesDatesIndex(files_dates_index_filename)
        self._topics_index = TopicsIndex(topics_index_filename).index

    def build_index(self, target_frequency):
        self.extract_dates_for_topics()

        if target_frequency is Frequency.ANNUAL:
            self.logger.debug('Filling annual frequencies')
            self.fill_annual_frequencies()
        elif target_frequency is Frequency.MONTHLY:
            self.logger.debug('Filling monthly frequencies')
            self.fill_monthly_frequencies()
        else:
            raise ValueError('Invalid target frequency specified: '+target_frequency)

    def extract_dates_for_topics(self):
        for topic in self._topics_occurrences_index:
            self.logger.debug('processing topic %s', topic)
            topic_details = self._topics_occurrences_index[topic]
            self.logger.debug('details found for topic %s: %s', topic, topic_details)
            for detail in topic_details:
                filename = detail[0]
                relevance = detail[1]
                if self._highly_relevant_only and relevance == 'N':
                    continue
                occurrence_date = self._files_dates_index.get_date_for_file(filename)
                self.update_min_max_year(occurrence_date)
                self.logger.debug('occurrence date: %s', occurrence_date)
                if topic in self._topics_frequency_index:
                    self._topics_frequency_index[topic].append(occurrence_date)
                else:
                    self._topics_frequency_index[topic] = [occurrence_date]
            if topic in self._topics_frequency_index and len(self._topics_frequency_index[topic]) > 0:
                self._topics_frequency_index[topic].sort()

    def shelve_index(self, output_index_filename):
        """Save the index on the file system.

        :param output_index_filename:
        :return:
        """
        self.logger.info("Shelving %s", output_index_filename)
        d = shelve.open(output_index_filename)
        d["Corpus"] = self._topics_frequency_index
        d.close()

    def export_as_csv(self, csv_filename, frequency=Frequency.ANNUAL):
        nl = ''
        if frequency is Frequency.ANNUAL:
            index = self._topics_annual_frequencies
        elif frequency is Frequency.MONTHLY:
            index = self._topics_monthly_frequencies
        else:
            raise ValueError('Invalid value for frequency: %s', frequency)
        with open(csv_filename, mode='w') as csv:
            header = 'topic_id,topic_label,'+','.join([str(year)
                                                       for year in range(self._min_year, self._max_year+1)])
            csv.write(header+'\n')
            for topic, occurrences in index.items():
                topic_label = self._topics_index[topic][0]
                self.logger.debug('topic: (%s) %s - occurrences: %s', topic, topic_label, occurrences)
                self.logger.debug(topic+','+topic_label+","+",".join(
                        [str(occurrence) for _, occurrence in occurrences.items()]))
                try:
                    csv.write(nl+topic+','+topic_label+","+",".join(
                            [str(occurrence) for _, occurrence in occurrences.items()]))
                except:
                    self.logger.debug('pb with topic %s label %s', topic, topic_label)
                nl = '\n'

    def fill_annual_frequencies(self):
        for topic, dates in self._topics_frequency_index.iteritems():
            occurrences = dict([(year, 0) for year in range(self._min_year, self._max_year+1)])
            for occurrence in dates:
                year = occurrence.year
                occurrences[year] += 1
            self._topics_annual_frequencies[topic] = occurrences

    def fill_monthly_frequencies(self):
        pass

    def update_min_max_year(self, occurrence_date):
        year = occurrence_date.year
        if year < self._min_year or self._min_year == 0:
            self._min_year = year
        if year > self._max_year or self._max_year == 0:
            self._max_year = year


def main():
    # Get configuration parameters
    basedir = os.path.abspath(os.path.dirname(__file__))
    config = ConfigParser.SafeConfigParser()
    config.read(os.path.join(basedir, 'corpus.conf'))
    # config.read(os.path.join(basedir, 'corpus_test.conf'))

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

    output_dir = config.get('MAIN', 'output_dir')
    topics_occurrences_index = os.path.join(output_dir, config.get('MAIN', 'topics_occurrences_index_filename'))
    files_dates_index = os.path.join(output_dir, config.get('MAIN', 'files_dates_index_filename'))
    topics_index = os.path.join(output_dir, config.get('MAIN', 'topics_index_filename'))

    frequency_extractor = TopicsFrequencyExtractor(topics_occurrences_index_filename=topics_occurrences_index,
                                                   files_dates_index_filename=files_dates_index,
                                                   topics_index_filename=topics_index)
    frequency_extractor.build_index(Frequency.ANNUAL)
    csv_file = os.path.join(output_dir, 'Topics_Frequency.csv')
    frequency_extractor.export_as_csv(csv_filename=csv_file)

if __name__ == '__main__':
    pass
    #main()
