import index.loader as loader


def validate_topics_occurrences_index(topics_occurrences_index):
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


def main():
    choice = 'files'
    if choice == 'files':
        # load files index
        files_index_filename = '../output/Files_Index'
        files_index = loader.FilesIndex(index_filename=files_index_filename)._index
        validate_files_index(files_index)
    if choice == 'occurrences':
        topics_occurrences_index_filename = '../output/Topics_Occurrences_Index'
        topics_occurrences_index = loader.TopicsOccurrencesIndex(index_filename=topics_occurrences_index_filename)._index
        # print topics_occurrences_index['4437']
        validate_topics_occurrences_index(topics_occurrences_index)

if __name__ == '__main__':
    main()
