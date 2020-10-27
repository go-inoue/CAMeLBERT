#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from six import unichr

from camel_tools.utils.normalize import normalize_unicode
from camel_tools.utils.dediac import dediac_ar


def _normalize_text(text):
    normalized = normalize_unicode(text)
    # De-diacritization
    normalized = dediac_ar(normalized)
    # Remove kashida
    normalized = normalized.replace(u'\u0640', '')
    return normalized


def main():
    try:
        with open(sys.argv[1], mode='r', encoding='utf-8') as f:
            for line in f.readlines():
                sys.stdout.write(_normalize_text(line).strip() + '\n')

    except Exception:
        sys.stderr.write('Error: An unknown error occurred.\n')
        sys.exit(1)


if __name__ == '__main__':
    main()
