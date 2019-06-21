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
    elif token_a < token_b:
        # print(token_a,  " is less than ", token_b, " ", index_i)
        return -1
    else:
        # print(token_a,  " is more than ", token_b, " ", index_i)
        return 1


def _create_suffix_array(_token_array):
    _suffix_array = [item for item in range(0, len(_token_array))]
    _suffix_array = sorted(_suffix_array, key=functools.cmp_to_key(_cmp_tokens_in_token_array))
    return _suffix_array


def create_common_prefix_array():
    global common_prefix_array
    # calculate common prefix array
    # walk over the suffix array
    # check whether the first item is the last as the previous item.
    # We create a list initialized to zero?
    # Or do we just create an empty list
    common_prefix_array = []
    previous = None
    for suffix in suffix_array:
        token = token_array[suffix]
        if token == previous:
            common_prefix_array.append(1)
        else:
            common_prefix_array.append(0)
        previous = token


# show the suffix array
def _show_suffix_array(_suffix_array):
    for token_pointer in _suffix_array:
        sub_token_array = token_array[token_pointer:]
        a = next((idx for idx, x in enumerate(sub_token_array) if x[0] == "$"), 10)
        sub_token_array = sub_token_array[0:a]
        if sub_token_array:
            print(sub_token_array)


# start and end specify an interval over the suffix array
# end is inclusive
def create_skip_bigrams_for_suffix_interval(start, end):
    for suffix_idx in range(start, end+1):
        token_idx = suffix_array[suffix_idx]
        sub_token_array = token_array[token_idx+1:]
        # pay attention to the fix limit that is included here!
        a = next((idx for idx, x in enumerate(sub_token_array) if x[0] == "$"), 10)
        sub_token_array = sub_token_array[0:a]
        if sub_token_array:
            print(sub_token_array)

        # create skip bigrams
        start_token_idx = token_idx
        for end_token_idx in range(start_token_idx+1, start_token_idx+1+a):
            print(start_token_idx, end_token_idx)
    pass


def main():
    # We take a simple example
    # Sample data
    witness_data = {'wit1': ['a', 'b', 'c', 'd', 'e'],
                    'wit2': ['a', 'e', 'c', 'd'],
                    'wit3': ['a', 'd', 'b']}

    global token_array
    token_array, witness_ranges = _prepare_token_array(witness_data)
    print(token_array)
    print(witness_ranges)
    global suffix_array
    suffix_array = _create_suffix_array(token_array)
    print(suffix_array)
    _show_suffix_array(suffix_array)

    create_common_prefix_array()

    print(common_prefix_array)

    # now we are going to try build skipgrams
    # to determine which ones we want we need to build a histogram
    # we do that on a token by token basis
    # First we need to walk over the common prefix array

    prefix_generator = enumerate(common_prefix_array)
    only_ones_generator = ((idx, prefix) for idx, prefix in prefix_generator if prefix == 1)
    only_zeroes_generator = ((idx, prefix) for idx, prefix in prefix_generator if prefix == 0)

    start, common = next(only_ones_generator)
    print("start is ", start-1)
    end, common = next(only_zeroes_generator)
    print("end is ", end-1)

    create_skip_bigrams_for_suffix_interval(start-1, end-1)

    # for idx, has_common_prefix in enumerate(common_prefix_array):
    #     if has_common_prefix == 0:
    #         continue
    #
    #     print("start is ",idx-1)
    #
    #     # need to search for the 0 now
    #     # better use a generator
    #
    #     pass


main()


