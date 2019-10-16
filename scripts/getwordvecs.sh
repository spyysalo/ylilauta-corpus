#!/bin/bash

# Download, unpack and convert word vectors

# https://stackoverflow.com/a/246128
SCRIPTDIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

WVDIR="$SCRIPTDIR/../wordvecs"

mkdir -p "$WVDIR"

# polyglot

if [ -e "$WVDIR/polyglot-fi.vec" ]; then
    echo "polyglot-fi.vec exists, skipping ..." >&2
else
    wget http://bit.ly/19bSmJo -O "$WVDIR/polyglot-fi.pkl"
    python3 "$SCRIPTDIR/polyglot2text.py" "$WVDIR/polyglot-fi.pkl" \
	    > "$WVDIR/polyglot-fi.vec"
    rm -f "$WVDIR/polyglot-fi.pkl"
fi

# fastText

if [ -e "$WVDIR/fasttext-wiki.fi.vec" ]; then
    echo "fasttext-wiki.fi.vec exists, skipping ..." >&2
else
    wget 'https://dl.fbaipublicfiles.com/fasttext/vectors-wiki/wiki.fi.vec' \
	 -O "$WVDIR/fasttext-wiki.fi.vec"
fi

if [ -e "$WVDIR/fasttext-cc.fi.300.vec" ]; then
    echo "fasttext-cc.fi.300.vec exists, skipping ..." >&2
else
    wget 'https://dl.fbaipublicfiles.com/fasttext/vectors-crawl/cc.fi.300.vec.gz' \
	 -O "$WVDIR/fasttext-cc.fi.300.vec.gz"
    gunzip "$WVDIR/fasttext-cc.fi.300.vec.gz"
fi

# TurkuNLP

if [ -e "$WVDIR/finnish_4B_parsebank_skgram.bin" ]; then
    echo "finnish_4B_parsebank_skgram.bin exists, skipping ..." >&2
else
    wget 'http://dl.turkunlp.org/finnish-embeddings/finnish_4B_parsebank_skgram.bin' \
	 -O "$WVDIR/finnish_4B_parsebank_skgram.bin"
fi
