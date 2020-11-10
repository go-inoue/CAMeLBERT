#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys

from filter_non_arabic_text import _filter_non_arabic_text
from clean_text import _clean_text
from normalize_text import _normalize_text


def main():
    with open(sys.argv[1], mode='r', encoding='utf-8') as f:
        for line in f.readlines():
            if line == '\n':
                sys.stdout.write('\n')
            else:
                cleaned = _clean_text(line)
                filtered = _filter_non_arabic_text(cleaned)
                if filtered is not None:
                    normalized = _normalize_text(filtered)
                    if normalized:
                        sys.stdout.write(normalized + '\n')
                else:
                    sys.stderr.write('This line was filtered.\n')


if __name__ == '__main__':
    main()
