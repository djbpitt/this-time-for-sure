import collections

# Output: shortest common supersequence of witnesses, which is the same as the topological order,
#   and which can be used, with the witnesses, to construct the variant graph
# Assumption: Align deepest matches first

# TODO: Single-token witnesses are not processed because they have no bigrams; this is an error
# TODO: Should we place non-repeated tokens first?
# TODO: At the moment we look only at skip-bigrams. Other lengths?

# Sample data
witnessData = {'wit1': ['a', 'b', 'c', 'd', 'e'], 'wit2': ['a', 'e', 'c', 'd'], 'wit3': ['a', 'd', 'b']}

# Construct common sequence table (csTable) of all witnesses as dict
# key is skip-bigram
# value is list of (siglum, pos1, pos2) tuple, with positions of skipgram characters

csTable = collections.defaultdict(list)
for key, value in witnessData.items():
    for first in range(len(value)):
        for second in range(first + 1, len(value)):
            csTable[value[first] + value[second]].append((key, first, second))

# Sort table into common sequence list (csList)
#   order by 1) number of witnesses (numerical high to low) and 2) sequence (alphabetic low to high)
csList = [k for k in sorted(csTable, key=lambda k: (-len(csTable[k]), k))]

# Build topologically ordered list (toList)
toList = []
toList.extend([{'norm': '#start'}, {'norm': '#end'}])
for skipgram in csList:
    locations = csTable[skipgram]  # list of tuples of (siglum, location1, location2) for skipgram
    norms = list(skipgram)  # two characters; TODO: will need to be changed when tokens are not single characters
    for skipgramPos in range(len(norms)):  # loop over head and tail by position ([1, 2])
        norm = skipgram[skipgramPos]  # normalized value of token
        for location in locations:  # for each token, get witness and offset within witness
            siglum = location[0]  # witness identifier
            offset = location[skipgramPos + 1]  # offset of token within witness
            # print('witness = ', siglum, '; offset = ', offset, '; norm = ', norm) # diagnostic
            # get lower and upper bounds for witness and offset within witness
            floor = 0
            ceiling = len(toList) - 1
            modifyMe = None
            # print('siglum = ', siglum, '; offset = ', offset) # diagnostic
            for dictPos in range(len(toList)):
                currentDict = toList[dictPos]
                # print('currentDict = ', currentDict) # diagnostic
                if siglum not in currentDict.keys():  # this dictionary isn't relevant; check the next item in toList
                    pass
                else:
                    if currentDict[siglum] == offset:  # the token is already in the list
                        pass
                    elif currentDict[siglum] < offset:
                        floor = dictPos
                    else:
                        ceiling = dictPos
            # scan from floor to ceiling, looking for matching 'norm' value
            for pos in range(floor, ceiling):
                if toList[pos]['norm'] == norm:
                    modifyMe = toList[pos]
                    break
            if modifyMe is None:
                toList.insert(ceiling, {'norm': norm, siglum: offset})
            else:
                modifyMe[siglum] = offset
# Diagnostic output
for dict in toList:
    print(dict)
