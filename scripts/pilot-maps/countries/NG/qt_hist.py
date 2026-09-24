import csv,json,collections,sys
csv.field_size_limit(10**9)
m={l.split()[0]:l.split()[1] for l in open('countries/NG/cands.txt')}
H=collections.defaultdict(list)
for r in csv.DictReader(open('countries/NG/cand_confs.tsv'),delimiter='\t'):
    H[(r['study_id'],r['conf_type'])].append((r['created'],json.loads(r['conf'])))
def ne(q):
    if not q: return 'NONE'
    out=[]
    def walk(x):
        if x.get('op') in ('and','or'):
            for v in x['vars']: walk(v)
        elif x.get('op')=='equal': out.append('eq:'+str(x['vars'][0].get('value')))
        else: out.append(x['op']+':'+','.join(str(v.get('value')) for v in x['vars']))
    walk(q); return ' & '.join(sorted(set(out)))
for sid,slug in m.items():
    ds=H.get((sid,'data_sources'),[])
    names=[x.get('config',{}).get('survey_name') or x.get('source') for x in ds[-1][1]] if ds else []
    rec=H.get((sid,'recruitment'),[]); r=rec[-1][1] if rec else {}
    qts=[]
    for c,conf in H.get((sid,'strata'),[]):
        q=sorted(set(ne(s.get('question_targeting')) for s in conf))
        if not qts or qts[-1][1]!=q: qts.append((c[:16],q))
    print('##',slug,'| dest',r.get('destination_type'),'| inc',r.get('incentive_per_respondent'),'| max',r.get('max_sample'),'|',str(r.get('start_date'))[:10],str(r.get('end_date'))[:10],'| survey',names)
    for c,q in qts: print('   QT',c,q)
