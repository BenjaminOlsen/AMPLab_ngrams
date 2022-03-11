#!/usr/local/bin/python3

import os
import sys
import json
import music21 as M



if __name__ == "__main__":
    # TODO
    # arguments: --ng <ngramJson> --sn <startingNotes> 
    # arhument is path to NGRAM JSON
    #parser = argparse.ArgumentParser()
    #parser.add_argument(
    ngramJson = sys.argv[1]
    startingNotesJson = sys.argv[2]

    with open(ngramJson, 'r') as f:
        ngrams = json.load(f)

    with open(startingNotesJson, 'r') as f:
        startingNotes = json.load(f)

    # use n = 9
    n = str(9)
    print(max(ngrams[n], key=ngrams[n].get))

    mostCommonFeatStr = max(ngrams[n], key=ngrams[n].get)
    
    fileOffsetDict = {}
    
    for offset, filename in startingNotes[mostCommonFeatStr]:
        print('offset {} in {}'.format(offset, filename))
        if filename not in fileOffsetDict:
            fileOffsetDict[filename] = []
        fileOffsetDict[filename].append(offset)


    for filename in fileOffsetDict:
        print("feature seq {} found in {} at offsets {}".format(mostCommonFeatStr, filename, fileOffsetDict[filename]))


