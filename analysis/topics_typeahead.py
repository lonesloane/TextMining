import json
import logging

from index.loader import TopicsIndex


class TopicsTypeaheadBuilder:
    LOG_LEVEL_DEFAULT = logging.INFO

    def __init__(self, input_index_filename=None):
        logging.basicConfig(level=TopicsTypeaheadBuilder.LOG_LEVEL_DEFAULT,
                            format='%(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)

        self._topics = list()
        self._topics_index = None
        if input_index_filename is not None:
            self._topics_index = TopicsIndex(input_index_filename).index

    def build(self):
        for topic_id in self._topics_index:
#            topic = dict()
#            topic['topic_id'] = topic_id
#            topic['value'] = self._topics_index[topic_id][0]
#            topic['tokens'] = tokenize(self._topics_index[topic_id][0])
#            self._topics.append(topic)
            self._topics.append(self._topics_index[topic_id][0])
        self.logger.debug("Topics json list: %s", json.dumps(self._topics))

    def save_index(self, topics_typeahead_json_filename):
        with open(topics_typeahead_json_filename, 'w') as outfile:
            json.dump(self._topics, outfile)


def tokenize(sentence):
    """
    Simplistic tokenize function (to be improved later...)
    :param sentence:
    :return:
    """
    return sentence.split(' ')


def main():
    logging.basicConfig(filename="../output/typeahead_json_builder.log", filemode="w",
                        level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # topics_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Index_H'
    # topics_typeahead_json_filename = '/home/stephane/Playground/PycharmProjects/TextMining/tests/testOutput/Test_Topics_Typeahead_Json_H'
    topics_index_filename = '/home/stephane/Playground/PycharmProjects/TextMining/output/Topics_Index_H'
    topics_typeahead_json_filename = '/home/stephane/Playground/PycharmProjects/TextMining/output/Topics_Typeahead_Json_H'
    index_builder = TopicsTypeaheadBuilder(input_index_filename=topics_index_filename,)
    index_builder.build()
    index_builder.save_index(topics_typeahead_json_filename)


if __name__ == '__main__':
    main()
