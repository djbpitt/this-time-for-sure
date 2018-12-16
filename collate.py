import collections

# Sample data
witnessData = {'wit1': ['a', 'b', 'c', 'd', 'e'], 'wit2': ['a', 'e', 'c', 'd'], 'wit3':['a', 'd', 'b']}

# Construct common sequence table (csTable) of all witnesses as dict
# key is skipbigram
# value is list of (siglum, pos1, pos2) tuple, with positions of skipgram characters

csTable = collections.defaultdict(list)
for key, value in witnessData.items():
    for first in range(len(value)):
        for second in range(first + 1, len(value)):
            csTable[value[first] + value[second]].append((key, first, second))

# Diagnostic output
print(csTable)
