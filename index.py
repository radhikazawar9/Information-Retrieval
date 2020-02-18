"""
Assignment 2 Group 12

Radhika Zawar s3734939
Parvi Verma s3744398
"""

import os
import re
import pandas as pd
import string
import paramiko
import argparse
from pathlib import Path
import struct
import math

"""
Variable definitions
Assingment 1 implementation
"""
host = "titan.csit.rmit.edu.au"             # server id where file is located
port = 22                                   # using port 22
username = "s3734939"                       # my student id to access data
keyfile_path = None                         # not needed
password = "R@dz0411484188"                 # password to access file from server

INT_SIZE = 32                               # -bits in an integer when saving the inverted lists

# Tag
_doc       = 'doc'                         # simple naming for doc tag
_doc_num   = r'docno>\s*(.*?)\s*<\/docno'  # regex for fetching docno
_head      = 'headline'                    # simple naming for headline tag
_text      = 'text'                        # simple naming for text tag

no_doc, parse, head, text = 1,2,3,4        # assigning integer id

document_map     = []       # to store found words in each doc
lexicon     = {}            # list to store word for dumping into file
match_previous  = None      # global - gets bounced between indexifier() and regex check funcs

"""
To fetch the data from server [ref : https://www.ivankrizsan.se/2016/04/28/implementing-a-sftp-client-using-python-and-paramiko/]
Assingment 1 implementation
"""
def create_sftp_client(host, port, username, password, keyfilepath, keyfiletype):

    sftp = None
    key = None
    transport = None
    try:
        if keyfilepath is not None:
            # Get private key used to authenticate user.
            if keyfiletype == 'DSA':
                # The private key is a DSA type key.
                key = paramiko.DSSKey.from_private_key_file(keyfilepath)
            else:
                # The private key is a RSA type key.
                key = paramiko.RSAKey.from_private_key(keyfilepath)

        # Create Transport object using supplied method of authentication.
        transport = paramiko.Transport((host, port))
        transport.connect(None, username, password, key)

        sftp = paramiko.SFTPClient.from_transport(transport)
        return sftp

    except Exception as e:
        print('An error occurred creating SFTP client: %s: %s' % (e.__class__, e))
        if sftp is not None:
            sftp.close()
        if transport is not None:
            transport.close()
        pass

"""
To download file from certain path
Assingment 1 implementation
"""
def get_file(path, filename):

    sftpclient = create_sftp_client(host, port, username, password, keyfile_path, 'DSA')
    sftpclient.chdir(path)
    # List files in the default directory on the remote computer.
    dirlist = sftpclient.listdir('.')
    #using file name to access the asked file
    latimes = sftpclient.file(filename, mode='r', bufsize=-1)
    # returning file
    return latimes

"""
indexing task 1
Assingment 1 implementation and some added implementation of advance retrival
"""

def indexifier(file_la, stoplist, print_findings, punctuations):
    global match_previous   #global veriable to pick the last matched value

    current_id  = -1        # incrementing with each new found doc. Starting at 0
    document_dict = {}      # dictinary to save entries of each new found document
    status = no_doc         # default status and also to notify closing tags
    leng = term_num = 0     # to store calculated length and term_num
    id = ""                 # to store current document id

    for line in file_la:

        line = line.strip().lower()     #case folding and whitespace removing

        # Check 1 closing tags of text and headline
        if any ([status == text and check_close(_text, line), status == head and check_close(_head, line)]):
            status = parse

        # check 2 checking end of the document
        # implementation to store term location
        elif status == parse and check_close(_doc, line):
            # storing doc id and term frequecy and tuple of frequecy
                for word, freq in document_dict.items():       # reading all the
                    lexicon[word].append( (current_id, len(freq)) + tuple(freq) )   # appending tuple of docId and frequency
                # Reseting for next doc
                document_dict = None
                status = no_doc

                #storing document id and document weight
                document_map.append((id, leng))          # Add entry to the map (the key is the item's index)



        # check 3 check for beginning of text or head
        elif ((status == text) or (status == head)):

            if line.startswith("<") and line.endswith(">"): # checking if it markup tags ie <p>
                continue                                    # ignoring <?> tags lines

            #calling normalise function refer line 184
            normalised = normalise(line, punctuation=punctuations, case=False, stops=stoplist)

            # implementation to store term location
            for word in normalised:             # Adding document frequency for words
                leng += len(word)               # Calculating document length for each document
                if word not in document_dict:
                    document_dict[word] = []    # increasing frequency
                document_dict[word].append(term_num)
                term_num += 1

                if word not in lexicon:         # if word isn't in lexicon that is a new word found
                    lexicon[word] = []          # empty at the moment. we add value once the document is scanned entirely

                    if print_findings:          # Print it if asked
                        print(word)


        # check 4 opening tags doc_id
        elif status == no_doc and check_tag(_doc, line):   #start of new document
            document_dict = {}                  # reseting dictionary
            current_id += 1                     # increamenting doc id
            status = parse                      # changing status to parse
            leng = term_num = 0       # to store calculated length and term_num
            id = ""                 # to store current document id


        # check 5 if parsing update the document_map
        elif status == parse and check_tag(_doc_num, line, is_regex=True):
            # Temporarily storing document number for each document
            id = match_previous.group(1)

        # check 6 opening tags headline
        elif status == parse and check_tag(_head, line):
                status = head                   # changing status to head

        # check 7 opening tags text
        elif status == parse and check_tag(_text, line):
                status = text                   # changing status to text

"""
Check tag for recording
Assingment 1 implementation
"""
def check_tag(tag, line, is_regex=False):
    global match_previous

    tag = '<' + tag + '>'                       # tag brackets
    if is_regex:                                # regex will do automatic matching
        match_previous = re.match(tag, line)    # check match
    else:
        match_previous = (tag == line)          # manual string matching
    return match_previous                       # returning true if matches

