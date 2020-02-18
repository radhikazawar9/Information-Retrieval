"""
Assignment 2 Group 12

Radhika Zawar s3734939
Parvi Verma s3744398
"""

import sys
import struct
from index import normalise as norm
from index import open_stoplist
import argparse
import math
import time
from pathlib import Path
from math import log
from heap import Heap
import traceback

start_time = int(round(time.time() * 1000)) #calculate the starting time
list_map = []    # List to read doc id and docnum from map file
hash_lex = {}    # Hashmap to read position of query in lexicon file
hash_acc = {}    # Hashmap to store accumulators
heapList = []   # List to store min heap

# HashMap to store Doc ID and its BM25 score for each query term
doc_Score = {}

# Constants for BM25 function
N, k1, b = 0, 0, 0

"""
to calculate partial similarity score
"""

def partial_accumulator(id, ft, fdt, list_map, Al):

    k1 = 1.2                        # constant parameter
    b = 0.75                        # constant parameter
    N = len(list_map)               # Number of documents in the collection
    Ld = float(list_map[id][2])    # Ld and AL are the document length and average document length

    K = k1 * ((1 - b) + ((b * Ld) / Al))

    #fdt: number of occurrences of t in d
    #ft: number of documents containing term t
    # BM25:  similarity function
    BM25 = math.calculateBM25(ft, K, fdt)
    return BM25

""" calculating and returning simple Similarity
score using BM 25 similarity function
"""
def calculateBM25(ft, K, fdt):
    # Calculates BM25 function score
    result = log((N-ft+0.5)/(ft+0.5))*(((k1+1)*fdt)/(K+fdt))
    return result


"""
opening map file to retrieve document number
Assignment 1 implementation
"""
def open_mapfile(map_file):
    ## Opening map file
    list_map = []                               # List to read doc id and docnum from map file
    with open(map_file, 'r') as file:           #reading map file from the local memory
        for line in file:
            line = line.rstrip().split(" ")     # splitting at space and removing space at the end of chars
            list_map.append([line[1], float(line[2])]) # saving in the list
    return list_map                             # returning list to lookup for query


"""
opening lexicon file to locate if query
term is present in lexicon resources
Assignment 1 implementation
"""
def open_lexicon(lexicon_file):
    hash_lex = {}                               # Hashmap to read position of query in lexicon file

    with open(lexicon_file, 'r') as file:       # reading lexicon file
        for line in file:
            line = line.rstrip().split(" ")     # splitting on space and stripping tailing whitespace
            hash_lex[line[0]] = line[1]         # saving in the hashmap key-value pair
    return hash_lex                             # returning hashmap for query search lookup


"""
to locate query term and query location in documents for implementing
phrase search advance feature
"""
def seek_query_occurence(query_term, inverted_list, hash_lex, list_map, BM25):
    if query_term not in hash_lex:                  # if query term is not located in lexicon hashmap
        print ('This query term is not in the record.')

    elif query_term in hash_lex:                    # if query term is present in the hashmap

        value = int(hash_lex[query_term])           # reading query term from hashmap key-value pair

        with open(inverted_list,"rb") as f:         # opening inverted list file

            f.seek(value,0)                         # seek() sets the file's current position at the offset
            #value = struct.unpack('>i', f.read(4))[0]
            #print (value)

            def found():                            # function found to read data from invlists file
                value = struct.unpack('>i', f.read(4))[0]
                #print value
                return value

            length_list = found()  # reading term frequency in a documemnt

            ft = length_list       #frequency of the term

            if not BM25:            # if BM25 = false that phrase search is requested
                doc_occurences = {} # store all occurences

            while length_list > 0 : # if entry for perticular query is located

                doc_num = found()   # reading term locations on the loop of total term that is term freq

                doc_row = list_map[doc_num] #reading term from map file

                id = doc_row[0]     # to read binary data of document id to lookup in map file
                fdt = found()       # reading term locations on the loop of total term that is term freq

                # reference https://rosettacode.org/wiki/Inverted_index#Python
                if BM25:
                    K = doc_row[1]
                    score = float(str(round(calculateBM25(ft, K, fdt),4)))
                    # adding scores to documents
                    if id in doc_Score:
                        doc_Score[id] += score
                    else:
                        doc_Score[id] = score

                    # if it has item read the binary value
                    for something in range(fdt):
                        found()

                else:
                    # if phrase search is requested
                    location = []   # to store locations
                    for something in range(fdt):    # read location of query term
                        location.append(found())    # store ocation
                    doc_occurences[doc_num] = location  # store in accurences list

                length_list -= 1    #decrese length_list to iterate

            if BM25:
                return None
            else:
                return doc_occurences #if phrase search is requested send the term location data


"""
this function has implementation of OKAPI BM 25 similarity feature
to invoke this function following query should be used
./search -BM25 -q <query-label> -n <num-results> -l <lexicon> -i <invlists>
-m <map> [-s <stoplist>] <queryterm-1> [<queryterm-2> ... <queryterm-N>]
"""

def function_bm25(args, queries, lexicon, map):

    global N, k1, b
    doc_length = len(map)
    N = len(map)
    k1 = 1.2
    b = 0.75

    number_results = args.num_rank  # total number of expected results
    query_terms = args.queryterms   # the index label for the query

    # get all accurences for each query
    for qterms in queries:
        seek_query_occurence(qterms, args.invlists, lexicon, map, BM25 = True)

    # initialise heap to store occurences
    minHeap = Heap()

    for term in doc_Score:
        # checking hashmap of document and query and the score for the query and sorting to get N results
        if len(minHeap) == number_results:
            minHeap.push(doc_Score[term], term, replace = True)
        else:
            minHeap.push(doc_Score[term], term)

    result_set = []
    # reading minHeap to get highest result set of N terms
    while True:
        try:
            val = minHeap.next()
            result_set.append((val,doc_Score[val]))
        except StopIteration:
            break

    # sorted output of okapi BM 25
    for i, value in enumerate(reversed(result_set)):
        print number_results," ", value[0], " ", i + 1, " ", value[1]


