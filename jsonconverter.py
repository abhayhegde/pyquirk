"""
A simple python program to convert quantum circuits to TeX code.

Acknowledgements: https://algassert.com/quirk
"""

import sys
import json

file = open(str(sys.argv[1]), "r")
data = json.load(file)
nrow = max([len(i) for i in data['cols']])

# if "•" in data['cols']:
#     targ_pos = data['cols'].index("•") - data['cols'].index("X")
# print(targ_pos)

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

subs = dict(zip([1, "X", "Y", "Z", "H", "U", "•", "Measure", "X1"],
                ["\qw", "\gate{X}", "\gate{Y}", "\gate{Z}", "\gate{H}", "\gate{U}", "\ctrl{1}", "\meter{}", "\targ{}"]))

comp = []
for i in range(nrow):
    a = [''.join(["\gate{", ele, "}"]) if ele not in subs else subs[ele] for ele in data['rows'][i]]
    comp.append(a)

main = []
for i in range(nrow):
    if i == nrow - 1:
        main.append(''.join([initial_state[i], '&', ' & '.join(comp[i]), '& \qw', '\n']))
    else:
        main.append(
            ''.join([initial_state[i], '&', ' & '.join(comp[i]), '& \qw ', '\\\\', '\n']))

met_index = [i.find('\\meter{}') for i in main]
if max(met_index) > -1:
    for i in range(len(met_index)):
        if met_index[i] > -1:
            old_str = main[i][met_index[i]+len('\\meter{} &'):]
            new_str = old_str.replace("\qw", "\cw")
            main[i] = main[i][:len('\\meter{} &')+met_index[i]] + new_str

code = open(sys.argv[2], "w")
preamble = "\\documentclass{article}\n\\usepackage{tikz}\n\\usetikzlibrary{quantikz}\n\\begin{document}\n\\begin{quantikz}\n"
end = "\\end{quantikz}\n\\end{document}"
code.write(preamble)
code.write(''.join(main))
code.write(end)
code.close()
