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
    # remove last marker
    _token_array.pop()
    # note at the moment we do not remove the last marker from the witness ranges.
    return _token_array, _witness_ranges

def _create_suffix_array(_token_array):
    _suffix_array = [item for item in range(1, len(_token_array))]
    # I need a custom comparator
    _suffix_array = sorted(_suffix_array, key=lambda i: _token_array[i])
    print(_suffix_array)


# create suffix array
# the suffix array has the same length as the token array
# for now we fill it with integers counting upwards

# for a in suffix_array
#     println(a)
# end

# sort!(suffix_array, lt=less_than)
# println(suffix_array)

# We take a simple example
# Sample data
witness_data = {'wit1': ['a', 'b', 'c', 'd', 'e'],
                'wit2': ['a', 'e', 'c', 'd'],
                'wit3': ['a', 'd', 'b']}

token_array, witness_ranges = _prepare_token_array(witness_data)
print(token_array)
print(witness_ranges)
_create_suffix_array(token_array)

