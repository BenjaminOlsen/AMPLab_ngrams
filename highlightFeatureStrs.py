#!/usr/local/bin/python3

import os
import sys
import json
import music21 as M
import os.path


if __name__ == "__main__":
    # TODO
    # arguments: --ng <ngramJson> --sn <startingNotes> 
    # arhument is path to NGRAM JSON
    #parser = argparse.ArgumentParser()
    #parser.add_argument(

    #default...
    showScore = True 
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
    for n in range(10, 11):
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
        

        # now go through the files mentioned in fileOffsetDict,
        # and highlight the spots where the mostCommonFeatStr occurs
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
            featStrCnt = len(featureStrOffsets)
            
            print("found {} occurances of {} in {}".format(featStrCnt, mostCommonFeatStr, filepath))
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
                        try:
                            nextNote = nextNote.next('Note')
                            nextNote.style.color = 'red'
                        except Exception as e:
                            print("problem getting next note: {}".format(e.args))
                        noteCnt -= 1
            
            if showScore and featStrCnt > 6:
                try:

                    ###########
                    #FIXME:
                    ##pdfDir = 'pdf'
                    #basename = os.path.basename(filepath)
                    #pdfFileName = os.path.splitext(basename)[0] + '.pdf'
                    #print("writing {}".format(os.path.join(pdfDir, pdfFileName)))
                    #s.write(pdfFileName, pdfDir)
                    ################
                    s.show()
                    input("press enter to continue...")
                except Exception as e:
                    print("error showing: {}".format(e.args))

        for pitch in startingPitchHistogram:
            print("for n={}; feature {} starts on: pitch: {}; cnt {}".format(n, mostCommonFeatStr, pitch, startingPitchHistogram[pitch]))
