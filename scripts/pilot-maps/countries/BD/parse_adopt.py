import csv,json,sys
csv.field_size_limit(10**9)
r=list(csv.reader(open(sys.argv[1]),delimiter='\t'))[1]
d=json.loads(r[2]); print('report',r[0])
S=P=0
for k in sorted(d):
    v=d[k]; S+=v['lifetime_spent']; P+=v['current_participants']
    print(f"{k:50s} {v['current_participants']:6d} {v['lifetime_spent']:9.2f} {v['lifetime_spent']/max(v['current_participants'],1):7.2f}  marg {v['current_price_per_participant']}")
print('TOTAL',P,round(S,2),round(S/P,2))
