import collections
from bitarray import bitarray
import pprint
pp = pprint.PrettyPrinter(indent=2)
from prettytable import PrettyTable # not in anaconda

import operator
import itertools
import glob
import os
import re
from tqdm import tqdm

class Node(object):
    def __init__(self, norm):
        self.tokendata = {}  # members are witness:offset pairs; not present for start and end tokens
        self.norm = norm
        self.rank = None

    def __repr__(self):
        return self.norm

    def __lt__(self, other):  # make it sortable by norm value
        return self.norm < other.norm

    def add_location(self, siglum, offset):
        self.tokendata[siglum] = offset


def generate_skipgrams(data: dict, skip: int = 5, length: int = 2) -> dict:
    """Return common sequence table for skip-ngrams.

    Keyword arguments:
        data -- dictionary with siglum as key and list of tokens as values
        skip -- maximum skip size (default to 5; other legal values are non-negative integers)
        length -- size of ngram (default to 2 for bigram); currently ignored—always creates bigrams

    Return:
        csTable -- dictionary:
            key is tuple of skipgram tokens
            value is list of tuples of (siglum, offset of first token, offset of ...)
    """
    csTable = collections.defaultdict(list)
    for key, value in data.items():
        for first in range(len(value) - skip):
            for second in range(first + 1, first + skip + 1):
                csTable[(value[first], value[second])].append((key, first, second))
    return csTable


# Output: shortest common supersequence of witnesses, which is the same as the topological order,
#   and which can be used, with the witnesses, to construct the variant graph
# Assumption: Align deepest matches first

# TODO: Single-token witnesses are not processed because they have no bigrams; this is an error
# TODO: At the moment we look only at skip-bigrams. Other lengths?

# Sample data 1: Darwin (repetition, no transposition)
yearRegex = re.compile(r'(\d{4})')
witnessData = {}
for filename in glob.glob(os.path.join('darwin/chapter_1', '*.txt')):
    siglum = yearRegex.search(filename).group(1)
    with open(filename, 'r') as f:
        # witnessData[siglum] = f.read().split()[:150]  # slice to limit word count
        witnessData[siglum] = f.read().split()  # all words

# Stopwords (based on NLTK English list)
with open('stopwords.txt') as f:
    stopwords = set(f.read().splitlines())
# Sample data 2: transposition, no repetition
# witnessData = {'wit1': ['a', 'b', 'c', 'd', 'e'],
#                'wit2': ['a', 'e', 'c', 'd'],
#                'wit3': ['a', 'd', 'b']}

###
# Construct common sequence table (csTable) of all witnesses as dict
###
# key is skip-bigram
# value is list of (siglum, pos0, pos1) tuple, with positions of skipgram characters

csTable = generate_skipgrams(data=witnessData, skip=1, length=2)

###
# Sort table into common sequence list (csList; just bigrams, without witness data)
###
# sort by depth (high to low), then by uniqueness (rareness) = depth / frequency, then alphabetically
csList = [key for key in
          sorted(csTable, key=lambda k: (k[0] in stopwords and k[1] in stopwords,
                                         -len({entry[0] for entry in csTable[k]}),  # depth (number of witnesses)
                                         len({entry[0] for entry in csTable[k]}) / len(csTable[k]),
                                         # uniqueness (depth/frequency)
                                         k  # alphabetical
                                         ))]

for k in csList:
    print(k, len({entry[0] for entry in csTable[k]}), len({entry[0] for entry in csTable[k]}) / len(csTable[k]))
###
# bitArrays tracks the tokens we've already placed
###
bitArrays = {k: bitarray(len(witnessData[k])) for k in witnessData}  # create a bitarray the length of each witness
for ba in bitArrays.values():  # initialize bitarrays to all 0 values
    ba.setall(0)

# ###
# Build topologically ordered list (toList)
#
# (with progress bar)
# ###
toList = []
toList.extend([Node('#start'), Node('#end')])
for skipgram in tqdm(csList): # skipgram is a tuple of skipgram items; progress bar
    locations = csTable[skipgram]  # list of three-item tuples of (siglum, location1, location2)
    for skipgramPos in range(len(skipgram)):  # loop over head and tail by position ([0, 1])
        norm = skipgram[skipgramPos]  # normalized value of each token in skipgram by position
        for location in locations:  # for each token, get witness and offset within witness
            siglum = location[0]  # witness identifier
            offset = location[skipgramPos + 1]  # offset of token within witness
            if bitArrays[siglum][offset] == 1: # already set, so break for this location
                # print('skipping: ', norm, ' from ', skipgram, ' at ', location)
                continue
            floor = 0
            ceiling = len(toList) - 1
            modifyMe = None  # existing toList entry to be modified; if None, create a new one
            for dictPos in range(len(toList)): # determine floor and ceiling
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
            # if there is a dictionary to modify, do it; otherwise insert a new dictionaryn at the ceiling
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

