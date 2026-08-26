def lum(h):
    h=h.lstrip("#"); c=[int(h[i:i+2],16)/255 for i in (0,2,4)]
    l=[x/12.92 if x<=0.03928 else ((x+0.055)/1.055)**2.4 for x in c]
    return 0.2126*l[0]+0.7152*l[1]+0.0722*l[2]
def r(a,b):
    la,lb=lum(a),lum(b); return (max(la,lb)+0.05)/(min(la,lb)+0.05)
PAPER_L="#F1F4F5"; PAPER_D="#13181C"; SURF="#FFFFFF"; INV_L="#1F272E"; INV_D="#0C1013"
DATA_L="#1D5F6E"; DATA_D="#4E9DB0"; BRASS_L="#7A5C1E"
cands={
 "moss (light)":"#3F6B4A","moss (dark lift)":"#79B489",
 "slate-violet (light)":"#5A4E7A","slate-violet (dark lift)":"#A093C4",
 "clay (light)":"#8A4B3C","clay (dark lift)":"#D0917F",
}
for n,h in cands.items():
    print(f"{n:26s} {h}  on paper-L {r(h,PAPER_L):5.2f}  on paper-D {r(h,PAPER_D):5.2f}  on surface {r(h,SURF):5.2f}  on inv-L {r(h,INV_L):5.2f}  on inv-D {r(h,INV_D):5.2f}")
print()
print(f"how far is each from --data? (luminance ratio vs data, greyscale confusability)")
for n,h in cands.items():
    print(f"{n:26s} vs data-L {r(h,DATA_L):5.2f}   vs brass-L {r(h,BRASS_L):5.2f}")
