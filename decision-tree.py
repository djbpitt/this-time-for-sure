import pandas as pd
import collections  # for defaultdict
from bitarray import bitarray
import pprint as pp
import copy
from prettytable import PrettyTable  # not part of anaconda distribution; install with pip
import itertools  # permutations()


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
    def __init__(self, _toList, _bitArray_dict, _df):
        self.toList = _toList
        self.bitArray_dict = _bitArray_dict
        self.df = _df
        self.children = []

    def __repr__(self):
        return str(self.toList)


def create_edge_list(_toList: list) -> set:
    """Create and return aa list of edges from the topologically ordered list of alignment nodes

    :param _toList: list of Node() objects
    :return: set of directed edges as (source, target) tuples
    """
    _edgeSets = collections.defaultdict(list)  # key = siglum, value = list of node (source, target) tuples
    _edgeSourceByWitness = {}  # last target will be next source
    for _node in _toList:  # token.norm is str; token.tokendata is dict with siglum:offset items
        if _node.norm == '#start':  # not an edge target, so don’t add an edge, but set up source for next edge
            for _siglum in witnessData:
                _edgeSourceByWitness[_siglum] = _node
        elif _node.norm == '#end':  # create edges to #end for all witnesses
            for _siglum in witnessData:
                _edgeSets[_siglum].append((_edgeSourceByWitness[_siglum], _node))
        else:
            for _key, _value in _node.tokendata.items():
                # add next witness-specific edge, update value in edgeSourceByWitness
                _edgeSets[_key].append((_edgeSourceByWitness[_key], _node))
                _edgeSourceByWitness[_key] = _node
    _edges = set(_inner for _outer in _edgeSets.values() for _inner in _outer)  # tuples of Tokens
    return _edges


def rank_nodes(_toList: list, _edges: set) -> pd.DataFrame:
    """Rank nodes and return df

    :param _toList: list of Node() objects
    :param _edges: set of directed edges (source, target) tuples
    :return: norm, tokendata, and rank of nodes as df
    """
    _findMySources = collections.defaultdict(list)
    for _edge in _edges:
        _findMySources[_edge[1]].append(_edge[0])
    for _item in _toList:
        _inEdges = _findMySources[_item]
        _item.rank = max([r.rank for r in _inEdges], default=-1) + 1
    _node_table = pd.DataFrame([(_item, _item.tokendata, _item.rank) for _item in _toList])
    _node_table.columns = ["norm", "tokendata", "rank"]
    return _node_table


def create_alignment_table(_toList: list, _witnessData: dict, _nodesByRank: pd.DataFrame) -> PrettyTable:
    """Create alignment table as PrettyTable

    :param _toList: list of Node() objects
    :param _witnessData: dictionary with sigla as keys and lists of tokens as values
    :param _nodesByRank: norm, tokendata, and rank of nodes as df
    :return: ASCII alignment table as PrettyTable
    """
    _nodesByRank = collections.defaultdict(list)
    for _node in _toList:
        _nodesByRank[_node.rank].append(_node)
    _table = PrettyTable(header=False)
    _orderedSigla = sorted(_witnessData.keys())
    _table.add_column(None, [_key for _key in _orderedSigla])
    for _rank, _nodes in _nodesByRank.items():  # add a column for each rank
        _columnTokens = {}
        for _node in _nodes:  # copy tokens from all nodes at rank into a single dictionary; value is string (not
            # offset)
            for _key in _node.tokendata.keys():
                _columnTokens[_key] = _node.norm
        _columnData = []
        for _siglum in _orderedSigla:
            if _siglum in _columnTokens:
                _columnData.append(_columnTokens[_siglum])
            elif _node.norm in ["#start", "#end"]:
                _columnData.append(_node.norm)
            else:
                _columnData.append('')
        _table.add_column(None, _columnData)
    return _table


# sample data with a bit of repetition
witnessData = {'wit1': ['a', 'b', 'c', 'a', 'd', 'e'],
               'wit2': ['a', 'e', 'c', 'd'],
               'wit3': ['a', 'd', 'b']}

# fake stoplist, to ensure that we can identify stopwords and process them last
stoplist = {'a', 'c'}  # set

# bitArray_dict is used to keep track of which witness tokens have already been processed
bitArray_dict = {k: bitarray(len(witnessData[k])) for k in witnessData}  # create a bitarray the length of each witness
for ba in bitArray_dict.values():  # initialize bitarrays to all 0 values
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

# sort and update row numbers, so that we can traverse the skipgrams as follows
#   (not currently using stopword list to filter)
#   1. Words that don’t repeat within a witness first
#   2. Within that, deepest block (most witnesses) first
#   3. within that, rarest skipgrams first (less repetition is easier to place correctly)
csDf.sort_values(by=["unique_witnessCount", "witness_uniqueness", "local_witnessCount"], ascending=[False, False, True],
                 inplace=True)
csDf.reset_index(inplace=True, drop=True)  # update row numbers

# root of decision tree inherits empty toList, bitArray_dict with 0 values, and complete, sorted df
dtRoot = dtNode([Node("#start"), Node("#end")], bitArray_dict, csDf)

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
    newChild = dtNode(parent.toList.copy(), copy.deepcopy(parent.bitArray_dict), parent.df.copy())
    print("\nNew choice:", choice, newChild.bitArray_dict)
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
            # do we need to process it, or have we already taken care of it?
            ###
            if newChild.bitArray_dict[siglum][offset]:  # already set, so break for this location
                print(siglum, offset, norm, "has already been processed")
                continue
            else:
                print("not processed yet; do it now")
            newChild.bitArray_dict[siglum][offset] = 1  # record that we've processed this token
    print(create_alignment_table(newChild.toList, witnessData,
                                 rank_nodes(newChild.toList, create_edge_list(newChild.toList))))

