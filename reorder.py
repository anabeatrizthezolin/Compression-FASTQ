import sys
import random

# Class to store data
class Fastq:
    def __init__(self, header, dna, qs):
        self.header = header
        self.dna = dna
        self.dna_reverse = dna[::-1]
        self.qs = qs

# Reorder the reads in colexicographical order using reversed reads
def sort_dna_reverse(read):
    return read.dna_reverse

# Reorder the reads in lexicographical order or random order
def sort_dna(read):
    return read.dna

# Write the reordered data to a new file
def save_out(file_out, i, fast):
    with open(file_out, 'w') as out:
        for k in range(i):
            out.write(fast[k].header + "\n")
            out.write(fast[k].dna + "\n")
            out.write("+\n")
            out.write(fast[k].qs + "\n")

# Function to print the data
def print_function(fast, i):
    for k in range(i):
        print(fast[k].header)
        print(fast[k].dna, fast[k].dna_reverse)
        print("+")
        print(fast[k].qs)

def main():    
    # Open file
    with open(sys.argv[1], 'r') as f:
        lines = f.readlines()
    nf = len(lines)
    fast = [] #create list

    # Read file
    i = 0
    p = 0
    while p < nf:
        header = lines[p].strip()
        p += 1
        dna = lines[p].strip()
        p += 1
        dna_reverse = dna[::-1]
        p += 1
        qs = lines[p].strip()
        fastq = Fastq(header, dna, qs)
        fast.append(fastq)
        i += 1
        p += 1

    #print_function(fast, i)

    op = int(sys.argv[3]) # Reorder option 

    # Option lexicographic
    if(op == 1 or op == 4):
        file_lex = sys.argv[2] + '_lex.fastq'
        fast.sort(key=sort_dna, reverse=False)
        save_out(file_lex, i, fast)

    # Option colexicographic
    if(op == 2 or op == 4):
        file_colex = sys.argv[2] + '_colex.fastq'
        fast.sort(key=sort_dna_reverse, reverse=False)
        save_out(file_colex, i, fast)
    
    # Option random
    if(op == 3 or op == 4):
        file_random = sys.argv[2] + '_random.fastq'
        random.shuffle(fast)
        save_out(file_random, i, fast)

    #print_function(fast, i)

if __name__ == "__main__":
    main()
