# -*- coding: utf-8 -*-
import sys, re, os
sys.stdout.reconfigure(encoding='utf-8')
files = ['README.md','docs/PLAN.md','docs/SPEC.md','docs/DECISIONS.md','docs/DIGEST.md']
bad = 0

# structural
for p in files:
    L = open(p, encoding='utf-8').read().split('\n')
    inf = False; prev = False; iss = []
    fences = sum(1 for l in L if l.strip().startswith('```'))
    if fences % 2: iss.append('unclosed fence (%d)' % fences)
    for i, l in enumerate(L, 1):
        if l.strip().startswith('```'): inf = not inf; prev = False; continue
        if inf: continue
        tab = l.strip().startswith('|')
        if prev and not tab and l.strip() and not l.startswith('#'):
            for j in range(i, min(i+3, len(L))):
                if L[j].strip().startswith('|'):
                    iss.append('L%d splits a table: %s' % (i, l.strip()[:40])); break
        prev = tab
    # table column consistency
    run = []
    inf = False
    for i, l in enumerate(L, 1):
        if l.strip().startswith('```'): inf = not inf; continue
        if inf: continue
        if l.strip().startswith('|'): run.append((i, l.count('|') - l.count('\|')))
        else:
            if len(run) >= 2:
                widths = set(w for _, w in run)
                if len(widths) > 1: iss.append('L%d-%d ragged table cols %s' % (run[0][0], run[-1][0], sorted(widths)))
            run = []
    print(('%-22s' % p), iss if iss else 'OK')
    bad += len(iss)

# cross references
spec = open('docs/SPEC.md', encoding='utf-8').read()
dec = open('docs/DECISIONS.md', encoding='utf-8').read()
plan = open('docs/PLAN.md', encoding='utf-8').read()
spec_secs = set(re.findall(r'^#{2,3} (\d+(?:\.\d+)?)[ .]', spec, re.M))
dec_ids = set(re.findall(r'^### ([DX]\d+)\.', dec, re.M))
plan_secs = set(re.findall(r'^#{2,3} (\d+(?:\.\d+)?)[ .]', plan, re.M))
plan_rq = set(re.findall(r'\| (RQ\d) \|', plan))
plan_ms = set(re.findall(r'\| (M\d) \|', plan))

print('\nSPEC sections:', len(spec_secs), '| DECISIONS ids:', len(dec_ids), '| PLAN secs:', len(plan_secs))
for p in files:
    t = open(p, encoding='utf-8').read()
    miss = []
    for r in set(re.findall(r'SPEC[ .]?(\d+\.\d+|\d+)(?:절)?', t)):
        if r not in spec_secs: miss.append('SPEC ' + r)
    for r in set(re.findall(r'\b([DX]\d+)\b', t)):
        if r not in dec_ids: miss.append(r)
    for r in set(re.findall(r'\b(RQ\d)\b', t)):
        if r not in plan_rq: miss.append(r)
    for r in set(re.findall(r'\b(M\d)\b', t)):
        if r not in plan_ms: miss.append(r)
    print(('%-22s' % p), 'dangling:', sorted(miss) if miss else 0)
    bad += len(miss)
print('\nTOTAL ISSUES:', bad)
