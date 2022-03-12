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

    #default...
    show = False
    if len(sys.argv) < 3:
        ngramJson = 'json/rast_ngrams_top500_no_redundant.json'
        startingNotesJson = 'json/rast_startingNotes_top500_no_redundant.json'
    else:
        ngramJson = sys.argv[1]
        startingNotesJson = sys.argv[2]

    with open(ngramJson, 'r') as f:
        ngrams = json.load(f)

    with open(startingNotesJson, 'r') as f:
        startingNotes = json.load(f)

    # use n = 9
    for n in range(7, 15):
        n = str(n)
        print(max(ngrams[n], key=ngrams[n].get))

        mostCommonFeatStr = max(ngrams[n], key=ngrams[n].get)
       
        print("most common: {}".format(mostCommonFeatStr))

        fileOffsetDict = {}
        
        for offset, filename in startingNotes[mostCommonFeatStr]:
            #print('offset {} in {}'.format(offset, filename))
            if filename not in fileOffsetDict:
                #print("inserting {}".format(filename))
                fileOffsetDict[filename] = []
            fileOffsetDict[filename].append(offset)
        

        startingPitchHistogram = {}
        for filepath in fileOffsetDict:
            featureStrOffsets = fileOffsetDict[filepath]

            #print("feature seq {} found in {} at offsets {}".format(mostCommonFeatStr, filepath, featureStrOffsets))
            
            try:
                s = M.converter.parse(filepath)
            except Exception as e:
                print("music21 couldnt parse {}".format(filepath))
          
            allNotes = s.flat.notes.stream()
           
            # what note is this
            for offset in featureStrOffsets:
                sOut = allNotes.getElementsByOffset(offset)
                # sOut is the first note of the ngram
                for element in sOut:
                    p = element.pitch
                    print('starting pitch ------> {}'.format(element.pitch))

                    if p not in startingPitchHistogram:
                        startingPitchHistogram[p] = 0
                    startingPitchHistogram[p] += 1
                    
                    noteCnt = int(n)
                    element.style.color = 'red'
                    nextNote = element
                    while noteCnt > 0:
                        nextNote = nextNote.next('Note')
                        nextNote.style.color = 'red'
                        noteCnt -= 1
                    print("next: {}".format(element.next('Note')))
            if True:
                try:
                    s.show()
                    input("press enter to continue...")
                except Exception as e:
                    print("error showing")

        for pitch in startingPitchHistogram:
            print("for n={}; feature {} starts on: pitch: {}; cnt {}".format(n, mostCommonFeatStr, pitch, startingPitchHistogram[pitch]))
