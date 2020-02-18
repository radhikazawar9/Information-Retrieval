"""
Assignment 2 Group 12

Radhika Zawar s3734939
Parvi Verma s3744398
"""

import paramiko
from index import get_file
import subprocess
import sys
import os

"""
Variable definitions
"""
directory = 'evalution'     # directory name
path = '/home/inforet/a2'   # file path
TOPICS = 'topics'           # file name
QRELS = 'qrels'             # file name

topic_file = {}             # storage for input file
qrels_file = {}             # storage for input file
store_for_bm25   = {}       # BM 25 storage
store_for_phrase = {}       # phrase search storage
answer_list = 20            # restricting results
precision = 10              # rsestricting precision

"""
to print on console
"""
def print_data():
    # Console output
    print('     BM25     Results:      {}'.format(len(store_for_bm25[q])))
    print('     BM25     Precision:    {}'.format(precision_bm))
    print('     Phrase   Results:      {}'.format(len(store_for_phrase[q])))
    print('     Phrase   Precision:    {}'.format(precision_ph))
    print " "

"""
to write in file
This is designed to store 20 results to disk to later
prsent in the report
"""
def print_to_disk():
    # disk output
    with open('{}/{}PHRASE'.format(directory, q), 'w') as ph_out:
        for e in store_for_phrase[q]:
            REL = qrels_file[q]
            ph_out.write('{} {} {}\n'.format(*(e + (1 if (e[0] in REL and REL[e[0]]) else 0,))))

    with open('{}/{}BM25'.format(directory, q), 'w') as bm_out:
        for e in store_for_bm25[q]:
            REL = qrels_file[q]
            bm_out.write('{} {} {}\n'.format(*(e + (1 if (e[0] in REL and REL[e[0]]) else 0,))))


if __name__ == '__main__':
    # opening file using Asssignment 1 implented function
    opened_topic = get_file(path, TOPICS)   #reusing code of Assignment 1
    for topic in opened_topic:
        topic = topic.split()
        topic_file[topic[0]] = topic[1:]

    opened_qrels = get_file(path, QRELS)    #reusing code of Assignment 1
    for q in opened_qrels:
        q = q.split()

        if q[0] not in qrels_file:
            qrels_file[q[0]] = {}

        qrels_file[q[0]][q[2].lower()] = q[3] == '1' # 1 when matching

    # writing into or creating new folder to store result directory into root directory
    if not os.path.exists(directory):
        os.makedirs(directory)

    for q, t in topic_file.items():
        print(q, ' '.join(t))
        # Performing BM25 search
        bm25_command = 'python search.py --BM25 -q {} -n {} -l lexicon -i invlists -m map'
        bm25_command = bm25_command.format(q, answer_list).split() + t
        calling_bm25 = subprocess.check_output(bm25_command).decode('utf-8').splitlines() # Calling search.py
        calling_bm25 = calling_bm25[:-1]                                                  # Discarding time data
        data = []       #initialised list for data
        for i in calling_bm25:
            i = i.split()
            data.append( (i[1], i[3]) ) # Extracting needed data
        store_for_bm25[q] = data        # Storing for writing in file

        # Calculating P@10
        cal_rel = qrels_file[q]
        cal_result = store_for_bm25[q][0:precision]
        # Getting the number of relevant documents in this query
        rel_ans = sum([1 if (doc[0] in cal_rel and cal_rel[doc[0]]) else 0 for doc in cal_result])
        precision_bm = rel_ans/(len(cal_result) or 1) # to avoid math error

        # phrase search
        phrase_command = 'python search.py --phrase-search -q {} -l lexicon -i invlists -m map'
        phrase_command = phrase_command.format(q, answer_list).split() + t
        #calling search.py
        calling_phrase = subprocess.check_output(phrase_command).decode('utf-8').splitlines()
        calling_phrase = calling_phrase[:-1] # removing time data
        data = []
        for i in calling_phrase:
            i = i.split()
            data.append( (i[1], i[2]) )
        store_for_phrase[q] = data

        # Calculating P@10
        cal_rel = qrels_file[q]
        cal_result = store_for_phrase[q][0:precision]
        # Get the number of relevant documents in this query
        rel_ans = sum([1 if (doc[0] in cal_rel and cal_rel[doc[0]]) else 0 for doc in cal_result])
        precision_ph = rel_ans/(len(cal_result) or 1)
        print_data()
        print_to_disk()
