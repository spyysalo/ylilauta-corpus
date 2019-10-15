#!/usr/bin/env python3

# Convert pickled polyglot word embeddings to word2vec text format

import sys
import pickle


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('-e', '--encoding', default='latin1')
    ap.add_argument('file')
    return ap


def main(argv):
    args = argparser().parse_args(argv[1:])
    with open(args.file, 'rb') as f:
        words, embeddings = pickle.load(f, encoding=args.encoding)
    print(len(embeddings), len(embeddings[0]))
    for w, e in zip(words, embeddings):
        print(w, ' '.join(str(v) for v in e))
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
