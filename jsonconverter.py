"""
A simple python program to convert quantum circuits to TeX code.

Acknowledgements: https://algassert.com/quirk
"""

import json

file = open("circuit.txt", "r")
data = json.load(file)
nrow = max([len(i) for i in data['cols']])

if data.get('init') == None:
    data['init'] = [0] * nrow
else:
    data['init'] += [0] * (nrow - len(data['init']))

for i in range(nrow):
    data['cols'][i] += [1] * (nrow - len(data['cols'][i]))

data['rows'] = list(map(list, zip(*data.pop('cols'))))
print(data)

quantikz_env = ["\\begin{quantikz}", "\end{quantikz}"]
initial_state = []

for state in range(len(data['init'])):
    initial_state.append(
        ''.join(["\lstick{\ket{", str(data['init'][state]), "}}"]))

subs = dict(zip(["X", "Y", "Z", "H", 1],
                ["\gate{X}", "\gate{Y}", "\gate{Z}", "\gate{H}", "\qw"]))

comp = []
for i in range(nrow):
    a = [subs[ele] for ele in data['rows'][i]]
    comp.append(a)

code = open("code.txt", "w")
code.write(''.join([quantikz_env[0], "\n"]))
for i in range(nrow):
    code.write(
        ''.join([initial_state[i], '&', ' & '.join(comp[i]), '\\', '\n']))
code.write(''.join([quantikz_env[1], "\n"]))
code.close()