# ###
# # build list of edges for each witness
# ###
edgeSets = collections.defaultdict(list)  # key = siglum, value = list of node (source, target) tuples
edgeSourceByWitness = {}  # last target will be next source
for node in toList:  # token.norm is str; token.tokendata is dict with siglum:offset items
    if node.norm == '#start':  # not an edge target, so don’t add an edge, but set up source for next edge
        for siglum in witnessData:
            edgeSourceByWitness[siglum] = node
    elif node.norm == '#end':  # create edges to #end for all witnesses
        for siglum in witnessData:
            edgeSets[siglum].append((edgeSourceByWitness[siglum], node))
    else:
        for key, value in node.tokendata.items():
            # add next witness-specific edge, update value in edgeSourceByWitness
            edgeSets[key].append((edgeSourceByWitness[key], node))
            edgeSourceByWitness[key] = node
edges = set(inner for outer in edgeSets.values() for inner in outer)  # tuples of Tokens

###
# index from edge target to source for calculating rank
###
findMySources = collections.defaultdict(list)
for edge in edges:
    findMySources[edge[1]].append(edge[0])

###
# Rank nodes in toList
###
for item in toList:
    inEdges = findMySources[item]
    item.rank = max([r.rank for r in inEdges], default=-1) + 1

###
# index from rank to nodes for retrieval when building table by columns/ranks
###
nodesByRank = collections.defaultdict(list)
for node in toList:
    nodesByRank[node.rank].append(node)

# for key, value in nodesByRank.items():
#     print(key, [(item.norm, item.tokendata) for item in value])

# ###
# # Create alignment table
# ###
table = PrettyTable(header=False)
orderedSigla = sorted(witnessData.keys())
table.add_column(None, [key for key in orderedSigla])
for rank, nodes in nodesByRank.items():  # add a column for each rank
    columnTokens = {}
    for node in nodes:  # copy tokens from all nodes at rank into a single dictionary; value is string (not offset)
        for key in node.tokendata.keys():
            columnTokens[key] = node.norm
    columnData = []
    for siglum in orderedSigla:
        if siglum in columnTokens:
            columnData.append(columnTokens[siglum])
        else:
            columnData.append('')
    table.add_column(None, columnData)

###
# Diagnostic output
###
# print('\n## Input')
# for item in witnessData.items():
#     print(item)
# print('\n## csTable')
pp.pprint(csTable) # full table
# pp.pprint(dict(itertools.islice(csTable.items(), 10))) # first 10 items
print('\n## Formatted iew of csTable')
x = PrettyTable()
x.field_names = ["First", "Second", "Uniqueness", "Depth", "Frequency"]
x.align["First"] = "l"
x.align["Second"] = "l"
x.align["Uniqueness"] = "r"
x.align["Depth"] = "r"
x.align["Frequency"] = "r"
for key, value in csTable.items():
    first, second = key
    frequency = len(value)
    depth = len({item[0] for item in csTable[key]})
    uniqueness = "{0:.4f}".format(depth / frequency)
    x.add_row([first, second, uniqueness, depth, frequency])
print(x.get_string(sort_key=operator.itemgetter(3, 4), sortby="First"))

print('\n## csList (sorted by number of occurrences and then alphabetically, first 10 items)')
pp.pprint(csList) # full list
# pp.pprint(csList[:10]) # first 10 items
print('\n## Nodes in topological order (norm, tokendata, rank): ')
for item in toList:
    print(item, item.tokendata, item.rank)
print('\n## Edges')
# merge witness-specific edge lists into single list
for edge in sorted(edges):
    print(edge[0].norm, edge[0].tokendata, '→', edge[1].norm, edge[1].tokendata)
print('\n## Edge target → sources (norm, tokendata, rank)')
for key, value in edges:
    print(key, key.tokendata, key.rank, '→', value, value.tokendata, key.rank)
print('\n## Nodes by rank')
for key, value in nodesByRank.items():
    print(key, '→' ,value)
print('\n## At last! Alignment table')
print(table)
print(bitArrays)
