CC = g++
#CFLAGS += -Wall 
CFLAGS += -g -O0
CFLAGS += -D_FILE_OFFSET_BITS=64 -m64 -O3 -fomit-frame-pointer -Wno-char-subscripts 

LFLAGS = -lm -lrt -ldl -lz

INPUT = dataset/input.100.txt
ALG = 10
	
CFLAGS += $(DEFINES)

all:
	make -C external/gsufsort/ DNA=1
	make main  

clean:
	\rm dataset/*.log dataset/*.zip dataset/*.header dataset/*.dna \
	dataset/*.qs dataset/*.part dataset/*.bsc dataset/*.4.lcp \
	dataset/*.4.sa dataset/*.bwt dataset/*.optBWT dataset/*data.txt \
	dataset/*.4.lcp dataset/*.4.sa dataset/*.4.isa \
	dataset/*.bwt  dataset/*_lex.fastq dataset/*_colex.fastq \
	dataset/*_random.fastq dataset/*MB.fastq

main: 
	$(CC) -o optBWT optBWT.cpp $(CFLAGS) $(LFLAGS)
	
run:
	./optBWT $(INPUT) -A $(ALG)