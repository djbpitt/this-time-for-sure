# Plain-language overview of how biskipgrams are placed in list containing the topological order of the variant graph

* `csList` is list of normalized biskipgrams (e.g., `[‘ad’, ‘bc’]`, sorted from deepest to shallowest; split into `normalizedHead` and `normalizedTail` (used later)
* `csTable` has `csList` values as keys and three-item tuples (actual [prenormalized] biskipgrams) as values:
	1. siglum
	1. offset of skipgram head within witness
	1. offset of skipgram tail within witness

* `toList` (“topological order”) will be a list of dictionaries with the following key:value pairs:
	* `‘norm’`: normalized form
	* `siglum`: offset (for each witness)

Seed `toList` with unique `#start` and `#end` `name` values and no `siglum:offset` properties.

1. For each item in `csList`, retrieve `csTable` value, which is a list of three-item tuples (siglum, offset of head in witness, offset of tail in witness) →
1. For each of normalized head and tail →
1, For each three-item tuple retrieved →
1, Select the value from the tuple that corresponds to whether we’re dealing with a head or a tail →
1. We now have:
	1. Normalized head or tail
	1. Siglum (zeroeth item of tuple)
	1. Offset in witness (first [for head] or second [for tail] item of tuple)

Starting floor is 0; starting ceiling is length of `toList` - 1 (initially, then, `#start` and `#end`).

1. For each dictionary in toList →
1. Does it have a key equal to siglum? If not, move on. If so →
1. Compare the value associated with that key to the offset in witness:
	1. If equal, break out, since the token is already in toList. If not →
	1. If the offset value is less than the one we care about, it becomes the new floor; keep going. If not →
	1. It must be greater, so it becomes the new ceiling. In any case, we now have a floor and ceiling, between which no dictionary has a key equal to the witness we’re looking at at the moment.
1. Scan from floor toward ceiling, looking for matching ‘norm’ value:
	1. If there is one, add the witness:offset pair to that dictionary and you’re done
	1. If not, insert witness:offset pair as new dictionary immediately before ceiling.

**TODO:** There may be more than one dictionary between the floor and ceiling that have the same `'norm'` value that we’re interested in. We are arbitrarily choosing the leftmost. Is this a problem?
