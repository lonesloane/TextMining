import logging
import shelve

from indexfiles.loader import FilesDatesIndex, TopicsOccurrencesIndex


class TopicsFrequencyExtractor:
    LOG_LEVEL_DEFAULT = logging.DEBUG

    def __init__(self, topics_occurrences_index_filename, files_dates_index_filename):
        logging.basicConfig(level=TopicsFrequencyExtractor.LOG_LEVEL_DEFAULT,
                            format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        self._topics_frequency_index = {}
        self._topics_occurrences_index = TopicsOccurrencesIndex(topics_occurrences_index_filename).index
        self._files_dates_index = FilesDatesIndex(files_dates_index_filename)

    def build(self):
        for topic in self._topics_occurrences_index:
            topic_details = self._topics_occurrences_index[topic]
            for detail in topic_details:
                filename = detail[0]
                occurrence_date = self._files_dates_index.get_date_for_file(filename)
                if topic in self._topics_frequency_index:
                    self._topics_frequency_index[topic].append(occurrence_date)
                else:
                    self._topics_frequency_index[topic] = [occurrence_date]
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

    def export_as_csv(self, csv_filename):
        nl = ''
        with open(csv_filename, mode='w') as csv:
            for topic, dates in self._topics_frequency_index.items():
                self.logger.debug('topic: %s - dates: %s', topic, dates)
                self.logger.debug(topic+","+",".join([date.isoformat() for date in dates]))
                csv.write(nl+topic+","+",".join([date.isoformat() for date in dates]))
                nl = '\n'


def main():
    pass

if __name__ == '__main__':
    main()
