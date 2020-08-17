"""
A simple python program to convert quantum circuits to TeX code.

Acknowledgements: https://algassert.com/quirk
"""

import sys
import json

file = open(str(sys.argv[1]), "r")
data = json.load(file)
nrow = max([len(i) for i in data['cols']])

for col in data['cols']:
    if "•" in col:
        nt_gates = [gate for gate in col if gate != 1]
        ctrl_index = col.index("•")
        targ_index = col.index(next(gate for gate in nt_gates if gate != "•"))
        diff = targ_index - ctrl_index
        col[ctrl_index] = ''.join(["\\ctrl{", str(diff), "}"])
        if "X" in nt_gates: col[col.index("X")] = "\\targ{}" 
    #     for i in range(2, len(nt_gates)):
    #         vdiff = col.index(nt_gates[i]) - col.index(nt_gates[i-1])
    #         col[i] += ''.join([" \\vqw{", str(vdiff), "}"])
    # if "X" in col: str.replace("X", "\\targ{}")
    
    if "◦" in col:
        octrl_ind = col.index("◦")
        nt_gate = next((gate for gate in col if gate not in ["◦", 1]), None)
        targ_ind = col.index(nt_gate)
        if nt_gate == "X": col[col.index(nt_gate)] = "\\targ{}"
        odiff = targ_ind - octrl_ind
        col[octrl_ind] = ''.join(["\\octrl{",str(odiff),"}"])

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

comp = []
main = []
## substitutions
for i in range(nrow):
    # row = [''.join(["\gate{", ele, "}"]) if ele not in subs else subs[ele] for ele in data['rows'][i]]
    row = [subs[ele] if ele in subs else ele if "ctrl" in str(ele) else ele if "targ" in str(ele) else ele if "swap" in str(ele) else ''.join(["\gate{", ele, "}"]) for ele in data['rows'][i]]
    comp.append(row)
    if i == nrow - 1:
        main.append(''.join([initial_state[i], '&', ' & '.join(comp[i]), '& \qw', '\n']))
    else:
        main.append(
            ''.join([initial_state[i], '&', ' & '.join(comp[i]), '& \qw ', '\\\\', '\n']))
            
## to replace with classical wires if meter is there
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
