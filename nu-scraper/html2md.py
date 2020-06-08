#!/usr/bin/env python
# -*- coding: utf-8 -*- 

from bs4 import BeautifulSoup
import sys, re

def html2md(text_html, **kargs):
    link_ref = kargs.get('refer', None)
    link_desc = kargs.get('desc', 'Link')
    soup_features = kargs.pop('features', 'lxml')
    soup_html = BeautifulSoup(text_html, features=soup_features)
    # kill all script and style elements
    for x in soup_html.find_all("div", {'class': 'sharedaddy'}):
        x.decompose() # broke merc
    for x in soup_html.find_all("div", {'id': 'jp-post-flair'}):
        x.decompose()
    for soup_script in soup_html(["ins", "script", "style"]):
        soup_script.decompose() # rip it out
    # soup_text = soup_html.get_text()
    # soup_text = re.sub('(\t|\s+)?\n+', '\n', soup_html.get_text(), re.MULTILINE) # WTF no break!?
    soup_text = re.sub('\n\s*\n', '\n', soup_html.get_text())
    # decompose broke mercenary wordads c131
    soup_text = soup_text.replace('\n', '<br/>\n')
    if link_ref is not None:
        return '[{desc}]({refer})\n<br/>{md}'.format(
            desc = link_desc, 
            refer = link_ref, 
            md = soup_text
        )
    else:
        return soup_text

if __name__ == '__main__':
    for line in sys.stdin:
        fname = line.rsplit('.', 1)[0]
        with open(line.strip('\n'), 'r') as fread:
            text_content = html2md(fread.read())
            with open(fname + '.md', 'w') as mdwn:
                mdwn.write(text_content)
else:
    pass

# sed -i '/^$/d; s/\.$/\.<br\/>/g; s/"$/"<br\/>/g; s/”$/"<br\/>/g; s/“/"/g; s/】$/"<br\/>/g; s/【/"/g; s/』$/"<br\/>/g; s/『/"/g' *.md
