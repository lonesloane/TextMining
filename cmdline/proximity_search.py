import shelve

import search.proximity_finder as proximity


def get_topics_for_files(files_index, target_file):
    print "Looking for topics in file: %s" % target_file
    result_topics = []
    result_topics.extend([t for t, _ in files_index[target_file]])
    return sorted(result_topics)


def load_files_index():
    print "Loading files index"
    d = shelve.open("../output/Files_Index")
    index = d["Corpus"]
    d.close()
    print "Files index loaded successfully"
    return index


def main():
    finder = proximity.ProximityFinder()
    files_index = load_files_index()

    while True:
        print "What file are you looking for?"
        target_file = raw_input(">> ")

        # First off, find the list of topics associated to the file
        topics = get_topics_for_files(files_index, target_file)
        print "Nb topics found: %s %s" % (len(topics), topics)
        print "Minimum number of matches?"
        match_number = int(raw_input(">> "))

        if topics is None:
            print "Sorry, this file does not exist, please choose another file."
        else:
            print "searching documents semantically 'related' to: %s" % target_file
            results = finder.build_proximity_results(semantic_signature=topics,
                                                     minimum_match_number=match_number,
                                                     sort_criteria=proximity.ProximityFinder.NB_HIGH_MATCHES).proximity_results
            print "Found %s files 'related' to file %s" % (len(results), target_file)
            for i in range(len(results) if len(results)<20 else 20):
                print "File: %s - Details: %s" % (results[i][0], results[0][1])


if __name__ == '__main__':
    main()
