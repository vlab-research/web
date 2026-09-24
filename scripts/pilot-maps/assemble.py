# Assembles the review page: template + maps + agent country sections. Edit the template, not the output.
import re,os,glob
SP=os.path.dirname(os.path.abspath(__file__)); C=SP+'/countries'
t=open(SP+'/country-pilot.tpl.html').read()
for k,f in [("NG2023","nigeria-2023-states.svg"),("ID","indonesia.svg"),("BO","bolivia.svg")]:
    t=t.replace("{{"+k+"}}",open(SP+'/geo/out/'+f).read())
extra=[C+'/BD/section.html',C+'/PK/section.html',C+'/KE/section.html',C+'/US/section.html']+sorted(glob.glob(C+'/MENA/section-*.html'))
secs=[open(f).read() for f in extra if os.path.exists(f)]
t=t.replace('{{EXTRA_SECTIONS}}','\n'.join(secs))
for k,f in [('KE','countries/KE/kenya-places.svg')]:
    if os.path.exists(SP+'/'+f): t=t.replace('{{'+k+'}}',open(SP+'/'+f).read())
order=['nigeria','bangladesh','pakistan','indonesia','kenya','united-states','iraq','jordan','egypt','saudi-arabia','morocco','bolivia','rules']
names={'united-states':'United States','saudi-arabia':'Saudi Arabia'}
ids=re.findall(r'<section id="([^"]+)" role="tabpanel"',t)
ids=sorted(ids,key=lambda x: order.index(x) if x in order else 50)
t=t.replace('{{TABS}}',''.join(f'\n      <button role="tab" id="t-{i}" aria-controls="{i}">{names.get(i,i.capitalize())}</button>' for i in ids)+'\n    ')
# every panel starts hidden; the script shows the first
t=re.sub(r'(<section id="[^"]+" role="tabpanel"[^>]*?)( hidden)?>',r'\1 hidden>',t)
assert '{{' not in t, re.findall(r'\{\{\w+\}\}',t)
dup=[i for i in set(re.findall(r'id="([^"]+)"',t)) if t.count(f'id="{i}"')>1]
print('panels',ids,'dup ids',dup,'bytes',len(t))
open(SP+'/country-pilot.html','w').write(t)
