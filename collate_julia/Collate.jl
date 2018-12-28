#=
Collate:
- Julia version: 1.0.3
- Author: rhdekker
- Date: 2018-12-28
=#

# create witness data
# TODO: Make ordered dict!

witnessData = Dict( "wit1" => ["a", "b", "c", "d", "e"],
                    "wit2" => ["a", "e", "c","d"],
                    "wit3" => ["a", "d", "b"])

println(typeof(witnessData))
println(witnessData)





# # Sample data
# witnessData = {'wit1': ['a', 'b', 'c', 'd', 'e'],
#                'wit2': ['a', 'e', 'c', 'd'],
#                'wit3': ['a', 'd', 'b']}
#
# witOrders = list(permutations(['wit1', 'wit2', 'wit3']))
# for witOrder in witOrders:
#
#     ###
#     # Construct common sequence table (csTable) of all witnesses as dict
#     ###
#     # key is skip-bigram
#     # value is list of (siglum, pos1, pos2) tuple, with positions of skipgram characters
#     csTable = collections.defaultdict(list)
#     for key in witOrder:
#         value = witnessData[key]
#         for first in range(len(value)):
#             for second in range(first + 1, len(value)):
#                 csTable[(value[first], value[second])].append((key, first, second))
