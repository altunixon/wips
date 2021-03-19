with open('/tmp/rit_merged.txt', 'r') as rf:
    rlines=[x.strip('\n') for x in rf.readlines() if '|' in x and not x.startswith('#')]

nlines = []
for z in rlines:
    w=z.split('|')
    old = w[0]
    print ('OLD Dir: "%s"' % old)
    news = w[1:]
    if len(news) == 1:
        mvline = ("mv -v --noclobber '{old}' '{new}' && ls -A '_empty/{new}' && echo 'Not Empty _empty/{new}' || rm -v -rf '_empty/{new}'".format(old=old, new=news[0]))
    else:
        for n, i in enumerate(news):
            print ('[%s]: "%s"' % (n, i))
        selection=int(input("Select One: ") or 0)
        mvline = ("mv -v --noclobber '{old}' '{new}' && ls -A '_empty/{new}' && echo 'Not Empty _empty/{new}' || rm -v -rf '_empty/{new}'".format(old=old, new=news[selection]))
    nlines.append(mvline)

with open('/tmp/rit_mv.txt', 'w+') as wf:
    wf.write('\n'.join(nlines))
