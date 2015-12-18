from search.semantic_query import QueryProcessor


def main():
    processor = QueryProcessor()

    print "What topic are you looking for?"
    target_topic = raw_input(">> ")

    # First off, find the topic id
    topic_id = processor.get_topic_id_from_label(target_topic)
    if topic_id is None:
        print "Sorry, this topic does not exist, please choose another topic."
    else:
        print "searching for documents related to topic: %s" % target_topic

    result_files, result_topics = processor.execute(topic_id)

    print "Found %s files matching topic %s" % (len(result_files), target_topic)
    print "Found %s topics co_occurring with topic %s" % (len(result_topics), target_topic)

if __name__ == "__main__":
    main()
