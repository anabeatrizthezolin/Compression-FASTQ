import sys, time, argparse, subprocess, os.path, pathlib, shutil
import matplotlib.pyplot as plt
import numpy as np

file_exe = "main.py"
cmdreorder = "reorder.py"
cmdcreate = "Criar_arquivos.py"
compress = []
times = []
rate = []
legend = []
file_datas = []

def main():
    parser = argparse.ArgumentParser(description="", formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument("input",                help="input file name", type=str, nargs="+")
    parser.add_argument("-n",                   help="not execute main.py", action="store_true", default = False)
    parser.add_argument('--7z',                 help='compression 7 zip: compression of the file with 7 zip', action='store_true', default = False)
    parser.add_argument('--bsc',                help='compression bsc: compression of the file with bsc', action='store_true', default = False)
    parser.add_argument('-c', '--compression',  help='compression 1(total), 2(in partitions), 3(in 3-components + partition) or 4(all)', default=False, type=int)
    parser.add_argument('-r', '--reorder',      help='reorder option: 1(lexicographic order), 2(colexicographic order), 3(random order) or 4(all)', default=False, type=int)
    parser.add_argument('-p', '--part',         help='size of the part for file division in MB', default=False, type=int)
    parser.add_argument('--rate',               help='compression rate: plot the rates in a bar graphic', action='store_true', default = False)
    parser.add_argument('-v',                   help='verbose: extra info in the log file',action='store_true')
    args = parser.parse_args()

    path_inp = os.path.split(sys.argv[1])[0]
    inp = os.path.splitext(sys.argv[1])[0]

    if(args.bsc): #if the compression is with bsc
        op_comp = 0
        comp = "bsc"
    else: #if the compression is with 7zip
        op_comp = 1
        comp = "zip"

    if(args.compression): # Compression option
        op = args.compression

    if(args.part): # Part size
        part = args.part*(2**20)
        P = args.part
    else:
        part = 10*(2**20)
        P = 10
    
    if(args.reorder): # Reordering option
        op_reorder = int(args.reorder)
        if(op_reorder == 4):
            i = 0
            while i <= 3:
                if(i == 0):
                    r = ""
                elif(i == 1):
                    r = "_lex"
                elif(i == 2):
                    r = "_colex"
                else:
                    r = "_random"
                
                create_file(sys.argv[1], inp, i, r)
                init(inp+r, op_comp, i, op, part, args, comp, P)
                i = i+1

        elif(op_reorder > 0 and op_reorder < 4):
            if(op_reorder == 1):
                r = "_lex"
                r_name = "lex"
            elif(op_reorder == 2):
                r = "_colex"
                r_name = "colex"
            else:
                r = "_random"
                r_name = "random"
            create_file(sys.argv[1], inp, op_reorder, r)
            init(inp+r, op_comp, op_reorder, op, part, args, comp, P)

        else:
            r = ""
            r_name = ""
            create_file(sys.argv[1], inp, op_reorder, r)
            init(inp+r, op_comp, op_reorder, op, part, args, comp, P)

    else:
       op_reorder = -1 
    
    if(args.rate):
        rat = 1
    else:
        rat = 0
    
    file_data = list(dict.fromkeys(file_datas)) # Remove repeated elements
    legends = list(dict.fromkeys(legend)) # Remove repeated elements
    i = 0
    aux = 0
    rate_orig = []
    rate_lex = []
    rate_colex = []
    rate_random = []

    j = 0
    while i < len(file_data):
        c, t, r = vectors_plot(file_data[i])
        compress.append(c)
        times.append(t)
        if(rat == 1):
            if(aux < 3):
                rate_orig.append(r[-1]) # Last data
            elif(aux < 6):
                rate_lex.append(r[-1]) # Last data
            elif(aux < 9):
                rate_colex.append(r[-1]) # Last data
            else:
                rate_random.append(r[-1]) # Last data
        aux = aux+1
        i = i+1
    graphic_lines(inp, legends, comp, rate_orig, rate_lex, rate_colex, rate_random, rat)

##########################################################################################################
### Function that calls all parts ###
def init(inp, op_comp, op_reorder, op, part, args, comp, P):
    MB = 25
    arquivos = []
    i = 25
    k = os.path.getsize(sys.argv[1])/(1000000)
    while(i < k):
        arquivos.append(str(i))  
        i += 25
    if(args.n == False):
        for item in arquivos:
            file_input = inp + "_" + item + "MB.fastq"
            execute_main(file_input, op_comp, op_reorder, op, P, inp)
            print("Executado: {}MB".format(item))

    execute_main(inp+".fastq", op_comp, op_reorder, op, P, inp)
    print("Executado: {}MB".format("300"))

##########################################################################################################

def vectors_plot(file_data):

    compres = []
    time = []
    rate = []
    for line in open(file_data,"r"):
        lines = [i for i in line.split()]
        compres.append(float(lines[0]))
        time.append(float(lines[1]))
        rate.append(float(lines[2]))

    return compres, time, rate

##########################################################################################################
### Functions of plot ###

def graphic_lines(inp, legend, comp, rate_orig, rate_lex, rate_colex, rate_random, rat):

    size = []
    i = 25
    k = os.path.getsize(sys.argv[1])/(1000000)
    while(i < k):
        size.append(i)  
        i += 25
    size.append(i)
    
    color = ["royalblue", "deeppink", "goldenrod", "plum", "mediumseagreen", "salmon", "mediumturquoise", "crimson", "darkviolet", "limegreen", "sienna", "red", "darkstateblue", "darkgreen", "gold"]
    
    ###### Plot compression and time ######
    plt.rcParams['xtick.labelsize'] = 17
    plt.rcParams['ytick.labelsize'] = 17
    plt.figure(figsize = (35,23), facecolor = None)
    plt.figure(1)
    plt.ylim(0,0.4)
    plt.ylabel("Compression", fontsize = 21)
    plt.xlabel("Size (MB)", fontsize = 21)

    i = 0
    while(i < len(compress)):
        plt.plot(size, compress[i], marker = "o", c = color[i], lw=1)
        i = i+1

    plt.title("Compression " + comp, fontsize = 30)
    plt.legend(legend, fontsize=17)
    plt.savefig(inp + "_compression_" + comp + ".png")

    plt.rcParams['xtick.labelsize'] = 17
    plt.rcParams['ytick.labelsize'] = 17
    plt.figure(figsize = (35,23), facecolor = None)
    plt.figure(2)
    plt.ylabel("Time (s)", fontsize = 21)
    plt.xlabel("Size (MB)", fontsize = 21)

    i = 0
    while(i < len(times)):
        plt.plot(size, times[i], marker = "o", c = color[i], lw=1)
        i = i+1
    plt.title("Compression time " + comp, fontsize = 30)
    plt.legend(legend, fontsize=17)
    plt.savefig(inp + "_compression_time_"+ comp + ".png")

    if(rat == 1):
        rate_lex[0] = 0
        rate_colex[0] = 0
        rate_random[0] = 0
        bW = 0.13
        b1 = [bW*2, 1-bW, 2-bW]
        b2 = [bW*2,1, 2]
        b3 = [bW*2,1+bW, 2+bW]
        b4 = [bW*2, 1+2*bW, 2+2*bW]
        position = [bW*2, 1+0.5*bW, 2+bW/2]
        plt.rcParams['xtick.labelsize'] = 17
        plt.rcParams['ytick.labelsize'] = 17
        plt.xlim(0,5)
        plt.figure(figsize = (35,23), facecolor = None)
        plt.figure(3)
        plt.ylabel("Compression", fontsize = 21)
        plt.title("Compression by types " + comp, fontsize = 30)
        plt.bar(b1, rate_orig, label = "Original", color = "royalblue", width=bW)
        plt.text(position[0]-bW/4, rate_orig[0], str(rate_orig[0]), rotation='horizontal', color = 'darkgrey')
        plt.bar(b2, rate_lex, label = "Lex", color = "deeppink", width=bW)
        plt.text(position[1]-bW*1.75, rate_orig[1], str(rate_orig[1]), rotation='horizontal', color = 'darkgrey')
        plt.bar(b3, rate_colex, label = "Colex", color = "seagreen", width=bW)
        plt.text(position[2]-bW*1.75, rate_orig[2], str(rate_orig[2]), rotation='horizontal', color = 'darkgrey')
        plt.bar(b4, rate_random, label = "Random", color = "plum", width=bW)
        plt.axhline(y = rate_orig[0], ls='--', lw=1, color = 'darkgrey')  
        plt.xticks(position, ["Original", "In partitions", "In 3-components + partitions"])
        plt.legend()

    plt.show()

##########################################################################################################
### Function that generates the options ###

def execute_main(file_input, op_comp, op_reorder, op, P, inp): 
    
    if(op_comp == 0):
        cmd_comp = '--bsc'
    elif(op_comp == 1):
        cmd_comp = '--7z'
    
    if(op_reorder == 4):
        i = 0
        while i <= 3:

            if(i == 0):
                r = ""
                op_r = ""
                r_name = ""
            elif(i == 1):
                r = "_lex"
                r_name = "lex"
            elif(i == 2):
                r = "_colex"
                r_name = "colex"
            else:
                r = "_random"
                r_name = "random"
            r_cmd = "-r " + str(i)
            command_op(file_input, op_comp, i, op, P, inp, r, cmd_comp, r_name, r_cmd)
            i = i+1

    elif(op_reorder > 0 and op_reorder < 4):
        if(op_reorder == 1):
            r = "_lex"
            r_name = "lex"
        elif(op_reorder == 2):
            r = "_colex"
            r_name = "colex"
        else:
            r = "_random"
            r_name = "random"
        r_cmd = "-r " + str(op_reorder)
        command_op(file_input, op_comp, op_reorder, op, P, inp, r, cmd_comp, r_name, r_cmd)

    else:
        r = ""
        r_name = ""
        r_cmd = ""
        command_op(file_input, op_comp, op_reorder, op, P, inp, r, cmd_comp, r_name, r_cmd)

##########################################################################################################
### Function that generates the commands ###
def command_op(file_input, op_comp, op_reorder, op, P, inp, r, cmd_comp, r_name, r_cmd):

    if(op == 4 or op == 1):
        command = "python3 {exe} {input} -1 {cmd_comp} -t {original}".format(exe=file_exe, input=file_input, cmd_comp=cmd_comp, original=inp)
        execute_command(command)
        file_datas.append(inp + "_1_data.txt")
        legend.append("Original " + r_name)
        
    if(op == 4 or op == 2):
        command = "python3 {exe} {input} -2 -p {part} {cmd_comp} -t {original}".format(exe=file_exe, input=file_input, part=P, cmd_comp=cmd_comp, original=inp)
        execute_command(command)
        file_datas.append(inp + "_2_data.txt")
        legend.append("In partitions " + r_name)
    
    if(op == 4 or op == 3):
        command = "python3 {exe} {input} -3 -p {part} {cmd_comp} -t {original}".format(exe=file_exe, input=file_input, part=P, cmd_comp=cmd_comp, original=inp)
        execute_command(command)
        file_datas.append(inp + "_3_data.txt")
        legend.append("In 3-components + partitions " + r_name)

##########################################################################################################
### Function that create the parts ###

def create_file(file_inp, file_output, op_reorder, r):

    command = "python3 {reorder} {input} {output} {op}".format(reorder=cmdreorder, input=file_inp, output=file_output, op=op_reorder)
    execute_command(command)
    file_output = file_output + str(r) + ".fastq" # Name of file reordered
    command = "python3 {create} {input}".format(create=cmdcreate, input=file_output)
    execute_command(command)

##########################################################################################################

def execute_command(command):

    try:    
        start = time.time()
        subprocess.call(command, shell = True)
        time1 = time.time()-start
    except subprocess.CalledProcessError:
        print("Error to executing command line: {command}".format(command = command))
        return False
    return time1 #return time of the execution

##########################################################################################################

if __name__ == "__main__":
    main()