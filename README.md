# set-similarity-search

## What is set similarity search?

Let's say we have a database of users and books they have read.
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

The set similarity search problem is given a 
collection of sets, a 
similarity function and a threshold, find all pairs of sets that have 
similarities greater than (or equal to) the threshold. 
This can be very computationally expensive as 1) the number of sets is 
large and 2) the set sizes are large. The simple brute-force algorithm
is O(n^2).

This package includes a Python implementation of the "All-Pair-Binary" algorithm in
[Scaling Up All Pairs Similarity Search](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/32781.pdf)
paper, with additional position filter optimization. 
This algorithm still runs in
O(n^2) in the worst case, however, by taking advantage of skewness in empirical
distributions of frequency, it often runs much faster.

## Usage

The input must be a file with each line a **unique** `SetID Token` tuple. 
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

Example usage:
```bash
./all_pairs.py --input-sets testdata/example_input.txt \
    --output-pairs testdata/example_output.txt \
    --similarity-func jaccard \
    --similarity-threshold 0.5
```

Supported similarity functions (more to come):
* [Jaccard](https://en.wikipedia.org/wiki/Jaccard_index): intersection size divided by union size
* [Cosine](https://en.wikipedia.org/wiki/Cosine_similarity): intersection size divided by square root of the product of sizes


## Benchmarks

Running on 3.5 GHz Intel Core i7, using similarity function `jaccard` and 
similarity threshold 0.5.

| Dataset | Input Sets | Output Pairs | Runtime | Note |
|---------|--------------|--------------|---------|------|
| [Pokec social network (relationships)](https://snap.stanford.edu/data/soc-Pokec.html) | 1432693 | 355215 | 16m2s | Each from-node is a set; each to-node is a token |
| [LiveJournal](https://snap.stanford.edu/data/soc-LiveJournal1.html) | 4308452 |  |  | Each from node is a set; each to-node is a token |