"""
check closed tag for regx
Assingment 1 implementation
"""
def check_close(reg, line, is_regex=False):         # checking for closed tags
    return check_tag(r'/' + reg, line, is_regex)    # using '/' symbol to identify end


"""
reading stoplist and storing as string
Assingment 1 implementation
"""
def open_stoplist(path,stoplst):
    if stoplst is None:             # if stoplist name is not provided
        return set()                # return blank if no stoplist

    sl = get_file(path,stoplst)     # if stoplist name is given then access the file from remote server

    stl = {w.strip() for w in sl}   # String words for whitespace
    return stl                      # return the set


"""
Normalizing string
hypen is true for seperating words with spaces
case true to fold to lower case
stop to ignore the word

Assingment 1 implementation
"""
def normalise(intake, hyphens=True, punctuation=r'[^\w\ ]+', case=True, stops=None):
    if case:                        # if capital
        intake = intake.lower()     # case folding to lower

    if hyphens:                     # Replacing hyphens
        intake = re.sub(r'(?<=[a-zA-Z])-(?=\w)', ' ', intake)   # matching hypenated words
        intake = re.sub(r'(?<=\w)-(?=[a-zA-Z])', ' ', intake)   # considering one side could have numbers
        intake = intake.replace('-', '')                        # removing -
    if punctuation:
        intake = re.sub(punctuation, ' ', intake)               # remove punctuation
    if stops:
        terms = [t for t in intake.split() if t not in stops]   # omitting stop words
    else:
        terms = intake.split()                                  # split terms if no anamaly
    return terms                                                # return normalised term

"""
writing file to disc
map: doc_id, DOCNO from tag

Added implementation
"""
def write_map(map, mapfile):                        # writing into mapfile
    k1 = 1.2
    b = 0.75
    AL = sum (s[1] for s in map) / len(map)
    # implementation for ranked retrieval feature
    with open(mapfile, 'w') as mf:                  # open in w mode
        for (d_id, data) in enumerate(map):         # iterate
            K = calculateKValue(k1, b, data[1], AL)
            mf.write('{} {}\n'.format(d_id, '{} {}'.format(data[0], K)))  # write in this foramat in the text file

""""###
Writes the 'lexicon' and 'invlists' files to disk
lexicon: word , pointer from ivlist (file.seek() func for navigation)
invlists (binary file) : document freq, id, in_doc freq, repeat for doc freq

Added implementation
"""
def write_lexicon_invs(lex, lxfile, ifn):
    with open(lxfile, 'w') as lf, open(ifn, 'wb') as lx:    # open lexicon in write mode
        for term, item in lex.items():                     # dict of list of tuples
            # populating lexicon
            lf.write('{} {}\n'.format(term, lx.tell() ))    # function tell() tells the location to seek() function

            # add to the List: the document-frequency, document ids, in-doc freqs and positions of the term
            lx.write(struct.pack('>i',len(item)))
            #to_save = [len(items)] + [a[i] for a in items for i in (0, 1)]

            for r in item:
                for n in r:
                    b = struct.pack('>i',int(n)) # Convert to a bytes array (4 large for 32 bit integers)
                    lx.write(b)             # And output to the file

"""
Calculates K for BM 25
k1, b - abritrary constants
Ld - document length
AL - average length

"""
def calculateKValue(k, b, data, AL):
    return k*((1-b)+((b*data)/AL))


""""
Reading command line Argument
Expected query is python index.py <path of file> -p -s <path of stopword file>
"""
if __name__ == '__main__':
    # Handle arg vars
    parser = argparse.ArgumentParser()
    parser.add_argument('sourcefile', help='The source document file')  # compulsary argument to know the file path
    parser.add_argument('-p', action='store_true',
                        help='Print each new term as it\'s found')      # optional to print what is found
    parser.add_argument('-s', '--stoplist', type=str,
                        help='A path to a file containing a list of stopwords') # optional to get path of stopword file
    args = parser.parse_args()                                          # argument parser

    # try catch for file error
    try:
        stoplist_file = ""              # initialing to avoid error as stoplist fiel is optional
        """Reading compulsary source file
        """
        p = Path(args.sourcefile)       # reading source path of compulsary sourcefile
        filepath = p.parent.as_posix()  # converting source path to str
        part = p.parts                  # access parts of source path

        # convert window path to unicode
        unicode_filepath = unicode(filepath, "utf-8", errors="ignore")

        #use unicode for window path and forth parameter of string list which is filename
        latime = get_file(unicode_filepath,part[4] )
        latime = latime

        """Reading optional source file
        """
        if args.stoplist:
            p_stls = Path(args.stoplist)
            filepath_stls = p_stls.parent.as_posix()    # covert source to string
            part_stls = p_stls.parts                    # tokenisisg path to access file name
            unicode_filepath_stls = unicode(filepath_stls, "utf-8", errors="ignore")#coverting window path to unicode

            #use window path and file name to envoke stoplist function
            stoplist_file = open_stoplist(unicode_filepath_stls, part_stls[4])

        """important steps
        """
        #indexing the file to retrieve requered data to feed into map, lexicon and invlist file
        indexifier(latime, stoplist_file, args.p, r'[^a-z0-9\ ]+')

        write_map(document_map, 'map')                      # save data to local memory map file
        write_lexicon_invs(lexicon, 'lexicon', 'invlists')  # save data to local memory binary inverted list file

    except OSError as e:                                    # to catch oserror if occurs
        print('{}\nProgram Exiting'.format(e))
