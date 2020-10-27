#!/usr/bin/env python

import sys
from lxml import etree


def main(fpath, tag):
    parser = etree.XMLParser(recover=True)
    tree = etree.parse(fpath, parser=parser)
    for t in tree.iter(tag):
        try:
            if t.text:
                sys.stdout.write(t.text)
                sys.stdout.write('\n\n')
        except:
            sys.stderr.write('Something went wrong!\n')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
