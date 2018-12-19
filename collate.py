import collections
from itertools import permutations
from bitarray import bitarray

# Output: shortest common supersequence of witnesses, which is the same as the topological order,
#   and which can be used, with the witnesses, to construct the variant graph
# Assumption: Align deepest matches first

# TODO: Single-token witnesses are not processed because they have no bigrams; this is an error
# TODO: Should we place non-repeated tokens first?
# TODO: At the moment we look only at skip-bigrams. Other lengths?

# Sample data
witnessData = {'wit1': ['a', 'b', 'c', 'd', 'e'], 'wit2': ['a', 'e', 'c', 'd'], 'wit3': ['a', 'd', 'b']}
bitArrays = {k:bitarray(len(witnessData[k])) for k in witnessData} # create a bitarray the length of each witness
for item in bitArrays: # initialize bitarrays to all 0 values
    bitArrays[item].setall(0)

# Construct common sequence table (csTable) of all witnesses as dict
# key is skip-bigram
# value is list of (siglum, pos1, pos2) tuple, with positions of skipgram characters

witOrders = list(permutations(['wit1', 'wit2', 'wit3']))
for witOrder in witOrders:
    csTable = collections.defaultdict(list)
    for key in witOrder:
        value = witnessData[key]
        for first in range(len(value)):
            for second in range(first + 1, len(value)):
                csTable[(value[first], value[second])].append((key, first, second))

    # for key, value in witnessData.items():
    #     for first in range(len(value)):
    #         for second in range(first + 1, len(value)):
    #             csTable[value[first] + value[second]].append((key, first, second))

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
            norm = norms[skipgramPos]  # normalized value of token
            for location in locations:  # for each token, get witness and offset within witness
                siglum = location[0]  # witness identifier
                offset = location[skipgramPos + 1]  # offset of token within witness
                floor = 0
                ceiling = len(toList) - 1
                modifyMe = None
                bitArrays[siglum][offset] = 1 # record that we've processed this token
                for dictPos in range(len(toList)):
                    currentDict = toList[dictPos]
                    if siglum not in currentDict.keys():  # this dictionary isn't relevant; check the next item in toList
                        pass
                    else:
                        if currentDict[siglum] == offset:  # the token is already in the list
                            pass
                        elif currentDict[siglum] < offset:
                            floor = dictPos
                        else:
                            ceiling = dictPos
                            break
                # scan from floor to ceiling, looking for matching 'norm' value
                # if there is a dictionary to modify, save it as modifyMe (don't modify it yet)
                # TODO: this gets the leftmost if there is more than one, which is not necessarily optimal
                for pos in range(floor, ceiling):
                    if toList[pos]['norm'] == norm:
                        modifyMe = toList[pos]
                        break
                # if there is a dictionary to modify, do it; otherwise insert a new dictionary
                if modifyMe is None:
                    toList.insert(ceiling, {'norm': norm, siglum: offset})
                else:
                    modifyMe[siglum] = offset
    # Diagnostic output
    print('added: ', norm, ' from ', skipgram, ' at ', location, ' with floor=', floor, ' and ceiling=', ceiling, sep='')
    for item in toList:
        print(item)
    print(witOrder, [item['norm'] for item in toList])
    print(bitArrays)