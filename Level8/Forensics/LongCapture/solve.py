# usage: tshark -r form.pcap -T fields -e frame.number -e tcp.srcport -e tcp.seq -e tcp.payload > all.tsv
#        python3 -I solve.py all.tsv   -> lists forms seen (account,code) with frame/port/seq, skipping the u* filler and c.mendes flood
import sys,collections
d=collections.defaultdict(list)
for l in open(sys.argv[1]):
    p=l.rstrip('\n').split('\t')
    if len(p)<4 or not p[3]: continue
    b=bytes.fromhex(p[3]).rstrip(b'P').decode()
    a,c=[x.split('=',1)[1] for x in b.split('\n')[:2]]
    d[(a,c)].append((int(p[0]),p[1],p[2]))
for k,v in d.items():
    if not k[0].startswith('u'): print(k,len(v),v[:2],v[-1])
