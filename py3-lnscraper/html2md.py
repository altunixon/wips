#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from bs4 import BeautifulSoup as Soup
import sys, re

for line in sys.stdin:
    fname = line.rsplit('.', 1)[0]
    with open(line.strip('\n'), 'r') as fread:
        text_content = Soup(fread.read()).getText().replace('\n', '<br/>\n')
        text_md = re.sub('[“”【】『』]', '"', text_content)
        with open(fname + '.md', 'w') as mdwn:
            mdwn.write(text_md)

# sed -i '/^$/d; s/\.$/\.<br\/>/g; s/"$/"<br\/>/g; s/”$/"<br\/>/g; s/“/"/g; s/】$/"<br\/>/g; s/【/"/g; s/』$/"<br\/>/g; s/『/"/g' *.md