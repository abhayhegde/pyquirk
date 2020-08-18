"""
A simple python program to convert quantum circuits to TeX code.

Acknowledgements: https://algassert.com/quirk
"""

import sys
import json

file = open(str(sys.argv[1]), "r")
data = json.load(file)
nrow = max([len(i) for i in data['cols']])
special = ["•", "◦"]
subcol = []    
vqw_ind = []
comp = []
main = []

for col in data['cols']:
    subcols = [''] * len(col)
    if any(s in col for s in special):
        inds1 = [i for i, x in enumerate(col) if x == "•"] 
        inds2 = [i for i, x in enumerate(col) if x == "◦"] 
        if len(inds1) == 0: ctrl_ind = inds2[0]
        elif len(inds2) == 0: ctrl_ind = inds1[0]
        else: ctrl_ind = min([inds1[0], inds2[0]]) 
        nt_gates = [gate for gate in col if gate not in special and gate != 1]
        targ_ind = col.index(nt_gates[0])
        diff = targ_ind - ctrl_ind
        for i in inds1: col[i] = "\\ctrl{}"
        for i in inds2: col[i] = "\\octrl{}"
        if col[ctrl_ind] == "\\octrl{}":
           col[ctrl_ind] = ''.join(["\\octrl{", str(diff), "}"])
        else:
           col[ctrl_ind] = ''.join(["\\ctrl{", str(diff), "}"])
        vgates = []
        lst = ['ctrl', "1"]
        for gate in col:
            if any([x in str(gate) for x in lst]): pass
            else: vgates.append(gate)
        cols = [str(x) for x in col]
        if "X" in nt_gates: col[col.index("X")] = "\\targ{}"
        for i in range(len(vgates) - 1):
            vdiff = cols.index(vgates[i+1]) - cols.index(vgates[i])
            subcols[i+1] = ''.join([" \\vqw {", str(vdiff), "}"])
    subcol.append(subcols)
    if "Swap" in col:
        pos = []
        for i in range(len(col)):
            if col[i] == "Swap": pos.append(i)
        sdiff = pos[1] - pos[0]
        col[pos[0]] = ''.join(["\\swap{", str(sdiff), "}"])
        col[pos[1]] = "\\targX{}"

if data.get('init') == None:
    data['init'] = [0] * nrow
else:
    data['init'] += [0] * (nrow - len(data['init']))

for i in range(len(data['cols'])):
    data['cols'][i] += [1] * (nrow - len(data['cols'][i]))
data['rows'] = list(map(list, zip(*data.pop('cols'))))

initial_state = []
for state in range(len(data['init'])):
    initial_state.append(
        ''.join(["\lstick{\ket{", str(data['init'][state]), "}}"]))

subs = dict(zip([1, "X", "Y", "Z", "H", "U", "Measure", "Z^½", "Z^¼", "Z^-½","Z^-¼", "Y^½", "Y^¼", "Y^-½","X^-¼", "X^½", "X^¼", "X^-½","X^-¼", "…"],
                ["\qw", "\gate{X}", "\gate{Y}", "\gate{Z}", "\gate{H}", "\gate{U}", "\meter{}", "\\gate{S}", "\\gate{T}","\\gate{S^{-1}}", "\\gate{T^{-1}}", "\\gate{Y^{\\frac{1}{2}}}", "\\gate{Y^{\\frac{1}{4}}}","\\gate{Y^{-\\frac{1}{2}}}", "\\gate{Y^{-\\frac{1}{4}}}", "\\gate{X^{\\frac{1}{2}}}", "\\gate{X^{\\frac{1}{4}}}","\\gate{X^{-\\frac{1}{2}}}", "\\gate{X^{-\\frac{1}{4}}}", "\qw"]))

for i in range(len(subcol)):
    for j in range(len(subcol[i])):
        if any([x in subcol[i][j] for x in "vqw"]):
            vqw_ind.append([j, i])

## substitutions
for i in range(nrow):
    # row = [''.join(["\gate{", ele, "}"]) if ele not in subs else subs[ele] for ele in data['rows'][i]]
    # leave = ['ctrl', 'targ', 'gate']
    row = [subs[ele] if ele in subs else ele if "ctrl" in str(ele) else ele if "targ" in str(ele) else ele if "swap" in str(ele) else ''.join(["\gate{", ele, "}"]) for ele in data['rows'][i]]
    comp.append(row)

for i, j in vqw_ind:
    comp[i][j] += subcol[j][i]

for i in range(nrow):
    if i == nrow - 1:
        main.append(''.join([initial_state[i], '&', ' & '.join(comp[i]), '& \qw', '\n']))
    else:
        main.append(
            ''.join([initial_state[i], '&', ' & '.join(comp[i]), '& \qw ', '\\\\', '\n']))

## to replace with classical wires if meter is present
met_index = [i.find('\\meter{}') for i in main]
if max(met_index) > -1:
    for i in range(len(met_index)):
        if met_index[i] > -1:
            old_str = main[i][met_index[i]+len('\\meter{} &'):]
            new_str = old_str.replace("\qw", "\cw")
            main[i] = main[i][:len('\\meter{} &')+met_index[i]] + new_str

code = open(sys.argv[2], "w")
#preamble = "\\documentclass{article}\n\\usepackage{tikz}\n\\usetikzlibrary{quantikz}\n\\begin{document}\n\\begin{center}\n\\begin{quantikz}\n"
#end = "\\end{quantikz}\n\\end{center}\n\\end{document}"
begin = "\\begin{quantikz}\n"
end = "\\end{quantikz}\n"
code.write(begin)
code.write(''.join(main))
code.write(end)
code.close()