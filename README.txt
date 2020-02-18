Assignment 2 Group 12

Radhika Zawar s3734939
Parvi Verma s3744398

### python version 2.7

## file index.py
> requirements
install library paramiko, argparse, path from pathlib, struct, re, pandas as pd, string, math and os

>input @command line
python index.py /home/inforet/a1/latimes -p -s /home/inforet/a1/stoplist

## file search.py
> requirements
install library sys, struct, from index import normalise as norm, from index import open_stoplist, argparse, math, time, heapq, from pathlib import Path, from math import log, from heap import Heap,traceback

>input @command line
python search.py -BM25 -q 100 -n 10 -l lexicon -i invlists -m map stanford university
or
python search.py --phrase-search -q 100 -l lexicon -i invlists -m map stanford university

## file effectiveness_evaluation.py
> requirements
install library paramiko, from index import get_file, subprocess, sys, os

>input @command line
python effectiveness_evaluation.py
