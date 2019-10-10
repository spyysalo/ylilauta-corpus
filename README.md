# ylilauta-corpus

Tools and data related to the Ylilauta corpus

Data source: http://urn.fi/urn:nbn:fi:lb-2016101210

Data licence: [CC-BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) (See data/README.txt)

# Processing

## Download and unpack source data

```
wget https://korp.csc.fi/download/Ylilauta/ylilauta_20150304.zip
unzip ylilauta_20150304.zip
```

Reformat to document-per-line format with fastText labels

```
python3 scripts/reformat.py --dedup --fix-text --strip-refs --min-toks 10 \
        ylilauta_20150304.vrt > ylilauta_20150304.txt
```

## Split into train/dev/test

Get label statistics

```
cut -d ' ' -f 1 ylilauta_20150304.txt | perl -pe 's/__label__//' \
        | sort | uniq -c | sort -rn > label_stats.txt
```

Split by label

```
mkdir split
awk '{ print $2 }' label_stats.txt | while read l; do
    egrep "^__label__$l " ylilauta_20150304.txt > split/$l.txt
done
```

Split chronologically into 80% train, 10% dev, 10% test (reformat.py sorts
by date).

```
for f in split/*.txt; do
    t=$(wc -l <$f)
    p80=$((80*t/100))
    p10=$((10*t/100))
    head -n $p80 $f > ${f%.txt}-train.txt
    tail -n +$((p80+1)) $f | head -n $p10 > ${f%.txt}-dev.txt
    tail -n +$((p80+p10+1)) $f > ${f%.txt}-test.txt
done
```

## Create balanced dataset with 10 most frequent labels

```
mkdir sampled
head -n 10 label_stats.txt | awk '{ print $2 }' | while read l; do
    shuf split/${l}-train.txt | head -n 10000 > sampled/${l}-train.txt
    for t in dev test; do
        shuf split/${l}-${t}.txt | head -n 1000 > sampled/${l}-${t}.txt
    done
done
for t in train dev test; do
    cat sampled/*-${t}.txt | shuf > data/ylilauta-${t}.txt
done
```

## Create 10% and 1% subsets of training data

```
for s in 1000 100; do
    mkdir sampled-${s}
    head -n 10 label_stats.txt | awk '{ print $2 }' | while read l; do
        shuf split/${l}-train.txt | head -n $s > sampled-${s}/${l}-train.txt
    done
    cat sampled-${s}/*-train.txt | shuf > data/ylilauta-train-${s}.txt
done
```

## Experiments w/fastText

Setup

```
export FASTTEXT=PATH_TO_FASTTEXT
```

Defaults (expect ~66%)

```
$FASTTEXT supervised -input data/ylilauta-train.txt -output ylilauta.model
$FASTTEXT test ylilauta.model.bin data/ylilauta-dev.txt
```

With more epochs and subwords (~76%)

```
$FASTTEXT supervised -input data/ylilauta-train.txt -output ylilauta.model \
    -minn 3 -maxn 5 -epoch 25
$FASTTEXT test ylilauta.model.bin data/ylilauta-dev.txt
```

Defaults with 10% of training data (~15%)

```
$FASTTEXT supervised -input data/ylilauta-train-1000.txt -output ylilauta.model
$FASTTEXT test ylilauta.model.bin data/ylilauta-dev.txt
```

More epochs and subwords, 10% of training data (~32%)

```
$FASTTEXT supervised -input data/ylilauta-train-1000.txt -output ylilauta.model\
    -minn 3 -maxn 5 -epoch 25
$FASTTEXT test ylilauta.model.bin data/ylilauta-dev.txt
```

Defaults, 1% of training data (~14%)

```
$FASTTEXT supervised -input data/ylilauta-train-100.txt -output ylilauta.model
$FASTTEXT test ylilauta.model.bin data/ylilauta-dev.txt
```

More epochs and subwords, 1% of training data (~20%)

```
$FASTTEXT supervised -input data/ylilauta-train-100.txt -output ylilauta.model\
    -minn 3 -maxn 5 -epoch 25
$FASTTEXT test ylilauta.model.bin data/ylilauta-dev.txt
```
