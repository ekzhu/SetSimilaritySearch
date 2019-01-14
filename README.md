# Set Similarity Search

[![Build Status](https://travis-ci.org/ekzhu/SetSimilaritySearch.svg?branch=master)](https://travis-ci.org/ekzhu/SetSimilaritySearch)

Efficient set similarity search algorithms in Python. 
For even better performance see the
[Go Implementation](https://github.com/ekzhu/go-set-similarity-search).

## What is set similarity search?

Let's say we have a database of users and the books they have read.
Assume that we want to recommend "friends" for each user,
and the "friends" must have read very similar set of books
as the user have. We can model this as a set similarity search problem,
by representing each user's books as a set:

```
Alice: {"Anna Karenina", "War and Peace", "The Chameleon", ...}
Bob: {"Lolita", "The Metamorphosis", "The Judgement", ...}
Joey: {"Anna Karenina", "The Chameleon" ...}
```

A popular way to measure the similarity between two sets is 
[Jaccard similarity](https://en.wikipedia.org/wiki/Jaccard_index), which
gives a fractional score between 0 and 1.0. 

There are two versions of set similarity search problem, 
both can be defined given a collection of sets, a 
similarity function and a threshold:

1. *All-Pairs:* find all pairs of sets that have 
similarities greater than (or equal to) the threshold;
2. *Query:* given a query set, from the collection  of sets, find all that
have similarities greater than (or equal to) the threshold with respect to
the query set.

Both versions of the problem can be very computationally expensive 
as the collection can be large and the set sizes can be large. 
The simple brute-force algorithm is O(n^2) for (1) and O(n) for (2).

This package includes a Python implementation of the "All-Pair-Binary" 
algorithm in
[Scaling Up All Pairs Similarity Search](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/32781.pdf)
paper, with additional position filter optimization. 
This algorithm still has the same worst-case complexity as the brute-force 
algorithm, however, by taking advantage of skewness in empirical
distributions of set sizes and frequencies, it often runs much faster
(even better than [MinHash LSH](https://ekzhu.github.io/datasketch/lsh.html)).

## Benchmarks

Run *All-Pairs* on 3.5 GHz Intel Core i7, using similarity function `jaccard` 
and similarity threshold 0.5. 
The running time of [`datasketch.MinHashLSH`](https://ekzhu.github.io/datasketch/lsh.html) is also shown below for 
comparison (`num_perm=32`).

| Dataset | Input Sets | Avg. Size | `SetSimilaritySearch` Runtime | `datasketch` Runtime | `datasketch` Accuracy |
|---------|--------------|--------------|---------|------|--|
| [Pokec social network (relationships)](https://snap.stanford.edu/data/soc-Pokec.html): from-nodes are set IDs; to-nodes are elements | 1432693 | 27.31 | 10m49s | 11m4s | Precision: 0.73; Recall: 0.67 |
| [LiveJournal](https://snap.stanford.edu/data/soc-LiveJournal1.html): from-nodes are set IDs; to-nodes are elements | 4308452 | 16.01 | 28m51s | 31m58s | Precision: 0.79; Recall: 0.74|

Although `datasketch.MinHashLSH` is an approximate algorithm, and I am using `num_perm=32` which is quite low, it is still 
a bit slower than the exact algorithm `SetSimilaritySearch`. 
The time for
creating `datasketch.MinHash` is also included in the end-to-end time, while
in practice this time can be saved through pre-computation. However, for 
*ad hoc* computation of *All-Pairs*, `SetSimilaritySearch` is still
the better choice, especially when sets are small and fit in memory.

Run *Query* on 3.5 GHz Intel Core i7, using similarity function `jaccard` 
and similarity threshold 0.5. 
The query sets are sampled from the dataset itself.
The running time of [`datasketch.MinHashLSH`](https://ekzhu.github.io/datasketch/lsh.html) is also shown below for 
comparison (`num_perm=32`).

| Dataset | Indexed Sets | Query Sets | Avg. Size | `SetSimilaritySearch` Indexing & Querying Time | `datasketch` Indexing & Querying Time | `datasketch` Accuracy |
|--|--|--|--|--|--|--|
| [Pokec social network (relationships)](https://snap.stanford.edu/data/soc-Pokec.html): from-nodes are set IDs; to-nodes are elements | 1432693 | 10k | 27.31 | Indexing: 1m7s; Querying (90pct): 2.3ms | Indexing: 9m23s; Querying (90pct): 0.72ms | Precision: 0.90; Recall: 0.88 |
| [LiveJournal](https://snap.stanford.edu/data/soc-LiveJournal1.html): from-nodes are set IDs; to-nodes are elements | 4308452 | 10k | 16.01 | Indexing: 2m32s; Querying (90pct): 1.6ms | Indexing: 30m58s; Querying (90pct): 2.1ms | Precision: 0.85; Recall: 0.78|

The indexing time for `datasketch.MinHashLSH`, including the time for 
creating `datasketch.MinHash`, is much worse than `SetSimilaritySearch` --
nearly 10x and 15x. Therefore `SetSimilaritySearch` is much better for 
*ad hoc* computation of the *Query* problem. For the scenario in which the same 
search index is reused for many *Query* problems, `datasketch.MinHashLSH` is 
faster than `SetSimilaritySearch` when the set sizes are large. This is 
easy to understand: the size of `datasketch.MinHash` is constant, wheres 
a set can be arbitrarily large, so the query time for large sets is faster
when sketch is used. However, when the set sizes become smaller, the sketch 
looses its advantage.

## Install

```bash
pip install -U SetSimilaritySearch
```

## Library usage

For *All-Pairs*, it takes an input of a list of sets, and output pairs that
meet the similarity threshold.

```python
from SetSimilaritySearch import all_pairs

# The input sets must be a Python list of iterables (i.e., lists or sets).
sets = [[1,2,3], [3,4,5], [2,3,4], [5,6,7]]
# all_pairs returns an iterable of tuples.
pairs = all_pairs(sets, similarity_func_name="jaccard", 
        similarity_threshold=0.1)
list(pairs)
# [(1, 0, 0.2), (2, 0, 0.5), (2, 1, 0.5), (3, 1, 0.2)]
# Each tuple is (<index of the first set>, <index of the second set>, <similarity>).
# The indexes are the list indexes of the input sets.
```

For *Query*, it takes an input of a list of sets, and builds a search index
that can compute any number of queries. Currently the search index only 
supports a static collection of sets with no updates.

```python
from SetSimilaritySearch import SearchIndex

# The input sets must be a Python list of iterables (i.e., lists or sets).
sets = [[1,2,3], [3,4,5], [2,3,4], [5,6,7]]
# The search index cannot be updated.
index = SearchIndex(sets, similarity_func_name="jaccard", 
    similarity_threshold=0.1)
# The query function takes input a set.
results = index.query([5,3,4])
results
# [(1, 1.0), (0, 0.2), (2, 0.5), (3, 0.2)]
# Each tuple is (<index of the found set>, <similarity>).
# The index is the list index of the sets in the search index.
```


Supported similarity functions (more to come):
* [Jaccard](https://en.wikipedia.org/wiki/Jaccard_index): intersection size divided by union size; set `similarity_func_name="jaccard"`.
* [Cosine](https://en.wikipedia.org/wiki/Cosine_similarity): intersection size divided by square root of the product of sizes; set `similarity_func_name="cosine"`.
* [Containment](https://ekzhu.github.io/datasketch/lshensemble.html#containment): intersection size divided by the size of the first set (or query set); set `similarity_func_name="containment"`.


## Command line usage

You can also use the command line program `all_pairs.py`.
The input must be **one or two** files with each line a **unique** `SetID Token` 
tuple. 
For example:
```
# Line starts with # will be ignored.
# Each line is <Set ID> <Token (i.e. Set Element)>, separate by a whitespace or tab.
# Every line must be unique.
1 a
1 b
1 c
1 d
2 a
2 b
2 c
3 d
3 e
```
When one input file is given, it computes *All-Pairs*; when two input files 
are given, it computes *Query* by building a search index on the first
collection and querying with sets from the second collection -- effectively
computes cross-collection pairs.

Example usage (*All-Pairs*):
```bash
all_pairs.py --input-sets testdata/example_input.txt \
    --output-pairs testdata/example_output.txt \
    --similarity-func jaccard \
    --similarity-threshold 0.1
```

