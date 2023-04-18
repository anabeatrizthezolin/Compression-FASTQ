CC = g++
#CFLAGS += -Wall 
CFLAGS += -g -O0
CFLAGS += -D_FILE_OFFSET_BITS=64 -m64 -O3 -fomit-frame-pointer -Wno-char-subscripts 

LFLAGS = -lm -lrt -ldl -lz

INPUT = dataset/input.100.txt
ALG = 10
	
CFLAGS += $(DEFINES)

all:
	make main  

clean:
	\rm dataset/*.log dataset/*.zip dataset/*.header dataset/*.dna dataset/*.qs dataset/*.part dataset/*.txt dataset/*.bsc dataset/*order.fastq dataset/*MB.fastq

main: 
	$(CC) -o sap SAP.cpp $(CFLAGS) $(LFLAGS) 
	$(CC) -o lex lex.cpp $(CFLAGS) $(LFLAGS) 
	
run:
	./sap $(INPUT) -A $(ALG)
	./lex $(INPUT) -A $(ALG)