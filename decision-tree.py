import pandas as pd
import collections  # for defaultdict
from bitarray import bitarray
import pprint as pp
import copy
from prettytable import PrettyTable  # not part of anaconda distribution; install with pip
import itertools  # permutations()


class Node(object):
    """Node in topologically ordered list"""

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


class dtNode(object):
    """Node in decision tree"""

    def __init__(self, _toList, _bitArray_dict, _df):
        self.toList = _toList  # topologically ordered list
        self.bitArray_dict = _bitArray_dict  # dictionary of bitarray
        self.df = _df  # dataframe with remaining options
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


def create_alignment_table(_toList: list, _witnessData: dict, _nodesByRank: pd.DataFrame, _offsets=None) -> PrettyTable:
    """Create alignment table as PrettyTable

    :param _toList: list: Node() objects
    :param _witnessData: dict: sigla as keys and lists of tokens as values
    :param _nodesByRank: pd.DataFrame: norm, tokendata, and rank of nodes
    :param _offsets: bool: print offsets for debugging
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
                if _offsets:
                    _columnTokens[_key] += "".join(["(", str(_node.tokendata[_key]), ")"])
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


def calculate_score(_node: dtNode) -> float:
    """  Score = witness tokens placed / length of toList

    :param _node: dtNode to score
    :return: score as float
    """
    wit_tokens_placed: int = sum([len(item.tokendata) for item in _node.toList])
    toList_length: int = len(_node.toList) - 2
    score: float = wit_tokens_placed / toList_length
    return score


def place_token(_toList, _norm, _siglum, _offset):
    ###
    # since we didn’t break, create a new node and figure out where to place it
    ###
    _modifyMe = None  # flag that tells us whether we need to modify an existing node (or create a new one)
    _floor = 0  # floor and ceiling frame the locations where the new node can be placed
    _ceiling = len(_toList) - 1
    ###
    # find floor and ceiling
    ###
    for _nodePos in range(len(_toList)):  # determine floor and ceiling by scanning nodes
        _currentDict = _toList[_nodePos].tokendata  # keys are a list of witnesses on token
        if _siglum not in _currentDict.keys():  # this dictionary isn't relevant; look at the next one
            pass
        else:  # is it a new floor or a new ceiling? (we've already filtered out the == case)
            if _currentDict[_siglum] < _offset:  # move up the floor if the new offset is
                # greater than a node already there
                _floor = _nodePos + 1
            else:  # we’ve hit the ceiling if the new offset is less than the old one
                _ceiling = _nodePos
                break

    ###
    # scan from floor to ceiling, looking for matching 'norm' value
    #
    # if there is a dictionary to modify, save it as modifyMe (don't modify it yet)
    # TODO: this gets the leftmost if there is more than one, which is not necessarily optimal
    ###
    for _pos in range(_floor, _ceiling):
        if _toList[_pos].norm == _norm:
            _modifyMe = _toList[_pos]
            break
    ###
    # if there is a dictionary to modify, do it; otherwise insert a new dictionary at the ceiling
    # TODO: why at the ceiling?
    ###
    if _modifyMe is None:  # create and insert new token
        _new_token = Node(_norm)
        _new_token.add_location(_siglum, _offset)
        _toList.insert(_ceiling, _new_token)
    else:  # modify existing token
        _modifyMe.tokendata[_siglum] = _offset
    return _toList


def compute_priority(_df: pd.DataFrame):
    """ Assign processing priority to skipgrams and use it to group and sort them

    :param _df: dataframe to prioritize
    :return: (none)

    (not currently using stopword list to filter)
    1. Deepest block (most witnesses) first (unique_witnessCount: int)
    2. Within that, words that don’t repeat within a witness first (witness_uniqueness: bool)
    3. within that, rarest skipgrams first (less repetition is easier to place correctly) (local_witnessCount: int)
    """
    _df.sort_values(by=["unique_witnessCount", "witness_uniqueness", "local_witnessCount"],
                    ascending=[False, False, True], inplace=True)
    _df.reset_index(inplace=True, drop=True)  # update row numbers


def step(_df: pd.DataFrame):
    """walk through rows grouped by priority"""
    _top = max(_df["priority"])
    _current = _df[_df["priority"] == _top]
    _remainder = _df[_df["priority"] != _top]
    return(_current, _remainder) # process current, then call again with remainder to continue


def expand_dtNode(_parent: dtNode):
    """ Add children to node in decision tree

    :param _parent: dtNode: decision tree node to be expanded
    :return: (none; expands in place)
    """
    # isolate next skipgram to process
    _current: pd.Series = _parent.df.iloc[0, :]
    # _current, _remainder = step(_parent)
    # Identify all possible placements of skipgram
    _d = collections.defaultdict(list)
    for _i in _current.locations:
        _d[_i[0]].append(_i)
    _choices: list = list(itertools.product(*_d.values()))
    print("There are", len(_choices), "choices at this level")
    for _choice in _choices:
        _newChild = dtNode(copy.deepcopy(_parent.toList), copy.deepcopy(_parent.bitArray_dict),
                           _parent.df.copy().iloc[1:, :])  # pop top of parent df and copy remainder to child
        _parent.children.append(_newChild)  # parents know who their children are
        for _witnessToken in _choice:
            for _position, _norm in enumerate(
                    [_current["first"], _current["second"]]):  # position (0, 1) is first or second skipgram token
                ###
                # what siglum and offset are we looking for?
                ###
                _siglum: str = _witnessToken[0]
                _offset: int = _witnessToken[_position + 1]
                ###
                # do we need to process it, or have we already taken care of it?
                ###
                # print(_newChild.bitArray_dict)
                if _newChild.bitArray_dict[_siglum][_offset]:  # already set, so break for this location
                    continue
                else:
                    place_token(_newChild.toList, _norm, _siglum, _offset)
                    _newChild.bitArray_dict[_siglum][_offset] = 1  # record that we've processed this token


def print_alignment_table(_dtNode: dtNode, _witnessData: dict, _print_witness_offset):
    """ Print alignment table for decision tree node

    :param _dtNode: dtNode: node to print
    :param _witnessData: dict: witness token input
    :param _print_witness_offset: bool: print offset of token in witness?
    :return: (none)
    """
    print(create_alignment_table(_dtNode.toList, _witnessData,
                                 rank_nodes(_dtNode.toList, create_edge_list(_dtNode.toList)), _print_witness_offset))


def print_score(_dtNode: dtNode):
    """ Print calculated score for decision tree node

    :param _dtNode: dtNode: decision tree node to score
    :return: (none)
    """
    print("Score (witness tokens / toList length): ", calculate_score(_dtNode))


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
scale = pd.Series([100, -1, 10])
csDf["priority"] = pd.np.dot(csDf[["unique_witnessCount", "witness_uniqueness", "local_witnessCount"]], scale)

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

# process root
parent: dtNode = dtRoot
expand_dtNode(parent)  # expands in place, adds children
print(parent.children)

# current, remainder = step(csDf)
# print("current", current)
# print("remainder", remainder)
#
# current,remainder = step(remainder)
# print("current", current)
# print("remainder", remainder)
#
# current,remainder = step(remainder)
# print("current", current)
# print("remainder", remainder)
#
# current,remainder = step(remainder)
# print("current", current)
# print("remainder", remainder)

# expand_dtNode(parent)  # expands in place, adds children
# for child in parent.children:
#     print("One level down")
#     print_alignment_table(child, witnessData, True)  # before expanding
#     print_score(child)
#     expand_dtNode(child)  # adds grandchildren
#     for grandchild in child.children:
#         print("Two levels down")
#         print_alignment_table(grandchild, witnessData, True)
#         print_score(grandchild)
