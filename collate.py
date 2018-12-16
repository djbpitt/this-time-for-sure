import collections

# Note
# Single-token witnesses are not processed because they have no bigrams; this is an error

# Sample data
witnessData = {'wit1': ['a', 'b', 'c', 'd', 'e'], 'wit2': ['a', 'e', 'c', 'd'], 'wit3':['a', 'd', 'b']}

# Construct common sequence table (csTable) of all witnesses as dict
# key is skipbigram
# value is list of (siglum, pos1, pos2) tuple, with positions of skipgram characters

csTable = collections.defaultdict(list)
for key, value in witnessData.items():
    for first in range(len(value)):
        for second in range(first + 1, len(value)):
            csTable[value[first] + value[second]].append((key, first, second))

# Sort table into common sequence list (csList)
#   order by 1) number of witnesses (numerica high to low) and 2) sequence (alphabetic low to high)
csList = [k for k in sorted(csTable, key=lambda k: (-len(csTable[k]), k))]

# Build topologically ordered list (toList)
toList = []
for skipgram in csList:
    locations = csTable[skipgram] # list of tuples of (siglum, location1, location2) for skipgram
    norms = list(skipgram) # two characters
    for skipgramPos in range(len(norms)): # loop over characters
        norm = skipgram[skipgramPos] # normalized value of toke
        for location in locations: # for each character, get witness and offset within witness
            siglum = location[0] # witness identifier
            offset = location[skipgramPos + 1] # offset of norm within witness
            # print(siglum, offset, norm) # diagnostic
            # get lower and upper bounds for witness and offset within witness
            for dictPos in range(len(toList)):
                currentDict = toList[dictPos]


# Diagnostic output
print(toList)

