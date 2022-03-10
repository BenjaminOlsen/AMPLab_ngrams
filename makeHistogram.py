#!/usr/local/bin/python3

import json
import sys
import matplotlib.pyplot as plt

def ascii_histogram(d) -> None:
    """A horizontal frequency-table/histogram plot."""
    for key, value in d:
        print('{0} {1}'.format(k, '+' * value))

if __name__ == "__main__":
    print(f"Arguments count: {len(sys.argv)}")
    for i, arg in enumerate(sys.argv):
        print(f"Argument {i:>6}: {arg}")

    if len(sys.argv) < 2:
        print("give path to json file")
        exit()
    elif len(sys.argv) > 2:
        print("too many arguments")
        exit()
    
    path = sys.argv[1]
    makamName = path.split("_")[0][5:]
    
    with open(path, 'r') as f:
        data = json.load(f)
    

    #for e in data:
    #    print(e)
    #    #print(data[e])
    #    for k in data[e]:
    #        print('{}: {}'.format(k, '+' * data[e][k]))
    #    print("~~~~~")



    for seqLen in range(3,15):
        seqLenStr = str(seqLen)
        names = list(data[seqLenStr].keys())
        values = list(data[seqLenStr].values())
        
        plt.bar(range(len(names)), values, tick_label=names)
        plt.title("makam {}\n frequency of sequences of length {}". format(makamName, seqLenStr))
        plt.xticks(rotation = 90)
        plt.tight_layout()

        
        fileStr= '{}_seq_{}.png'.format(makamName, seqLenStr)
        plt.savefig(fileStr)
        plt.clf()
        print('saved {}'.format(fileStr))

