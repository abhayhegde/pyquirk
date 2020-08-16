"""
A simple python program to convert quantum circuits to TeX code.

Acknowledgements: https://algassert.com/quirk
"""

import json

file = open("circuit.txt", "r")
data = json.load(file)
nrow = max([len(i) for i in data['cols']])

""" targ_pos = 0
if "•" in data['cols']:
    targ_pos = data['cols'].index("•") - data['cols'].index("X")
print(targ_pos) """

if data.get('init') == None:
    data['init'] = [0] * nrow
else:
    data['init'] += [0] * (nrow - len(data['init']))

for i in range(len(data['cols'])):
    data['cols'][i] += [1] * (nrow - len(data['cols'][i]))
data['rows'] = list(map(list, zip(*data.pop('cols'))))

quantikz_env = ["\\begin{quantikz}", "\end{quantikz}"]
initial_state = []

for state in range(len(data['init'])):
    initial_state.append(
        ''.join(["\lstick{\ket{", str(data['init'][state]), "}}"]))

subs = dict(zip([1, "X", "Y", "Z", "H", "•", "Measure"],
                ["\qw", "\gate{X}", "\gate{Y}", "\gate{Z}", "\gate{H}", "\ctrl{1}", "\meter{}"]))

comp = []
for i in range(nrow):
    a = [subs[ele] for ele in data['rows'][i]]
    comp.append(a)

code = open("code.tex", "w")
code.write(''.join([quantikz_env[0], "\n"]))
for i in range(nrow):
    if i == nrow - 1:
        code.write(''.join([initial_state[i], '&', ' & '.join(comp[i]), '\n']))
    else:
        code.write(
            ''.join([initial_state[i], '&', ' & '.join(comp[i]), '\\\\', '\n']))
code.write(''.join([quantikz_env[1]]))
code.close()
