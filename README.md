# google-all-pairs-similarity-search-python

Python implementation of the 
[Scaling Up All Pairs Similarity Search](https://static.googleusercontent.com/media/research.google.com/en//pubs/archive/32781.pdf)
paper, with position filter optimization.

## Usage

The input must be a file with each line a `SetID Token` tuple. For example:
```
# Line starts with # will be ignored.
1 a
1 b
1 c
1 d
2 a
2 b
2 c
3 d
3 e
...
```

Example usage:
```bash
./all_pairs.py --input-sets testdata/example_input.txt \
    --output-pairs testdata/example_output.txt \
    --similarity-func jaccard \
    --similarity-threshold 0.1
```

## Benchmark

| Dataset              | Input Num. Tuples | Note | Runtime |
|----------------------|------------|------|---------|
| [Pokec social network (relationships)](https://snap.stanford.edu/data/soc-Pokec.html) 
| 30622564 | Each from-node is a set, each to-node is a token | 16m2s |
