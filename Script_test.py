import sys, time, argparse, subprocess, os.path, pathlib, shutil
from xml.etree.ElementInclude import default_loader
import matplotlib.pyplot as plt

file_exe = 'main.py'

def main():
    parser = argparse.ArgumentParser(description='', formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('input',         help='input file name', type=str, nargs='+')
    parser.add_argument('-o','--output', help='output base name (def. input base name)', default="", type=str) 
    parser.add_argument('-n',            help='not execute main.py', action='store_true', default = False)
    args = parser.parse_args()
    
    define_basename(args)

    inp = os.path.splitext(sys.argv[1])[0]

    file_data1 = inp + "_1_data.txt"
    file_data2 = inp + "_2_data.txt"
    file_data3 = inp + "_3_data.txt"

    MB = 25
    arquivos = ["25", "50", "75", "100", "125", "150"]
    
    if(args.n == False):
        for item in arquivos:
            file_input = inp + '_' + item + 'MB.fastq'
            execute_main(file_input)
            print("Executado: {}MB".format(MB))
        
    graphic(file_data1, file_data2, file_data3)

##########################################################################################################

def graphic(file_data1,file_data2, file_data3):

    compres1, time1 = vectors_plot(file_data1)
    compres2, time2 = vectors_plot(file_data2)
    compres3, time3 = vectors_plot(file_data3)
    size = [25, 50, 75, 100, 125, 150]

    plot_compression("Compression", "Compression FASTQ", compres1, compres2, compres3, size) #Plot compression
    plot_compression("Time (s)", "Compression time FASTQ", time1, time2, time3, size) #Plot compression time

##########################################################################################################

def vectors_plot(file_data):

    compres = []
    time = []
    for line in open(file_data,'r'):
        lines = [i for i in line.split()]
        compres.append(float(lines[0]))
        time.append(float(lines[1]))

    return compres, time

##########################################################################################################

def plot_compression(labely, title, c1, c2, c3, size):
    
    ###### Plot compression or time ######
    plt.ylabel(labely, fontsize = 12)
    plt.xlabel('Size (MB)', fontsize = 12)
    plt.plot(size, c1, marker = 'o', c = 'g')
    plt.plot(size, c2, marker = 'o', c = 'r')
    plt.plot(size, c3, marker = 'o', c = 'b')

    plt.title(title, fontsize = 20)
    plt.legend(['File Original', 'File in blocks', 'File in partitions'], fontsize=14)
    plt.show()

##########################################################################################################

def execute_main(file_input): 

    command = "python3 {exe} {input} -1 --bsc".format(exe=file_exe, input=file_input)
    time1 = execute_command(command)

    command = "python3 {exe} {input} -2 --bsc".format(exe=file_exe, input=file_input)
    time1 = execute_command(command)

    command = "python3 {exe} {input} -3 -p 20000000 --bsc".format(exe=file_exe, input=file_input)
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

def define_basename(args):
    if len(args.output)==0:
        args.basename = args.input[0]
    else:
        args.basename = args.output

##########################################################################################################

if __name__ == '__main__':
    main()