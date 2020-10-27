#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re

from camel_tools.utils.charsets import AR_CHARSET


AR_CHARSET_RE = re.compile(u'[' + u''.join(AR_CHARSET) + u']')


def _filter_non_arabic_text(text):
    # if the line contains at least one Arabic letter or it's an empty line
    if re.search(AR_CHARSET_RE, text) or len(text.strip()) == 0:
        return text.strip()
    else:
        sys.stderr.write('No Arabic letter in "{}"\n'.format(text))
        return None


def main():
    with open(sys.argv[1], mode='r', encoding='utf-8') as f:
        for line in f.readlines():
            if _filter_non_arabic_text(line) is not None:
                sys.stdout.write(_filter_non_arabic_text(line) + '\n')
            else:
                sys.stderr.write('This line was flitered.\n')


if __name__ == '__main__':
    main()
