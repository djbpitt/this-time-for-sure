# Plain-language overview of how biskipgrams are placed in list containing the topological order of the variant graph

* `csList` is list of normalized skip-bigrams (e.g., `[(‘a','d’), ('b','c’)]`, sorted from deepest to shallowest; split into `normalizedHead` and `normalizedTail` (used later)
* `csTable` has `csList` values (tuples like `('a','b')`) as keys and three-item tuples (actual skip-bigrams, like `('wit1',0,2)`) as values:
	1. siglum (in the example above, 	`'wit1'`)
	1. offset of skipgram head within witness (in the example above, `0`)
	1. offset of skipgram tail within witness (in the example above, `2`)

* `toList` (“topological order”) will be a list of dictionaries with the following key:value pairs:
	* `‘norm’`: normalized form (a string, corresponding to the head or tail of a skipgram), e.g., `norm: 'a'`
	* `siglum`: offset of token within witness, e.g., `'wit1':2`

Seed `toList` with unique `#start` and `#end` `name` values and no `siglum:offset` properties.

1. For each item in `csList`, retrieve `csTable` value, which is a list of three-item tuples (siglum, offset of head in witness, offset of tail in witness) →
1. For each of normalized head and tail →
1, For each location (three-item tuple) retrieved →
1, Select the value from the tuple that corresponds to whether we’re dealing with a head or a tail →
1. We now have:
	1. Normalized head or tail
	1. Siglum (zeroeth item of tuple)
	1. Offset of corresponding real token in witness (first [for head] or second [for tail] item of tuple)

Starting floor is 0; starting ceiling is length of `toList` - 1. Initialize `modifyMe` to `None`; this will be used to hold a reference to an existing dictionary in `toList` that needs to be modified.

1. For each dictionary in `toList` →
1. Does it have a key equal to siglum? If not, `pass`, that is, move on to the next dictionary in `toList`. If so →
1. Compare the value associated with that key in that dictionary to the offset in the witness under consideration at the moment:
	1. If equal, `pass`, since the token is already in `toList`. (Note: We could, in theory, stop at this point, since the token is already there, and we know where. By continuing, we’ll eventually wind up overwriting it with itself, which wastes effort but does not damage the result.) If not →
	1. If the offset value is less than the one we care about, it becomes the new floor, and we move on to the next dictionary in `toList`. If not →
	1. It must be greater, so it becomes the new ceiling. We break at this point, since we want the ceiling to be the lowest value above the one we’re currently trying to place. We now have a floor and ceiling, between which a dictionary may (if the compared values were equal, above) or may not have a key equal to the witness we’re looking at at the moment.
1. Scan from floor toward ceiling, looking for matching ‘norm’ value:
	1. If there is one, add the witness:offset pair to that dictionary and we’re done. It’s possible that this token was already there, in which case we’re overwriting it with itself, harmlessly, except for the wasted effort.
	1. If not, insert witness:offset pair as new dictionary immediately before ceiling.

**TODO:** There may be more than one dictionary between the floor and ceiling that have the same `'norm'` value that we’re interested in. We are arbitrarily choosing the leftmost. Is this a problem?
