import logging

import search.proximity_finder as proximity
from index.loader import FilesIndex


def proximity_score(scored_topics):
    result = 0
    for _, _, _, score in scored_topics:
        result += score
    return result


def main():
    finder = proximity.ProximityFinder()
    files_index = FilesIndex("../output/Files_Index")

    while True:
        print "What file are you looking for?"
        target_file = raw_input(">> ")

        ignored_files = [target_file]
        # First off, find the list of topics associated to the file
        semantic_enrichment = files_index.get_enrichment_for_files(target_file)
        print "Nb topics found: %s %s" % (len(semantic_enrichment), semantic_enrichment)
        print "Minimum number of matches?"
        match_number = int(raw_input(">> "))

        if semantic_enrichment is None:
            print "Sorry, this file does not exist, please choose another file."
        else:
            print "searching documents semantically 'related' to: %s" % target_file
            results = finder.build_proximity_results(semantic_signature=semantic_enrichment,
                                                     minimum_match_number=match_number,
                                                     sort_criteria=proximity.SortBy.PROXIMITY_SCORE,
                                                     ignored_files=ignored_files).proximity_results
            print "Found %s files 'related' to file %s" % (len(results), target_file)
            for i in range(len(results) if len(results) < 20 else 20):
                print "File: %s - Proximity score: %s - Nb matches: %s" % (results[i][0],
                                                                           proximity_score(results[i][1]),
                                                                           len(results[i][1]))
                print "Matches: %s" % results[i][1]


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
    main()
