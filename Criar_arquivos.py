import sys, time, argparse, subprocess, os.path, pathlib, shutil
from xml.etree.ElementInclude import default_loader


path = os.path.split(sys.argv[0])[0]
path_inp = os.path.split(sys.argv[1])[0]
inp = os.path.splitext(sys.argv[1])[0]
file_aux = inp + "_"

cont = 25
    
sarq = os.path.getsize(sys.argv[1])
part = 25000000

file_part = file_aux + str(cont) + "MB.fastq"
f_part = open(file_part, 'w')
f = open(sys.argv[1], 'r')

sum = 0
s = None
while(s != "" and cont < os.path.getsize(sys.argv[1])):
    
    for i in range(4):
        s = f.readline()
        f_part.write(s) #header, dna, +, qs
        sum += len(s)

    if(sum >= part):
        cont += 25
        part = part + 25000000
        sum = 0
        f_part.close()
        f.close()
        f = open(sys.argv[1], 'r')
        s = None
        file_part = file_aux + str(cont) + 'MB.fastq'
        f_part = open(file_part, 'w')

f_part.close()
f.close()