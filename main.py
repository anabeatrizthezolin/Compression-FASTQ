import sys, time, argparse
import subprocess, os.path, pathlib
import math, shutil
from xml.etree.ElementInclude import default_loader

Description = """FASTQ file compression tool
For example
    {exe} example.txt

--------------------------
Command line options:
--------------------------
""".format(exe=sys.argv[0])

cmd7z = "7z a -mm=PPMd"
cmdbsc = "external/libbsc/bsc e"
cmdreorder = "reorder.py"
sap = "./sap"
lex = "./lex"

def main():
    parser = argparse.ArgumentParser(description=Description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('input',           help='input file name', type=str, nargs='+')
    parser.add_argument('-o', '--output',  help='output base name (def. input base name)', default="", type=str) 
    parser.add_argument('--7z',            help='compression 7 zip: compression of the file with 7 zip', action='store_true', default = False)
    parser.add_argument('--bsc',           help='compression bsc: compression of the file with bsc', action='store_true', default = False)
    parser.add_argument('-1', '--c1',      help='compression 1: compression of the input file', action='store_true', default = False)
    parser.add_argument('-2', '--c2',      help='compression 2: compression of the file in partitions', action='store_true', default = False)
    parser.add_argument('-3', '--c3',      help='compression 3: compression of the file in 3-components and partitions', action='store_true', default = False)
    parser.add_argument('-r', '--reorder', help='reorder option: 1 (lexicographical order), 2 (colexicographical order) or 3(random order)', default=False, type=int)
    parser.add_argument('-p', '--part',    help='size of the part for file division in MB', default=False, type=int)
    parser.add_argument('-t', '--test',    help='compression test: original file', default="", type=str)
    parser.add_argument('-v',              help='verbose: extra info in the log file',action='store_true')
    args = parser.parse_args()
    
    define_basename(args)
    
    path = os.path.split(sys.argv[0])[0]
    path_inp = os.path.split(sys.argv[1])[0]
    inp = os.path.splitext(sys.argv[1])[0]

    if(args.bsc): #if the compression is with bsc
        op_comp = 0
    else: #if the compression is with 7zip
        op_comp = 1

    file_inp = sys.argv[1]
    if(args.reorder):
        op = args.reorder
        reorder(sys.argv[1], inp, op)
        if(op == 1):
            r = '_lex'
            file_inp = inp + "_lex.fastq"
        elif(op == 2):
            r = '_colex'
            file_inp = inp + "_colex.fastq"
        elif(op == 3):
            r = '_random'
            file_inp = inp + "_random.fastq"
    
    if(args.output): #all output files named args.argv[1]
        inp_aux = os.path.join(path_inp, args.output)
        if(args.reorder):
            inp_aux = inp_aux + r

    else: #all output files named --output
        inp_aux = inp
        if(args.reorder):
            inp_aux = inp + r
    
    if(op_comp == 1):
        logfile_name = inp_aux + ".zip.log"
        file_out = inp_aux + ".zip"
        file_outh = inp_aux + "_header.zip"
        file_outd = inp_aux + "_dna.zip"
        file_outq = inp_aux + "_qs.zip"
    else:
        logfile_name = inp_aux + ".bsc.log"
        file_out = inp_aux + ".bsc"
        file_outh = inp_aux + "_header.bsc"
        file_outd = inp_aux + "_dna.bsc"
        file_outq = inp_aux + "_qs.bsc"

    file_header = inp_aux + ".header"
    file_dna = inp_aux + ".dna"
    file_qs = inp_aux + ".qs"
    file_aux = inp_aux + "_"
    
    if(args.c1): #if the compression is total
        aux = 1
    if(args.c2): #if the compression is in partitions
        aux = 2
    if(args.c3): #if the compression is in 3-components + partitions
        aux = 3
   
    print("Sending logging messages to file:", logfile_name)

    with open(logfile_name,"a") as logfile:
        print(">>> Begin computation",file=logfile)
        show_command_line(logfile)
        logfile.flush()
        
        if(args.part):
            part = args.part*(2**20) # X MB
        else:
            part = 10*(2**20) # 10 MB

        sarq = os.path.getsize(file_inp)
        if(args.test):
            inp_original = os.path.splitext(args.test)[0]
            file_data = inp_original + "_" + str(aux) + "_data.txt" #create the document with the compression and time data
            f_data = open(file_data, 'a') #open file data

        ###### print data from the compression ######
        print("\n\n###### COMPRESSION ######\n")
        print("Size .fastq: {:.6f} bytes\n".format(sarq))

        if(args.c1): #if the compression is total
            
            t = compression(file_out, file_inp, logfile_name, op_comp ) #return of the time compression 
            sarq_c = os.path.getsize(file_out)
            ratio = (sarq_c/sarq)*100

            print("Size .zip: {:.6f} bytes".format(sarq_c))
            print("Compression 1 (FASTQ): {:.6f}".format(sarq_c/sarq))
            print("Time 1: {:.6f}".format(t))
            if(args.test):
                f_data.write("{:.6f} {:.6f} {:.2f}\n".format(sarq_c/sarq, t, ratio))
        
        if(args.c2): #if the compression is in partitions (size set in the input command)
            
            parts = partition(file_aux, part, file_inp)
            cont = 1
            sarq_c = 0
            t = 0
            while(cont <= parts):
                file_part = file_aux + str(cont) + ".part"
                if(op_comp == 1):
                    file_outp = file_aux + str(cont) + ".zip"
                else:
                    file_outp = file_aux + str(cont) + ".bsc"

                t = t + compression(file_outp, file_part, logfile_name, op_comp) #return of the time compression, sum of the times
                sarq_c = sarq_c + os.path.getsize(file_outp)
                cont = cont + 1
            ratio = (sarq_c/sarq)*100

            print("Compression 3 (sum parts): {:.6f}".format(sarq_c/sarq))
            print("Time: {:.6f}".format(t))
            if(args.test):
                f_data.write("{:.6f} {:.6f} {:.2f}\n".format(sarq_c/sarq, t, ratio))
            
        if(args.c3): #if the compression is in 3-components (header, dna and qs)
            
            t = 0
            components(file_header, file_dna, file_qs, file_inp)

            file_h = os.path.splitext(file_outh)[0] + "_"
            file_d = os.path.splitext(file_outd)[0] + "_"
            file_q = os.path.splitext(file_outq)[0] + "_"

            parts_h = partition(file_h, part, file_header)
            parts_d = partition(file_d, part, file_dna)
            parts_q = partition(file_q, part, file_qs)

            cont = 1
            sarq_c = 0
            t = 0
            while(cont <= parts_h or cont <= parts_d or cont <= parts_q):

                if(cont <= parts_h):
                    file_part = file_h + str(cont) + ".part"
                    if(op_comp == 1):
                        file_outp = file_h + str(cont) + ".zip"
                    else:
                        file_outp = file_h + str(cont) + ".bsc"

                    t = t + compression(file_outp, file_part, logfile_name, op_comp) #return of the time compression, sum of the times
                    sarq_c = sarq_c + os.path.getsize(file_outp)

                if(cont <= parts_d):
                    file_part = file_d + str(cont) + ".part"
                    if(op_comp == 1):
                        file_outp = file_d + str(cont) + ".zip"
                    else:
                        file_outp = file_d + str(cont) + ".bsc"
                    t = t + compression(file_outp, file_part, logfile_name, op_comp) #return of the time compression, sum of the times
                    sarq_c = sarq_c + os.path.getsize(file_outp)

                if(cont <= parts_q):
                    file_part = file_q + str(cont) + ".part"
                    if(op_comp == 1):
                        file_outp = file_q + str(cont) + ".zip"
                    else:
                        file_outp = file_q + str(cont) + ".bsc"

                    t = t + compression(file_outp, file_part, logfile_name, op_comp) #return of the time compression, sum of the times
                    sarq_c = sarq_c + os.path.getsize(file_outp)
                cont = cont + 1
            ratio = (sarq_c/sarq)*100

            print("Compression 3-components with partitions (sum parts): {:.6f}".format(sarq_c/sarq))
            print("Time: {:.6f}".format(t))
            if(args.test):
                f_data.write("{:.6f} {:.6f} {:.2f}\n".format(sarq_c/sarq, t, ratio))

        if(args.test):
            f_data.close() #close data file
        
##########################################################################################################
###### function of the reordered ######
##########################################################################################################
def reorder(file_inp, file_output, op):
    command = "python3 {reorder} {input} {output} {op}".format(reorder=cmdreorder, input=file_inp, output=file_output, op=op)
    execute_command(command)

##########################################################################################################
###### function of the compression ######
##########################################################################################################
def compression(file_out, file_input, logfile, op_comp): 
    if(op_comp == 1): #compression with 7zip
        cmd = cmd7z
        command =  cmd + " {zip} {input} >> {log}".format(zip=file_out, input=file_input, log=logfile)
    else: #compression with bsc
        cmd = cmdbsc
        command =  cmd + " {input} {zip} >> {log}".format(zip=file_out, input=file_input, log=logfile)

    #execution of the command
    t = execute_command(command)
    return t #return time de compression

##########################################################################################################
###### function of the 3-components division ######
##########################################################################################################
def components(file_header, file_dna, file_qs, file_inp):

    f = open(file_inp, 'r')
    f_header = open(file_header, 'w') #file with header
    f_dna = open(file_dna, 'w') #file with dna
    f_qs = open(file_qs, 'w') #file with qs

    s = None
    while(s != ""):
        s = f.readline()
        f_header.write(s)
        s = f.readline()
        f_dna.write(s)
        #+
        s = f.readline() 
        s = f.readline()
        f_qs.write(s)

    f_header.close()
    f_dna.close()
    f_qs.close()
    f.close()

##########################################################################################################
###### function of the partition ######
##########################################################################################################
def partition(file_aux, part, file_inp):

    cont = 1 #count the number of parts

    file_part = file_aux + str(cont) + ".part"
    f_part = open(file_part, 'w')
    f = open(file_inp, 'r')
    sum = 0
    s = None
    while(s != ""):
        for i in range(4):
            s = f.readline()
            sum += len(s)
            f_part.write(s) #header, dna, +, qs
        
        if(s == "" and sum < part):
            cont = cont + 1
        elif(sum >= part):
            cont = cont + 1
            sum = 0
            f_part.close()
            file_part = file_aux + str(cont) + ".part"
            f_part = open(file_part, 'w')

    f_part.close()
    f.close()
    return cont-1

##########################################################################################################

def define_basename(args):
    if len(args.output)==0:
        args.basename = args.input[0]
    else:
        args.basename = args.output

##########################################################################################################
###### function of the command execution #######
##########################################################################################################
def execute_command(command):
    try:    
        start = time.time()
        subprocess.call(command, shell = True)
        t = time.time()-start
    except subprocess.CalledProcessError:
        print("Error to executing command line: {command}".format(command = command))
        return False
    return t #return time of the execution

##########################################################################################################

def show_command_line(f):
    f.write("Python command line: ") 
    for x in sys.argv:
        f.write(x+" ")
    f.write("\n") 

##########################################################################################################

if __name__ == '__main__':
    main()