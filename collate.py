import collections
from itertools import permutations
from bitarray import bitarray

class Node(object):
    def __init__(self, norm):
        self.tokendata = {} #  members are witness:offset pairs; not present for start and end tokens
        self.norm = norm
    def __repr__(self):
        return self.norm
    def __lt__(self, other): # make it sortable by norm value
        return self.norm < other.norm
    def add_location(self, siglum, offset):
        self.tokendata[siglum] = offset

# Output: shortest common supersequence of witnesses, which is the same as the topological order,
#   and which can be used, with the witnesses, to construct the variant graph
# Assumption: Align deepest matches first

# TODO: Single-token witnesses are not processed because they have no bigrams; this is an error
# TODO: Should we place non-repeated tokens first?
# TODO: At the moment we look only at skip-bigrams. Other lengths?

# Sample data
witnessData = {'wit1': ['a', 'b', 'c', 'd', 'e'], 'wit2': ['a', 'e', 'c', 'd'], 'wit3': ['a', 'd', 'b']}

witOrders = list(permutations(['wit1', 'wit2', 'wit3']))
for witOrder in witOrders:

    ###
    # Construct common sequence table (csTable) of all witnesses as dict
    ###
    # key is skip-bigram
    # value is list of (siglum, pos1, pos2) tuple, with positions of skipgram characters
    csTable = collections.defaultdict(list)
    for key in witOrder:
        value = witnessData[key]
        for first in range(len(value)):
            for second in range(first + 1, len(value)):
                csTable[(value[first], value[second])].append((key, first, second))
    ###
    # Sort table into common sequence list (csList)
    ###
    #   order by 1) number of witnesses (numerical high to low) and 2) sequence (alphabetic low to high)
    csList = [k for k in sorted(csTable, key=lambda k: (-len(csTable[k]), k))]
    bitArrays = {k: bitarray(len(witnessData[k])) for k in witnessData}  # create a bitarray the length of each witness
    for ba in bitArrays.values():  # initialize bitarrays to all 0 values
        ba.setall(0)

    ###
    # Build topologically ordered list (toList)
    ###
    toList = []
    toList.extend([Node('#start'), Node('#end')])
    for skipgram in csList:
        locations = csTable[skipgram]  # list of tuples of (siglum, location1, location2) for skipgram
        norms = list(skipgram)  # two tokens
        for skipgramPos in range(len(norms)):  # loop over head and tail by position ([1, 2])
            norm = norms[skipgramPos]  # normalized value of token
            for location in locations:  # for each token, get witness and offset within witness
                siglum = location[0]  # witness identifier
                offset = location[skipgramPos + 1]  # offset of token within witness
                if bitArrays[siglum][offset] == 1:
                    # print('skipping: ', norm, ' from ', skipgram, ' at ', location)
                    break
                floor = 0
                ceiling = len(toList) - 1
                modifyMe = None # existing toList entry to be modified; if None, create a new one
                for dictPos in range(len(toList)):
                    currentDict = toList[dictPos].tokendata
                    if siglum not in currentDict.keys():  # dictionary isn't relevant; check the next item in toList
                        pass
                    else:  # it can't be equal, since we used the bitarray to filter those out
                        if currentDict[siglum] < offset:
                            floor = dictPos
                        else:
                            ceiling = dictPos
                            break
                # scan from floor to ceiling, looking for matching 'norm' value
                # if there is a dictionary to modify, save it as modifyMe (don't modify it yet)
                # TODO: this gets the leftmost if there is more than one, which is not necessarily optimal
                for pos in range(floor, ceiling):
                    if toList[pos].norm == norm:
                        modifyMe = toList[pos]
                        break
                # if there is a dictionary to modify, do it; otherwise insert a new dictionary
                if modifyMe is None:
                    new_token = Node(norm)
                    new_token.add_location(siglum, offset)
                    toList.insert(ceiling, new_token)
                else:
                    # print('adding', siglum,':',offset,'to',modifyMe,modifyMe.tokendata)
                    modifyMe.tokendata[siglum] = offset
                bitArrays[siglum][offset] = 1  # record that we've processed this token
                # print('added: ', norm, ' from ', skipgram, ' at ', location,
                #       ' with floor=', floor, ' and ceiling=', ceiling, sep='')

    ###
    # build list of edges for each witness
    ###
    edgeSets = collections.defaultdict(list) #  key = siglum, value = list of (source, target) tuples
    for token in toList:  # token.norm is str; token.tokendata is dict with siglum:offset items
        if token.norm == '#start':  # not an edge target, so don’t add an edge
            pass
        # elif node['norm'] == '#end':  # create edges for all witnesses; source is target of last edge, target is end
        #     for key in witnessData:  # key is siglum
        #         edgeSets[key].append((edgeSets[key][-1][1], toList[-1]))
        else:
            for key, value in token.tokendata.items():
                try:  # target of last edge is source of new one, but only if the list isn't empty
                    source = edgeSets[key][-1][1]
                except IndexError:  # if edgeSets[key] is empty, use the #start node as the source
                    source = toList[0]
                edgeSets[key].append((source, token))

    ###
    # Diagnostic output
    ###
    print('---\n## witOrder =', witOrder)
    print('## Input')
    for item in witnessData.items():
        print(item)
    print('## Nodes in topological order: ')
    for item in toList:
        print(item, item.tokendata)
    print('## Edges')
    # merge witness-specific edge lists into single list
    edges = set(inner for outer in edgeSets.values() for inner in outer)  # tuples of Tokens
    for edge in sorted(edges):
        print(edge[0].norm, edge[0].tokendata, '→', edge[1].norm, edge[1].tokendata)
