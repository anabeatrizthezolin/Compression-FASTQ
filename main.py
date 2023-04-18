import sys, time, argparse, subprocess, os.path, pathlib, shutil
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
sap = "./sap"
lex = "./lex"

def main():
    parser = argparse.ArgumentParser(description=Description, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('input',         help='input file name', type=str, nargs='+')
    parser.add_argument('-o','--output', help='output base name (def. input base name)', default="", type=str) 
    parser.add_argument('--7z',          help='compression 7 zip: compression of the file with 7 zip', action='store_true', default = False)
    parser.add_argument('--bsc',         help='compression bsc: compression of the file with bsc', action='store_true', default = False)
    parser.add_argument('-1', '--c1',    help='compression 1: compression of the input file', action='store_true', default = False)
    parser.add_argument('-2', '--c2',    help='compression 2: compression of the file in blocks', action='store_true', default = False)
    parser.add_argument('-3', '--c3',    help='compression 3: compression of the file in partitions', action='store_true', default = False)
    parser.add_argument('--sap',         help='reorder sap: reorder file reads with SAP', action='store_true', default = False)
    parser.add_argument('--lex',         help='reorder in lexicographical order: reorder file reads in lexicographical order', action='store_true', default = False)
    parser.add_argument('-p','--part',   help='size of the part for file division', default=False, type=int)
    parser.add_argument('-v',            help='verbose: extra info in the log file',action='store_true')
    args = parser.parse_args()
    
    define_basename(args)
    
    path = os.path.split(sys.argv[0])[0]
    path_inp = os.path.split(sys.argv[1])[0]
    inp = os.path.splitext(sys.argv[1])[0]

    if(args.output): #all output files named args.out
        logfile_name = os.path.join(path_inp, args.output) + ".zip.log"
        file_out = os.path.join(path_inp, args.output) + ".zip"
        file_header = os.path.join(path_inp, args.output) + ".header"
        file_dna = os.path.join(path_inp, args.output) + ".dna"
        file_qs = os.path.join(path_inp, args.output) + ".qs"
        file_aux = os.path.join(path_inp, args.output) + "_"
    else: #all output files named input
        logfile_name = inp + ".zip.log"
        file_out = inp + ".zip"
        file_outh = inp + "_header.zip"
        file_outd = inp + "_dna.zip"
        file_outq = inp + "_qs.zip"
        file_header = inp + ".header"
        file_dna = inp + ".dna"
        file_qs = inp + ".qs"
        file_aux = inp + "_"
    

    if(args.bsc): #if the compression is with bsc
        zip = 0
    else: #if the compression is with 7zip
        zip = 1
    
    if(args.c1): #if the compression is total
        aux = 1
    if(args.c2): #if the compression is in blocks
        aux = 2
    if(args.c3): #if the compression is in partitions
        aux = 3
    
    file_data = "dataset/frag_1_"+ str(aux) + "_data.txt" #create the document with the compression and time data
    print("Sending logging messages to file:", logfile_name)

    with open(logfile_name,"a") as logfile:
        print(">>> Begin computation",file=logfile)
        show_command_line(logfile)
        logfile.flush()
        
        if(args.part):
            part = args.part

        sarq = os.path.getsize(sys.argv[1])

        if(args.sap):
            order = 0
            time_r = reorder(sys.argv[1], order, path, path_inp)
            file_inp = path_inp + '_sap.fastq'
        
        elif(args.lex):
            order = 1
            time_r = reorder(sys.argv[1], order, path, path_inp)
            file_inp = path_inp + '_lex.fastq'

        else:
            time_r = 0

        f_data = open(file_data, 'a') #open file data

        ###### print data from the compression ######
        print("\n\n###### COMPRESSION ######\n")
        print("Size .fastq: {:.6f} bytes\n".format(sarq))

        if(args.c1): #if the compression is total
            
            time1 = compression(file_out, sys.argv[1], logfile_name, zip) #return of the time compression 
            sarq_zip1 = os.path.getsize(file_out) 

            print("Size .zip: {:.6f} bytes".format(sarq_zip1))
            print("Compression 1 (FASTQ): {:.6f}\n".format(sarq_zip1/sarq))
            print("Time 1: {:.6f}".format(time1))
            f_data.write("{:.6f} {:.6f}\n".format(sarq_zip1/sarq, time1))

        if(args.c2): #if the compression is in 3 blocks (header, dna and qs)
            
            time2 = 0
            blocks(file_header, file_dna, file_qs)

            #return of the time compression, sum of the times
            time2 = time2 + compression(file_outh, file_header, logfile_name, zip) 
            time2 = time2 + compression(file_outd, file_dna, logfile_name, zip)
            time2 = time2 + compression(file_outq, file_qs, logfile_name, zip)
            sarq_zip2 = os.path.getsize(file_outh) + os.path.getsize(file_outd) + os.path.getsize(file_outq)

            print("Size _header.zip: {:.6f} bytes".format(os.path.getsize(file_outh)))
            print("Size _dna.zip: {:.6f} bytes".format(os.path.getsize(file_outd)))
            print("Size _qs.zip: {:.6f} bytes".format(os.path.getsize(file_outq)))
            print("Compression 2 (header + dna + qs): {:.6f}\n".format(sarq_zip2/sarq))
            print("Time 2: {:.6f}".format(time2))
            f_data.write("{:.6f} {:.6f}\n".format(sarq_zip2/sarq, time2))

        if(args.c3): #if the compression is in partitions (size set in the input command)
            
            time3 = 0
            partition(file_aux, part)
            parts = sarq/part
            cont = 1
            sarq_zip3 = 0
            while(cont <= parts):

                file_part = file_aux + str(cont) + ".part"
                if(zip == 1):
                    file_outp = file_aux + str(cont) + ".zip"
                else:
                    file_outp = file_aux + str(cont) + ".bsc"

                time3 = time3 + compression(file_outp, file_part, logfile_name, zip) #return of the time compression, sum of the times
                sarq_zip3 = sarq_zip3 + os.path.getsize(file_outp)
                cont = cont + 1

            print("Size of one part.zip: {:.6f} bytes".format(sarq/parts))
            print("Compression 3 (sum parts): {:.6f}".format(sarq_zip3/sarq))
            print("Time 3: {:.6f}".format(time3))
            f_data.write("{:.6f} {:.6f}\n".format(sarq_zip3/sarq, time3))

        f_data.close() #close data file

##########################################################################################################
###### function of the reorder ######
##########################################################################################################
def reorder(file_input, order, path, path_inp): 
    if(order == 0): #reorder with SAP
        exe = os.path.join(path, sap)
        file_order = path_inp + '_sap.fastq'
    else: #compression in lexicographical order
        exe = os.path.join(path, lex)
        file_order = path_inp + '_lex.fastq'

    command = "{exe} {input} {order}".format(exe=exe, input=file_input, order=file_order)
    #execution of the command
    print(command)
    time_r = execute_command(command)
    return time_r #return time of the reorder
        
##########################################################################################################
###### function of the compression ######
##########################################################################################################
def compression(file_out, file_input, logfile, zip): 
    if(zip == 1): #compression with bsc
        cmd = cmd7z
        command =  cmd + " {zip} {input} >> {log}".format(zip=file_out, input=file_input, log=logfile)
    else: #compression with bsc
        cmd = cmdbsc
        command =  cmd + " {input} {zip} >> {log}".format(zip=file_out, input=file_input, log=logfile)
    
    
    #execution of the command
    time1 = execute_command(command)
    return time1 #return time de compression

##########################################################################################################
###### function of the blocks division ######
##########################################################################################################
def blocks(file_header, file_dna, file_qs):

    f = open(sys.argv[1], 'r')
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
def partition(file_aux, part):

    cont = 1 #count the number of parts

    file_part = file_aux + str(cont) + ".part"
    f_part = open(file_part, 'w')
    f = open(sys.argv[1], 'r')
    
    sum = 0
    s = None
    while(s != ""):
        for i in range(4):
            s = f.readline()
            sum += len(s)
            f_part.write(s) #header, dna, +, qs
        
        if(sum >= part):
            cont += 1
            sum = 0
            f_part.close()
            file_part = file_aux + str(cont) + ".part"
            f_part = open(file_part, 'w')

    f_part.close()
    f.close()

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
        time1 = time.time()-start
    except subprocess.CalledProcessError:
        print("Error to executing command line: {command}".format(command = command))
        return False
    return time1 #return time of the execution

##########################################################################################################

def show_command_line(f):
    f.write("Python command line: ") 
    for x in sys.argv:
        f.write(x+" ")
    f.write("\n") 

##########################################################################################################

if __name__ == '__main__':
    main()