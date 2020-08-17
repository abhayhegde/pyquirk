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
        ctrl_ind = col.index("•")
        nt_gate = next((gate for gate in col if gate not in ["•", 1]), None)
        targ_ind = col.index(nt_gate)
        if nt_gate == "X": col[col.index(nt_gate)] = "X1"
        diff = targ_ind - ctrl_ind
        col[ctrl_ind] = ''.join(["\\ctrl{",str(diff),"}"])
        # all_gates = [gate for gate in col if gate != 1]
        # all_gates = ["X1" if x=="X" else x for x in all_gates]
        # if len(all_gates) > 1:
        #     for i in range(1, len(all_gates)):
        #         vindex = col.index(all_gates[i]) - col.index(all_gates[i-1])
        #         print(vindex)
    
    if "◦" in col:
        octrl_ind = col.index("◦")
        nt_gate = next((gate for gate in col if gate not in ["◦", 1]), None)
        targ_ind = col.index(nt_gate)
        if nt_gate == "X": col[col.index(nt_gate)] = "X1"
        odiff = targ_ind - octrl_ind
        col[octrl_ind] = ''.join(["\\octrl{",str(odiff),"}"])


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

subs = dict(zip([1, "X", "Y", "Z", "H", "U", "Measure", "X1"],
                ["\qw", "\gate{X}", "\gate{Y}", "\gate{Z}", "\gate{H}", "\gate{U}", "\meter{}", "\\targ{}"]))

comp = []
main = []

## substitutions
for i in range(nrow):
    # row = [''.join(["\gate{", ele, "}"]) if ele not in subs else subs[ele] for ele in data['rows'][i]]
    row = [subs[ele] if ele in subs else ele if "ctrl" in str(ele) else ''.join(["\gate{", ele, "}"]) for ele in data['rows'][i]]
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
