import collections

# Note
# Single-token witnesses are not processed because they have no bigrams; this is an error

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

# Sort table into common sequence list (csList)
#   ordered by 1) number of witnesses (numerica high to low) and 2) sequence (alphabetic low to high)
csList = [(k, csTable[k]) for k in sorted(csTable, key=lambda k: (-len(csTable[k]), k))]

# Build topologically ordered list (toList)
toList = []
for bigram, locations in csList:
    first, second = list(bigram)
    print(first, second, (locations))

# Diagnostic output
# print(csList)
