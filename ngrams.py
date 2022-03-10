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
#fileDir = xmlDir 
fileDir = noKeySigDir

fileList = [f for f in os.listdir(fileDir) if os.path.isfile(os.path.join(fileDir, f))]
print("file list: length {}".format(len(fileList)))

accidentalDict = {} 

#contains histogram of ngrams
ngramDict = {}
featureStrDict = {}

totFileCnt = len(fileList)
fileCnt = 1

# how much alter is each accidental:
# e.g. 
# tone = 200 # cents
# slashFlatAlter = -(4 * tone / 9)

#alterDict = {
#        "slash-flat": -(4*tone/9),
#

def generate_ngrams(noteSeq, ngram=1):
    temp = zip(*[noteSeq[i:] for i in range(0,ngram)])
    ans = []
    for n in temp:
        ans.append(n)
    return ans

def are_rotations(str1, str2):
    if len(str1) != len(str2):
        return 0

    s = str1 + str1

    if (s.count(str2) > 0):
        return 1
    else:
        return 0

### make alters for each accidental:
makamAccidentals = ['double-slash-flat', 'flat', 'slash-flat', 'quarter-flat', 'quarter-sharp', 'sharp', 'slash-quarter-sharp', 'slash-sharp']

tone = 200 # cents

slashFlatAlter = -(4 * tone / 9)
doubleSlashFlatAlter = -(8 * tone / 9)
flatAlter = -(5 * tone / 9)
quarterFlatAlter = -(1 * tone / 9)
sharpAlter = (4 * tone / 9)
slashSharpAlter = (5 * tone / 9)
doubleSlashSharpAlter = (8 * tone / 9)
quarterSlashSharpAlter = (1 * tone / 9)

alterDict = {
        'double-slash-flat': doubleSlashFlatAlter,
        'flat': flatAlter,
        'slash-flat': slashFlatAlter,
        'half-flat': quarterFlatAlter, 
        'quarter-flat': quarterFlatAlter,
        'sharp': sharpAlter,
        'slash-quarter-sharp': quarterSlashSharpAlter,
        'slash-sharp': slashSharpAlter,
        'half-sharp': quarterSlashSharpAlter
        }
'''
A feature string of a sequence of notes is made from the characters {R, U, W, D, B}.:
    R denotes a repeated note
    U denotes an ascending small interval 
    W denotes an ascending large interval
    D denotes a descending small interval
    B denotes a descending large interval
'''
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
#makamNames = ['huzzam']

# DERIVE From music21.note mutherfucker
#class makamNote(M.note):
#    def __init__(self):
#        self.accidental = ""
#        self.name = ""
#    
#    def __init__(self, accidental, name):
#        self.accidental = accidental
 #       self.name = name

#    def getAlter(self):
#        return 1


for makamName in makamNames:
    fileCnt = 0 
    for f in fileList:
        path = os.path.join(fileDir, f)
        print("reading file {}/{}: {}".format(fileCnt, totFileCnt, f))

        # just analyze one makam at a time
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
            print("error reading {}: {}\n--> going to raw-dog the xml".format(f, e.args))
        
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
       
            print("accidentals:::::: {}".format(accidentals))
        # list elements in score:
        #print('This score contains these {} elements'.format(len(s.elements)))
        #for element in s.elements:
        #    print('-', element)

        allNotes = s.flat.notes.stream()
        #print("element count: {}".format(len(allNotes.elements)))

        # TODO hack
        # READ THROUGH allNotes
        # READ THROUGH xmlNotes
        # if xmlNotes[idx].accidental:
        #    allNotes[idx].whateverFuckignmetadata = accidental

        #TODO:
        # modify the note.pitch.microtone to fit its accidental
        for n in allNotes: 
            if n.pitch.accidental:
                try:
                    n.pitch.microtone = alterDict[n.pitch.accidental.name]
                except Exception as e:
                    print("error adding microtone: {}".format(e.args))
                    quit()
            #TODO:
            #elif n.whateverfuckinmetadata:
            #    n.pitch.microtone = alterDict[n.pitch.accidental.name]

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
        print(accidentalDict)

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
    onlyMostCommon = True
    doNormalize = False
    doCombineRotations = False 
     
    #TODO sum all values -> normalize

    mostCommonCnt = 20
    for ngLen in featureStrDict:
        entryCount = 0
        reversedAndSorted = reversed(sorted(featureStrDict[ngLen].items(), key = lambda item: item[1])) 
        for key, value in reversedAndSorted:
            
            if doCombineRotations:
                for key2, value2 in reversedAndSorted:
                    if are_rotations(key, key2):
                        value += value2
                        #remove key2 from reversedAndSorted
                        del reversedAndSorted[key2]
                        print("rotation!: {} -- {}: {}+{}={}".format(key, key2, value-value2, value2, value))

            entryCount += 1
            # to only keep entries above this count:
            if onlyMostCommon:
                if entryCount > mostCommonCnt:
                    break
            if ngLen not in sortedFeatureHistogram:
                sortedFeatureHistogram[ngLen] = {}
            sortedFeatureHistogram[ngLen][key] = value
            #print("-- {}: {}".format(key, value))
    
    versionStr = ''
    if onlyMostCommon:
        versionStr += '_above{}'.format(mostCommonCnt)
    if doCombineRotations:
        versionStr += '_no_redundant'

    jsonFile = "{}_ngrams{}.json".format(makamName, versionStr)
    jsonPath = os.path.join(jsonDir, jsonFile) 
    with open(jsonPath, "w") as outfile:
        json.dump(sortedFeatureHistogram, outfile, indent=4)


