import index.loader as loader


def validate_topics_occurrences_index(topics_occurrences_index):
    """

    :param topics_occurrences_index:
    :return:
    """
    duplicate_files = []
    idx = 0
    print "%s topics to validate" % len(topics_occurrences_index)
    for topic, files_list in topics_occurrences_index.iteritems():
        idx += 1
        file_names = []
        for file_name, relevance in files_list:
            if file_name not in file_names:
                file_names.append(file_name)
            else:
                duplicate_files.append((topic, file_name))
                print 'File %s found multiple times for topic %s' % (file_name, topic)
        if idx % 10 == 0:
            print "%s topics processed" % idx

    print 'Found %s duplicate files' % len(duplicate_files)
    return duplicate_files


def validate_files_index(files_index):
    """

    :param files_index:
    :return:
    """
    duplicate_topics = []
    idx = 0
    for file_name, signature in files_index.iteritems():
        idx += 1
        uri_list = []
        for uri, relevance in signature:
            if uri not in uri_list:
                uri_list.append(uri)
            else:
                duplicate_topics.append((uri, file_name))
                print 'URI %s found multiple times for file %s' % (uri, file_name)

        if idx % 100 == 0:
            print "%s files processed..." % idx

    print 'Found %s duplicate topics' % len(duplicate_topics)
    return duplicate_topics


def validate_topics_index(topics_index):
    print '%s topics found in index' % len(topics_index)
    lbl_en, lbl_fr = topics_index['19']
    print (lbl_en, lbl_fr)


def validate_topics_index_highly(topics_index):
    print '%s topics found in index' % len(topics_index)
    for topic, details in topics_index.iteritems():
        print topic, details


def validate_typeahead_index(typeahead_index):
    """

    :param typeahead_index:
    :return:
    """
    root = 'research and'
    print '%s elements in typeahead index' % len(typeahead_index)
    print 'look up for %s:\n%s' % (root, typeahead_index[root])


def validate_typeahead_index_highly(typeahead_index):
    """

    :param typeahead_index:
    :return:
    """
    root = 'research'
    print '%s elements in typeahead index' % len(typeahead_index)
    print 'look up for %s:\n%s' % (root, typeahead_index[root])


def main():
    choice = 'typeahead_highly'

    if choice == 'files':
        # load files index
        files_index_filename = '../output/Files_Index'
        index = loader.FilesIndex(files_index_filename).index
        validate_files_index(index)
    if choice == 'occurrences':
        topics_occurrences_index_filename = '../output/Topics_Occurrences_Index'
        index = loader.TopicsOccurrencesIndex(topics_occurrences_index_filename).index
        validate_topics_occurrences_index(index)
    if choice == 'typeahead':
        typeahead_index_filename = '../output/Topics_Typeahead_Index'
        index = loader.TopicsTypeAheadIndex(typeahead_index_filename).index
        validate_typeahead_index(index)
    if choice == 'typeahead_highly':
        typeahead_index_filename = '../output/Topics_Typeahead_Index_H'
        index = loader.TopicsTypeAheadIndex(typeahead_index_filename).index
        validate_typeahead_index_highly(index)
    if choice == 'topics':
        topics_index_filename = '../output/Topics_Index'
        index = loader.TopicsIndex(topics_index_filename).index
        validate_topics_index(index)
    if choice == 'topics_highly':
        topics_index_filename = '../output/Topics_Index_H'
        index = loader.TopicsIndex(topics_index_filename).index
        validate_topics_index_highly(index)

if __name__ == '__main__':
    main()
