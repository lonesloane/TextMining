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
        if semantic_enrichment is None:
            print "Sorry, this file does not exist, please choose another file."
        else:
            print "Nb topics found: %s %s" % (len(semantic_enrichment), semantic_enrichment)
            print "Minimum number of HRT matches? (Highly Relevant Terms)"
            hrt_match_number = int(raw_input(">> "))
            print "searching documents semantically 'related' to: %s" % target_file
            results = finder.build_proximity_results(semantic_signature=semantic_enrichment,
                                                     minimum_hrt_match_number=hrt_match_number,
                                                     sort_criteria=proximity.SortBy.PROXIMITY_SCORE,
                                                     ignored_files=ignored_files).proximity_results
            print "Found %s files 'related' to file %s\n" % (len(results), target_file)
            for i in range(len(results) if len(results) < 20 else 20):
                print '--------------------------------------------------'
                print "File: %s - Proximity score: %s - Nb matches: %s" % (results[i][0],
                                                                           proximity_score(results[i][1]),
                                                                           len(results[i][1]))
                print '--------------------------------------------------'
                for topic_lbl, score in [(topic_lbl, score) for _, topic_lbl, _, score in results[i][1]]:
                    print "\t- %s: %s" % (topic_lbl, score)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
    main()
