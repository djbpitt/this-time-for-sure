#
# Goal: Skipgram indexing the witnesses.
# Want to tokenize the witnesses (We skip that in the first example)
#
# @author: Ronald Haentjens Dekker
# 18-06-2019
#
# 1. Create the token array by chaining the tokens of all the witnesses together.
# 2. Create a suffix array by sorting the suffix array using a special comparator.
#
#
#

import functools


# this method creates both the token array and the witness ranges dictionary
def _prepare_token_array(_witness_data):
    counter = 0
    _token_array = []
    _witness_ranges = {}
    for idx, sigil in enumerate(_witness_data):
        witness_tokens = _witness_data[sigil]
        # print("witness.tokens", witness)
        witness_range = (counter, counter + len(witness_tokens))
        # the extra one is for the marker token
        counter += len(witness_tokens) + 1
        _witness_ranges[sigil] = witness_range
        _token_array.extend(witness_tokens)
        # add marker token
        _token_array.append('$' + str(idx))
    return _token_array, _witness_ranges


# Custom comparator
def _cmp_tokens_in_token_array(index_i, index_j):
    # print("Asked for:", index_i, index_j)
    token_a = token_array[index_i]
    token_b = token_array[index_j]
    # TODO: this has to be in a loop, rather then recursive
    if token_a == token_b:
        # print(index_i, " ", token_a, " and ", index_j, " are equal; checking next")
        # check exit condition
        if index_i < len(token_array)-1 and index_j < len(token_array)-1:
            # compare the next token.
            return _cmp_tokens_in_token_array(index_i+1, index_j+1)
        # print("We are close to running out of bounds")
        return 0
    else:
        if token_a < token_b:
            # print(token_a,  " is less than ", token_b, " ", index_i)
            return -1
        else:
            # print(token_a,  " is more than ", token_b, " ", index_i)
            return 1


def _create_suffix_array(_token_array):
    _suffix_array = [item for item in range(0, len(_token_array))]
    _suffix_array = sorted(_suffix_array, key=functools.cmp_to_key(_cmp_tokens_in_token_array))
    print(_suffix_array)

# We take a simple example
# Sample data
witness_data = {'wit1': ['a', 'b', 'c', 'd', 'e'],
                'wit2': ['a', 'e', 'c', 'd'],
                'wit3': ['a', 'd', 'b']}

token_array, witness_ranges = _prepare_token_array(witness_data)
print(token_array)
print(witness_ranges)
_create_suffix_array(token_array)

