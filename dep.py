with open("c.dep.da") as da, open("c.dep.sv") as sv, open("model/aligned.srctotgt") as align:
    da = reconstruct(da.read().split("\n"))
    sv = reconstruct(sv.read().split("\n"))
    al = align.read().split("\n")[:1000]

def reconstruct(blokk):
    out, curr = [], []
    for line in blokk:
        if line == '':
            out.append(curr)
            curr = []
        elif line[0] == '#':
            continue
        else:
            cols = line.split("\t")
            # 1 -> form, 5 -> feats
            curr.append((cols[1], cols[5]))

    return out

out = []
for n, (d, s, l) in enumerate(zip(da, sv, al)):
    if l == "":
        continue
    rels = l.split(" ")
    m = map(lambda x: (int(x.split("-")[0]), int(x.split("-")[1])), rels)
    for pair in m:
        out.append((d[pair[0]], s[pair[1]]))

def from_dict(f1, f2, unmatched):
    out = []
    keys = set(f1.keys()).union(f2.keys())
    for key in keys:
        try:
            if not unmatched:
                string = "{}:{}:{}".format(key, f1[key], f2[key])
            else:
                if f1[key] == f2[key]:
                    continue
                else:
                    string = "{}:{}:{}".format(key, f1[key], f2[key])
        except:
            if key not in f1.keys():
                string = "{}:{}:{}".format(key, '_', f2[key])
            else:
                string = "{}:{}:{}".format(key, f1[key], '_')
        out.append(string)
    return out

# i/p: morph feature strings; unmatched = return only non-matching
# o/p: {'feat_key': ('f1_val', 'f2_val')}
def pair_feats(pairs, unmatched=False):
    out = []
    for l1, l2 in pairs:
        w1, w2, f1, f2 = l1[0], l2[0], l1[1], l2[1]
        # dicts are easier to query
        if f1 == '_':
            f1 = {}
        else:
            f1 = {k: v for k, v in [eqn.split("=") for eqn in f1.split("|")]}
        if f2 == '_':
            f2 = {}
        else:
            f2 = {k: v for k, v in [eqn.split("=") for eqn in f2.split("|")]}

        out.extend(from_dict(f1, f2, unmatched))
        '''
        keys = set(f1.keys()).union(f2.keys())
        for key in keys:
            try:
                out[key] = (f1[key], f2[key])
            except:
                if key not in f1.keys():
                    out[key] = ('_', f2[key])
                else:
                    out[key] = (f1[key], '_')
        '''

    return out

with open("/home/vinit/corpora/da-sv/dump", "w") as f:
    for line in pair_feats(out, True):
        f.write(line + "\n")
