#!/usr/bin/env python3
"""
pyquirk.py: A simple python program to convert quantum circuits to TeX code.
Written by Abhay Hegde.
"""

import sys
import argparse
import json
from urllib.parse import unquote

NUM_ROWS = 0

def get_parser():
    """Returns the parser argument for this script."""
    parser = argparse.ArgumentParser(description='Generates quantikz LateX codes from either URL or a text file. Options are explained below.')
    group = parser.add_mutually_exclusive_group()
    nextg = parser.add_mutually_exclusive_group()
    group.add_argument("-u", "--url", dest="url", nargs=1, type=str, 
                       help='Converts Quirk URL to circuit code.')
    group.add_argument('-i', '--input', dest="input", nargs=1, 
                       help='Converts input text file with circuit in JSON format to circuit code.')
    nextg.add_argument('-o', '--output', nargs=1, dest="output", 
                        help='Latex code with only quantikz environment is saved in output file.')
    nextg.add_argument('-m', '--main', nargs=1, 
                        help='A standalone LaTeX document containing the output circuit code.')
    return parser

def decode_url(URL):
    global args
    url = args.url
    decoded_url = unquote(url)
    return decoded_url

def json_from_URL(decoded_url):
    decoded_url = unquote(decoded_url)
    file = decoded_url[decoded_url.find("{"):]
    data = json.loads(file)
    return data

def json_from_text(text_file):
    tmp = open(text_file, "r")
    data = json.load(tmp)
    return data

def insert_vertical_qw(data):
    special = ["•", "◦"]
    subcol = []    

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
            vind = 0
            for gate in col:
                if any([x in str(gate) for x in lst]): vgates.append(0)
                else: vgates.append(vind)
                vind += 1
            cols = [str(x) for x in col]
            if "X" in nt_gates: col[col.index("X")] = "\\targ{}"
            vnon = [x for i, x in enumerate(vgates) if x != 0]
            for i in range(len(vnon)-1):
                vdiff = vgates.index(vnon[i+1]) - vgates.index(vnon[i])
                subcols[vgates.index(vnon[i])] = ''.join([" \\vqw{", str(vdiff), "}"])
        subcol.append(subcols)
        if "Swap" in col:
            pos = []
            for i in range(len(col)):
                if col[i] == "Swap": pos.append(i)
            sdiff = pos[1] - pos[0]
            col[pos[0]] = ''.join(["\\swap{", str(sdiff), "}"])
            col[pos[1]] = "\\targX{}"
        return data, subcol

def get_initial_states(data):
    global NUM_ROWS
    NUM_ROWS = max([len(i) for i in data['cols']])
    if data.get('init') == None:
        data['init'] = [0] * NUM_ROWS
    else:
        data['init'] += [0] * (NUM_ROWS - len(data['init']))
    return data

def convert_columns_to_rows(data):
    for i in range(len(data['cols'])):
        data['cols'][i] += [1] * (NUM_ROWS - len(data['cols'][i]))
    data['rows'] = list(map(list, zip(*data.pop('cols'))))
    return data

def vqw_append(subcol):
    vqw_ind = []
    for i in range(len(subcol)):
        for j in range(len(subcol[i])):
            if any([x in subcol[i][j] for x in "vqw"]):
                vqw_ind.append([j, i])
    return vqw_ind

def tex_initial_states(data):
    initial_state = []
    initial_state = [''.join(["\lstick{\ket{", str(data['init'][row]),"}}"]) for row in range(len(data['init']))]
    return data, initial_state

def substitute_gates(data, vqw_ind, subcol, initial_state):
    global NUM_ROWS
    comp = []
    commands = []
    rules = dict(zip([1, "X", "Y", "Z", "H", "U", "Measure", "Z^½", "Z^¼", "Z^-½","Z^-¼", "Y^½", "Y^¼", "Y^-½","X^-¼", "X^½", "X^¼", "X^-½","X^-¼", "…"],
                ["\qw", "\gate{X}", "\gate{Y}", "\gate{Z}", "\gate{H}", "\gate{U}", "\meter{}", "\\gate{S}", "\\gate{T}","\\gate{S^{-1}}", "\\gate{T^{-1}}", "\\gate{Y^{\\frac{1}{2}}}", "\\gate{Y^{\\frac{1}{4}}}","\\gate{Y^{-\\frac{1}{2}}}", "\\gate{Y^{-\\frac{1}{4}}}", "\\gate{X^{\\frac{1}{2}}}", "\\gate{X^{\\frac{1}{4}}}","\\gate{X^{-\\frac{1}{2}}}", "\\gate{X^{-\\frac{1}{4}}}", "\qw"]))

    ## substitutions
    for i in range(NUM_ROWS):
        # leave = ['ctrl', 'targ', 'gate']
        row = [rules[ele] if ele in rules else ele if "ctrl" in str(ele) else ele if "targ" in str(ele) else ele if "swap" in str(ele) else ''.join(["\gate{", ele, "}"]) for ele in data['rows'][i]]
        comp.append(row)

    for i, j in vqw_ind:
        comp[i][j] += subcol[j][i]

    for i in range(NUM_ROWS):
        if i == NUM_ROWS - 1:
            commands.append(''.join([initial_state[i], '&', ' & '.join(comp[i]), '& \qw', '\n']))
        else:
            commands.append(
                ''.join([initial_state[i], '&', ' & '.join(comp[i]), '& \qw ', '\\\\', '\n']))
    return commands

def replace_with_cw(commands):
    ## to replace with classical wires if meter is present
    met_index = [i.find('\\meter{}') for i in commands]
    if max(met_index) > -1:
        for i in range(len(met_index)):
            if met_index[i] > -1:
                old_str = commands[i][met_index[i]+len('\\meter{} &'):]
                new_str = old_str.replace("\qw", "\cw")
                commands[i] = commands[i][:len('\\meter{} &')+met_index[i]] + new_str
    return commands

def write_output_commands(commands, code_file):
    quantikz_file = open(code_file, "w")
    quantikz_file.write("\\begin{quantikz}\n")
    quantikz_file.write(''.join(commands))
    quantikz_file.write("\\end{quantikz}\n")
    quantikz_file.close()

def write_output_main(commands, main_file):
    latex_file = open(main_file, "w")
    latex_file.write("\\documentclass{article}\n\\usepackage{tikz}\n\\usetikzlibrary{quantikz}\n\\begin{document}\n\\begin{center}\n\\begin{quantikz}\n"
)
    latex_file.write(''.join(commands))
    latex_file.write("\\end{quantikz}\n\\end{center}\n\\end{document}")
    latex_file.close()

def convert_json_to_tex(data):
    vqw_data, subcol = insert_vertical_qw(data)
    states_init = get_initial_states(vqw_data)
    rows_formed = convert_columns_to_rows(states_init)
    vqw_indices = vqw_append(subcol)
    init_texed, initial_states = tex_initial_states(rows_formed)
    gates_sub = substitute_gates(init_texed, vqw_indices, subcol, initial_states)
    final_sub = replace_with_cw(gates_sub)
    return final_sub

def main():
    parser = get_parser()
    args = parser.parse_args()

    if args.input != None:
        text_file = args.input[0]
        data = json_from_text(text_file)

    if args.url != None:
        url_file = args.url[0]
        data = json_from_URL(url_file)
    
    final_sub = convert_json_to_tex(data)
    
    if args.output != None:
        write_output_commands(final_sub, args.output[0])
    
    if args.main != None:
        write_output_main(final_sub, args.main[0])

if __name__ == "__main__":
    main()
