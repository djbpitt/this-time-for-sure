# Scoring

## Input data

Witness | Token | Token | Token | Token | Token | Token
---|---|---|---|---|---|---
wit1|a|b|c|a|d|e
wit2|a|e|c|-|d|-
wit3|a|-|-|-|d|b

The table above reflects the optimal alignment, which corresponds to the following partially ordered topological sort, which has a length of 8:

a, (b ~ e), c, a, d, (b ~ e)

## Outcome constraints

1. Valid topological orders must be compatible with the token order of all witnesses.
2. Valid final topological orders must be compatible with 100% of the tokens in all witnesses.

## Operational considerations

1. We have no control over token repetition within witnesses.
2. We want to minimize transpositions, since transposition is the source of extra duplicate nodes (extra = beyond those required by repetition within a witness).

## Scoring observations

### Best case

1. Crudely, and not entirely precisely or correctly, the shortest possible topological order is equal to the length of longest witness. in this case, that value is 6 (length of `wit1`, which is the longest witness).
1. More specifically, and more precisely and correctly, the shortest possible topological order is `sum(max(freq(token, witness)))`, where `freq(token, witness)` is the number of times a particular `token` occurs in a particular `witness`, for each witness in the collation set. In this case, that value is 6: the maximum number of occurrences of `a` in any witness is 2 in `wit1`, and the maximum number of occurrentces of each of the other four types (`b`, `c`, `d`, and `e`) is 1, since none of them repeats in any witness.
1. The actual best case (shortest possible topological order) with the sample data is 8 because `b` and `e` are both transposed, and therefore must both be doubled in the topological order.

### Worst case

1. In general, the worst case is that no token occurs in more than one witness, in which case the shortest possible topological order is the sum of the lengths of all of the witnesses.

## Scoring considerations

1. Total score for any node on the decision tree is the sum of the actual and potential scores. For that reason, the two scores must observe the same scale.
1. Each step moves tokens from the potential score to the actual score. 


### Actual score

1. The actual score takes order into account.
3. The best actual score maximizes the information value per node. For example, given 2 nodes with a total of 4 tokens, the *average* information value of each node is 2 in both cases. But we prefer 3 tokens on 1 node and 1 token on the other to 2 tokens on each. Therefore:
	4. We cannot just average the tokens per node, since that value would be 2 in both of the preceding cases.
	5. We could, instead, square each number of tokens per node and divide by the number of nodes. In that case, 3 and 1 would yield 5 (3^2 + 1^2 = 9 + 1 = 10; then divide by 2) and 2 and 2 would yield 4 (2^2 + 2^2 = 4 + 4 = 8; then divide by 2).

### Potential score

1. Potential score makes optimistic judgments, that is, the best possible potential score.
1. The potential score is the best clustering you can make with the tokens yet to be placed, given the existing clusters. 
	2. The best case is that they can all be accommodated in existing clusters, and require no new nodes.
1. The potential score ignores order.
