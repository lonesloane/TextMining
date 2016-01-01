import search.semantic_query as semantic


def chose_topic(processor, topic_id):
    new_topic_chosen = False
    target_topic = ''
    while not new_topic_chosen:

        print "What topic are you looking for? (Press return to start a new search)"
        target_topic = raw_input(">> ")
        if len(target_topic) == 0:
            return '', -1  # forces a restart

        # First off, find the topic id
        topic_id = processor.get_topic_id_from_label(target_topic)
        if topic_id is None:
            print "Sorry, this topic does not exist, please choose another topic."
        else:
            new_topic_chosen = True
            print "searching for documents related to topic: %s" % target_topic

    return target_topic, topic_id


def main():
    processor = semantic.QueryProcessor()

    topics = []
    topic_id = None
    while True:
        target_topic, topic_id = chose_topic(processor, topic_id)
        if target_topic == '' and topic_id == -1:
            topics = []
            topic_id = None
            print 'Topics list cleared.\nStarting new search'
            continue
        else:
            topics.append(topic_id)

        result_files, result_topics = processor.execute(topics)

        print "Found %s files matching topic(s) %s" % (len(result_files), topics)
        print "Found %s topics co_occurring with topic(s) %s" % (len(result_topics), topics)


if __name__ == "__main__":
    main()
