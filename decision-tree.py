import pandas as pd
import collections  # for defaultdict
from bitarray import bitarray
import pprint as pp
from prettytable import PrettyTable  # not part of anaconda distribution; install with pip
import \
    pandas_profiling  # https://towardsdatascience.com/10-simple-hacks-to-speed-up-your-data-analysis-in-python
# -ec18c6396e6b
import itertools  # permutations()
import math  # factorial()

pd.set_option('display.max_columns', 100)
pd.set_option('display.max_colwidth', 150)

# sample data with a bit of repetition
witnessData = {'wit1': ['a', 'b', 'c', 'a', 'd', 'e'],
               'wit2': ['a', 'e', 'c', 'd'],
               'wit3': ['a', 'd', 'b']}

# fake stoplist, to ensure that we can identify stopwords and process them last
stoplist = {'a', 'c'}  # set

# bitArrays is used to keep track of which witness tokens have already been processed
bitArrays = {k: bitarray(len(witnessData[k])) for k in witnessData}  # create a bitarray the length of each witness
for ba in bitArrays.values():  # initialize bitarrays to all 0 values
    ba.setall(0)

# csTable: dictionary, in which
#   key: two-item tuple representing skipgram normalized token values (token[0], token[1])
#   value: list of three-item tuples records all locations where the key occurs: (siglum, offset[0], offset[1])
#     In Real Life:
#       values will include the t values corresponding to the normalized token values
#       use a named tuple or dataclass (https://realpython.com/python-data-classes/)
# In this test sample, we find all skip bigrams; in Real Life we would specify parameters for:
#   size of skipgram (bi, tri-, etc.; here bi-)
#   size of window (maximum distance between first and last members of skipgram; here the full witness length)
#   maximum size of skip between members of skipgram (here constrained only by size of window)
csTable = collections.defaultdict(list)
for key, value in witnessData.items():  # key is siglum, value is list of normalized token readings
    # in Real Life the value would also include a non-normalized t property
    for first in range(len(value)):  # all first items in bigram
        for second in range(first + 1, len(value)):  # pair with all following items
            csTable[(value[first], value[second])].append((key, first, second))

# convert to series before df since list lengths vary
csSeries = pd.Series(csTable)

# convert series to dataframe, flatten MultiIndex, label columns
csDf = pd.DataFrame(csSeries).reset_index()
csDf.columns = ["first", "second", "locations"]

# count witnesses for each skipgram (depth of block) and check for uniqueness of skipgram in all witnesses
#   extract sigla inside set comprehension to remove duplicates, then count
csDf["local_witnesses"] = csDf["locations"].map(lambda x: [location[0] for location in x])
csDf["unique_witnesses"] = csDf["local_witnesses"].map(lambda x: set(x))
csDf["local_witnessCount"] = csDf["local_witnesses"].str.len()
csDf["unique_witnessCount"] = csDf["unique_witnesses"].str.len()
csDf["witness_uniqueness"] = csDf["local_witnessCount"] == csDf["unique_witnessCount"]

# are both tokens are stopwords? (if so, we’ll process them last)
csDf["stopwords"] = csDf[["first", "second"]].T.isin(stoplist).all()

# sort and update row numbers, so that we can travese the skipgrams as follows
#   (not currently using stopword list to flter)
#   1. Words that don’t repeat within a witness first
#   2. Within that, deepest block (most witnesses) first
#   3. within that, rarest skipgrams first (less repetition is easier to place correctly)
csDf.sort_values(by=["unique_witnessCount", "witness_uniqueness", "local_witnessCount"], ascending=[False, False, True],
                 inplace=True)
csDf.reset_index(inplace=True, drop=True)  # update row numbers


class Node(object):
    def __init__(self, _norm):
        self.tokendata = {}  # members are tokens (witness:offset pairs); no tokens for start and end nodes
        self.norm = _norm  # string value of node;
        # here all values are pre-normalized, so the n value on the node is equal to the (implicit) t value on the
        # witness tokens in Real Life, witness tokens will have t values that may differ from their shared n value
        # that appears on the node
        self.rank = None

    def __repr__(self):
        return self.norm

    def __lt__(self, other):  # make it sortable by norm value
        return self.norm < other.norm

    def add_location(self, _siglum, _offset):
        self.tokendata[_siglum] = _offset


# Decision-tree node
class dtNode(object):
    ###
    # topologically ordered list, dictionary of bitarrays, dataframe with remaining options
    ###
    def __init__(self, _toList, _bitArrays, _df):
        self.toList = _toList
        self.bitArrays = _bitArrays
        self.df = _df
        self.children = []

    def __repr__(self):
        return str(self.toList)


# root of decision tree inherits empty toList, bitArrays with 0 values, and complete, sorted df
dtRoot = dtNode([], bitArrays, csDf)

# isolate next skipgram to process
current = dtRoot.df.iloc[0, :]

# Identify all possible placements of skipgram
d = collections.defaultdict(list)
for i in current.locations:
    d[i[0]].append(i)
choices = list(itertools.product(*d.values()))
pp.pprint(choices)

# current["first"] and current["second"]
parent = dtRoot
for choice in choices:
    newChild = dtNode(dtRoot.toList.copy(), dtRoot.bitArrays.copy(), dtRoot.df.copy())
    print("\nNew choice:", choice, newChild.bitArrays)
    parent.children.append(newChild)
    for witnessToken in choice:
        print(witnessToken)
        for position, norm in enumerate(
                [current["first"], current["second"]]):  # position (0, 1) is first or second skipgram token
            ###
            # what siglum and offset are we looking for?
            ###
            siglum = witnessToken[0]
            offset = witnessToken[position + 1]
            print(siglum, offset, norm)
            ###
            # do we need to process it, or have we alreaady taken care of it?
            ###
            if newChild.bitArrays[siglum][offset]:  # already set, so break for this location
                print(siglum, offset, norm, "has already been processed")
                continue
            else:
                print("not processed yet; do it now")
            newChild.bitArrays[siglum][offset] = 1  # record that we've processed this token
