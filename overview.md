# Plain-language overview of how skip bigrams are placed in list according to the topological order of the variant graph

## Principal variables

* `csTable` has `csList` values (tuples like `('a','b')`) as keys and lists of three-item tuples (actual skip bigrams, like `('wit1',0,2)`) as values:
	1. siglum (in the example above, 	`'wit1'`)
	1. offset of skipgram head within witness (in the example above, `0`)
	1. offset of skipgram tail within witness (in the example above, `2`)

* `csList` is list of normalized skip-bigrams (e.g., `[(‘a','d’), ('b','c’)]`, sorted from deepest to shallowest; split into `normalizedHead` and `normalizedTail` (used later)

* `toList` (“topological order”) is a list of dictionaries with the following key:value pairs:
	* `'norm'`: normalized form (a string, corresponding to the head or tail of a skipgram), e.g., `'norm': 'a'`
	* `siglum`: offset of token within witness, e.g., `'wit1':2`

## Process

### Find the location of each normalized form in each witness

Seed `toList` (eventually a tuple of name; dictionary of `siglum:offset` pairs; and rank) with unique `#start` and `#end` `name` values and no `siglum:offset` properties.

Use each item in `csList` to retrieve a `csTable` value, which is a list of three-item tuples (siglum, offset of head in witness, offset of tail in witness)

```
For each of normalized head and tail in the csList
    For each location (three-item tuple) retrieved for the head or tail
        Select the value from the tuple that corresponds to whether we’re dealing with a head or a tail
```

We now have, for each normalized value (with repetition):

1. Normalized head or tail (from `csList`), used to retrieve a list of three-item tuples from `csTable`
1. Siglum (zeroeth item of retrieved tuple)
1. Offset of corresponding real token in witness (first [for head] or second [for tail] item of retrieved tuple)

### Locate the item in the topological order

Starting floor is `0`; starting ceiling is length of `toList` - 1. Initialize `modifyMe` to `None`; this will be used to hold a reference to an existing node in `toList` that needs to be modified.

```
For each node in `toList`, does it have a key equal to siglum? 
    If not, `pass`, that is, move on to the next dictionary in `toList`.
    If so, compare the value associated with that key in that dictionary to the offset in the witness under consideration
        If equal, `pass`, since the token is already in `toList`.* 
	    If the offset value is less than the one we care about, it becomes the new floor, and we move on to the next dictionary in `toList`
	    If not, it must be greater, so it becomes the new ceiling.
```
	    
\* We could stop at this point, since the token is already there, and we know where. By continuing, we’ll eventually wind up overwriting it with itself, which wastes effort but does not damage the result.) If not →

We break at this point, since we want the ceiling to be the lowest value above the one we’re currently trying to place. We now have a floor and ceiling, between which a dictionary may (if the compared values were equal, above) or may not have a key equal to the witness we’re looking at at the moment.
Scan from floor toward ceiling, looking for matching `'norm’` valuea:

    If there is one, add the witness:offset pair to that dictionary and we’re done.* 
    If not, insert witness:offset pair as new dictionary immediately before ceiling.

\* It’s possible that this token was already there, in which case we’re overwriting it with itself, harmlessly, except for the wasted effort.

**TODO:** There may be more than one dictionary between the floor and ceiling that have the same `'norm'` value that we’re interested in. We are arbitrarily choosing the leftmost. Is this a problem?

____

Stopword list is based on NLTK English stopwords, with partials (e.g., `didn`, `t`) removed.