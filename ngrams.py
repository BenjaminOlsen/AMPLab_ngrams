#!/usr/local/bin/python3

import os
import json
import music21 as M
import numpy as np
import xml.etree.ElementTree as ET

# turkish makam scores:
xmlDir = 'SymbTr/MusicXML'
noKeySigDir = os.path.join(xmlDir, 'noKeySig')
jsonDir = 'json'

if not os.path.exists(noKeySigDir):
    os.makedirs(noKeySigDir)

#change to noKeySigDir if you already made the no key sig xmls
fileDir = xmlDir 

fileList = [f for f in os.listdir(fileDir) if os.path.isfile(os.path.join(fileDir, f))]
print("file list: length {}".format(len(fileList)))

accidentalDict = {} 

#contains histogram of ngrams
ngramDict = {}
featureStrDict = {}

totFileCnt = len(fileList)
fileCnt = 1

def generate_ngrams(noteSeq, ngram=1):
    temp = zip(*[noteSeq[i:] for i in range(0,ngram)])
    ans = []
    for n in temp:
        ans.append(n)
    return ans

def generate_feature_string(intervalSeq):
    s = '' #empty string
    for interval in intervalSeq:
        if interval <= 1 and interval >= -1:
            s += 'R'
        elif interval <= 300 and interval >= 10:
            s += 'U'
        elif interval > 300:
            s += 'W'
        elif interval >= -300 and interval < -1:
            s += 'D'
        elif interval < -300:
            s += 'B'
        else:
            print("shouldnt get here")
    
    return s

# analyze only these makam names:
makamNames = ['rast', 'acemasiran', 'acemkurdi', 'beyati', 'buselik', 'hicaz', 'huseyni', 'huzzam', 'kurdilihicazkar', 'nihavent']

for makamName in makamNames:
    fileCnt = 0 
    for f in fileList:
        path = os.path.join(fileDir, f)
        print("reading file {}/{}: {}".format(fileCnt, totFileCnt, f))

        if f.split('--')[0] != makamName: 
            fileCnt += 1
            print("skipping {}".format(f))
            continue

        print("analyzing {}".format(f))

        try:
            s = M.converter.parse(path)

            #print('This score {} contains these {} elements'.format(f, len(s.elements)))
            #for element in s.elements:
            #    print('-', element)
        
        except Exception as e:
            print("error reading {}: {}".format(f, e.args))
        
            tree = ET.parse(path)
            root = tree.getroot()        

            notes = []
            accidentals = []

            for k in root.iter('key'):
                for ks in k.findall('key-step'):
                    notes.append(ks.text)
                for ka in k.findall('key-accidental'):
                    accidentals.append(ka.text)

            print('The key signature of this score has:')
            for i in range(len(notes)):
                print('-', notes[i], accidentals[i])

            # remove the problematic key signature:
            for att in root.iter('attributes'):
                if att.find('key'):
                    att.remove(att.find('key'))

            newMakamScore = f[:-4] + '--noKeySignature.xml'
            newPath = os.path.join(noKeySigDir, newMakamScore)

            tree.write(newPath)
            try:
                s = M.converter.parse(newPath)
            except Exception as e:
                print("error parsing {}: {}".format(newPath, e.args))
        
        # list elements in score:
        #print('This score contains these {} elements'.format(len(s.elements)))
        #for element in s.elements:
        #    print('-', element)

        allNotes = s.flat.notes.stream()
        #print("element count: {}".format(len(allNotes.elements)))

        #TODO:
        # modify the note.pitch.microtone to fit its accidental

        intervalList = []
        for note in allNotes:
            if note.pitch.accidental:
                accName = note.pitch.accidental
                if accName not in accidentalDict:
                    accidentalDict[accName] = 1
                else: 
                    accidentalDict[accName] += 1

            ### test
            nextNote = note.next()
            #print("note: {}, next: {}, interval: {}".format(note, nextNote, M.interval.Interval(note, nextNote).cents) )
            intervalList.append(M.interval.Interval(note, nextNote).cents)

        # create ngrams and feature string histogram
        for ngramLength in range(3,15):
            #print("finding ngrams of length {}".format(ngramLength))
            ngs = generate_ngrams(intervalList, ngramLength)
            for ng in ngs:
                featureStr = generate_feature_string(ng)
                #print(featureStr)
                if ngramLength not in featureStrDict:
                    featureStrDict[ngramLength] = {}
                if featureStr not in featureStrDict[ngramLength]:
                    featureStrDict[ngramLength][featureStr] = 1
                else:
                    featureStrDict[ngramLength][featureStr] += 1

        fileCnt += 1

        #print(featureStrDict) 
        #if (fileCnt > 10):
        #     break

    #fixme:
    sortedFeatureHistogram = {}
    for ngLen in featureStrDict:
        entryCount = 0
        for key, value in reversed(sorted(featureStrDict[ngLen].items(), key = lambda item: item[1])):
            entryCount += 1
            if entryCount > 15:
                break
            if ngLen not in sortedFeatureHistogram:
                sortedFeatureHistogram[ngLen] = {}
            sortedFeatureHistogram[ngLen][key] = value
            #print("-- {}: {}".format(key, value))
    
    jsonFile = "{}_ngrams.json".format(makamName)
    jsonPath = os.path.join(jsonDir, jsonFile) 
    with open(jsonPath, "w") as outfile:
        json.dump(sortedFeatureHistogram, outfile, indent=4)


