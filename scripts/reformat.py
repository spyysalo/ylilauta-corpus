#!/usr/bin/env python3

import sys
import re

from xml.sax.saxutils import unescape

try:
    import ftfy
except ImportError:
    ftfy = None


TEXT_START_RE = re.compile(r'^<text .*?\bdate="([^"]*)".*\bsec="([^"]*)".*>$')

TEXT_END_RE = re.compile(r'^</text>$')

REF_RE = re.compile(r'^>>[0-9]+$')


def argparser():
    from argparse import ArgumentParser
    ap = ArgumentParser()
    ap.add_argument('-d', '--dedup', default=False, action='store_true',
                    help='skip duplicate texts')
    ap.add_argument('-f', '--fix-text', default=False, action='store_true',
                    help='run ftfy to fix broken Unicode')
    ap.add_argument('-i', '--include-date', default=False, action='store_true',
                    help='include text date in output')
    ap.add_argument('-m', '--min-toks', default=None, type=int,
                    help='minimum number of tokens in text to output')
    ap.add_argument('-s', '--strip-refs', default=False, action='store_true',
                    help='strip text-initial comment references')
    ap.add_argument('file', nargs='+')
    return ap


def is_tag(line):
    return line.startswith('<') and line.endswith('>')


def is_conll(line):
    fields = line.split('\t')
    return len(fields) == 8


def format_date(date):
    m = re.match(r'^(\d+)\.(\d+)\.(\d+)$', date)
    if not m:
        raise ValueError(date)
    day, month, year = (int(i) for i in m.groups())
    return '{}-{:02d}-{:02d}'.format(year, month, day)


def process_text(text, sec, date, options):
    if not text:
        return None
    text = [unescape(t) for t in text]
    if options.strip_refs:
        text = [t for t in text if not REF_RE.match(t)]
    if options.min_toks and len(text) < options.min_toks:
        return
    text = ' '.join(text)
    if text in process_text.seen:
        return None
    process_text.seen.add(text)
    text = text.replace('\u0080', '/')    # always fix
    if options.fix_text:
        text = ftfy.fix_text(text)
    date = format_date(date)
    return [date, sec, text]
process_text.seen = set()


def read_texts(fn, options):
    texts = []
    current_text, current_sec, current_date = None, None, None
    with open(fn) as f:
        for ln, l in enumerate(f, start=1):
            l = l.rstrip()
            if TEXT_START_RE.match(l):
                # text starts
                m = TEXT_START_RE.match(l)
                assert current_text == None
                current_text = []
                current_date = m.group(1)
                current_sec = m.group(2)
                continue
            elif TEXT_END_RE.match(l):
                # text ends
                t = process_text(current_text, current_sec,
                                 current_date, options)
                if t is not None:
                    texts.append(t)
                current_text, current_sec, current_date = None, None, None
                continue
            elif is_tag(l):
                pass
            elif is_conll(l):
                fields = l.split('\t')
                current_text.append(fields[0])
            else:
                print('Failed to parse line {} in {}: {}'.format(ln, fn, l),
                      file=sys.stderr)
    return texts


def main(argv):
    args = argparser().parse_args(argv[1:])
    if args.fix_text and ftfy is None:
        print('--fix-text unavailable, try `pip3 install ftfy`',
              file=sys.stderr)
        return 1
    for fn in args.file:
        texts = read_texts(fn, args)
        texts.sort()
        for date, sec, text in texts:
            if args.include_date:
                print('{}\t__label__{} {}'.format(date, sec, text))
            else:
                print('__label__{} {}'.format(sec, text))                
    return 0

    
if __name__ == '__main__':
    sys.exit(main(sys.argv))