"""
Advance search feature to provide phrase search functionality.
this is extension to the ranked retrieval implementation to support phrase queries
can be invoked with following command
python search.py --phrase-search -q 100 -l lexicon -i invlists -m map  ancient city ruins
"""

def function_pharse_search(args, queries, lexicon, map):
    queryterm = args.label

    query_loc_list = []         # to store docId and locations for each term in doc
    final_query_loc_list = []   # to store final outcome of insection documents where phrase is present
    win_list = []               # to store intermendiate results


    for q in queries:
        # finding query occurences using earlier implementation
        occ = seek_query_occurence(q, args.invlists, lexicon, map, BM25 = False)
        query_loc_list.append(occ)  # storing occurences along with term location

    # check if we have some valid results
    if query_loc_list and query_loc_list[0] and None not in query_loc_list:

        # finding intersection of the Documents
        # only considering common documents for following analysis
        winner = query_loc_list[0].keys()
        #print winner
        #print type(winner)
        for val in query_loc_list:
            #print winner
            #print val.keys()
            winner = set(winner) & set(val.keys())
            #print list(winner)

        # checking if the query terms are adjusent
        for val in winner:
            #print val
            for t in range(1, len(queries)):
                # comparing location of the term to the location of its previous term to find output
                # actual document which has the phrase
                comp = query_loc_list[t][val]
                prev = query_loc_list[t-1][val]
                win_list = list(comp)

                # if locations are not adjusent then discard that doc
                for item in comp:
                    if(item - 1) not in prev:
                        win_list.remove(item)

                # the documents which actually has the qeury
                query_loc_list[t][val] = win_list

            if query_loc_list[-1][val]: # valid documents are stored in the final output
                final_query_loc_list.append((val, len(query_loc_list[-1][val])))

    else: # if we dont have any document with the term
        pass

    if final_query_loc_list:    # sorting on number of occurences for better result
        final_query_loc_list.sort(key = lambda x: x[1], reverse = True)

        # final output of phrase search retrieval feature
        for documents in final_query_loc_list:
            print ('{} {} {}'.format(queryterm, map[documents[0]][0], documents[1]))

    else: # if we have no final output
        pass

""""
reading command from command line
where command is like
"python search.py -BM25 -q <query-label> -n <num-results> -l <lexicon> -i<invlists> -m <map> [-s <stoplist>] <queryterm-1> [<queryterm-2> ... <queryterm-N>]"
example: python search.py -BM25 -q 114 -n 5 -l lexicon -i  invlists -m map -s /home/inforet/a1/stoplist woode
"""
def start(start_args):
    # Handle arg vars
    try:
        parser = argparse.ArgumentParser()
        ranker = parser.add_mutually_exclusive_group(required=True)

        ranker.add_argument('-BM25', '--BM25', action='store_true', default = False,
                            help = 'Similarity Type')     # compulsary argument to know similarity metric
        ranker.add_argument('--phrase-search', action='store_true', default=False,
                            help='Shows results that match the exact phrase searched')
        parser.add_argument('-q','--label', type=int, required = True,
                            help='The Query Label')  # compulsary argument to know query label
        parser.add_argument('-n', '--num_rank', type=int ,
                            help='Number of Top Ranked Documents') # compulsary argument to know number of top ranked documents
        parser.add_argument('-l', '--lexicon', type=str, required = True,
                            help='A path to a file containing lexicon') # compulsary to get path of lexicon file
        parser.add_argument('-i','--invlists', type=str, required = True,
                            help='A path to a file containing invlists') # compulsary to get path of invlists file
        parser.add_argument('-m','--map', type=str, required = True,
                            help='A path to a file containing map') # compulsary to get path of map file
        parser.add_argument('-s', '--stoplist', type=str, required = False,
                            help='A path to a file containing a list of stopwords') # optional to get path of stopword file
        parser.add_argument('queryterms', nargs='+', help='Query Terms')                       # Taking query terms
        args = parser.parse_args(start_args)                                          # argument parser

        if(args.BM25 and args.num_rank is None):
            parser.error('BM25 query requires numeber of result output [ --n || --num_rank] ')

        elif (args.phrase_search and args.num_rank is not None):
            parser.error('Phrase query does not have limited output. Please remove --n, and --num_rank argument')

        lexicon_file = open_lexicon(args.lexicon)        # reading contents of lexicon file
        map_file = open_mapfile(args.map)                # reading contents of map file

        if args.stoplist:
            path = "/home/inforet/a2/"
            stoplist_file = open_stoplist(path, args.stoplist)
        else:
            stoplist_file = None
        query_list = norm(' '.join(args.queryterms), r'[^a-z0-9\ ]+', case=True, stops=stoplist_file)

        if not query_list:                                # if no query term is given
            print ('search query is missing!')

        # finding relevant document on BM 25 similarity function
        if args.BM25:
            function_bm25(args, query_list, lexicon_file, map_file)

        # finding relevant document on phrase search retrieval feature
        elif args.phrase_search:
            function_pharse_search(args, query_list, lexicon_file, map_file)

    except OSError as OSerr:                            # if OSError occurs
        print('{}\nBad Error'.format(OSerr))

    except IndexError:                                  # if order of command is bad
        print('No meaningfull parameters')
        traceback.print_exc()

# online source //stackoverflow.com
if __name__ == '__main__':
    start_time = time.time()

    start(sys.argv[1:])

    print("Running time: %d ms" % ((time.time() - start_time) * 1000))
