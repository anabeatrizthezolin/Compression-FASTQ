# Compression-FASTQ 

This repository contains a set of algorithms for evaluating the compression of FASTQ files.

We used lexicographic, colexicographic and random sorting to reorder the DNA sequences in the file. 
The reordering methods used were partitioned and 3-component with partitioning. 
The 7zip and bsc methods were used to compress the files. 

## Build requirements

python3

make

```sh
pip install numpy
pip install -U matplotlib
pip install argparse
pip install os.path2
pip install pathlib
pip install pytest-shutil
pip install subprocess.run
```

## Example

**Compilation:**

```sh
git clone --recursive https://github.com/anabeatrizthezolin/Compression-FASTQ.git
make
```

**Available options:**

```sh
-o    output converted file
--7z  compression of the file with 7 zip
--bsc compression of the file with bsc
-1    compression 1: compression of the input file
-2    compression 2: compression  of the file in partitions
-3    compression 3: compression of the file in 3-components and partitions
-r    reorder option: 1 (lexicographical order), 2 (colexicographical order) or 3(random order)
-p    size of the part for file division in MB
-t    compression test: original file
-v    verbose output
-h    this help message

```
_Notes:_ 
- Supported extensions _.fastq_.


**Run a test: main.py**

```c
python3 main.py dataset/frag.fastq --bsc -3 -r 2
```

**Output:**

```c
Sending logging messages to file: dataset/frag_colex.bsc.log


###### COMPRESSION ######

Size .fastq: 293596682.000000 bytes

Compression 3-components with partitions (sum parts): 0.338181
```

**Run a test: Script_Test.py**

```c
python3 Script_test.py dataset/frag.fastq --bsc -c 3 -r 4
```

**Output:**

```c
Sending logging messages to file: dataset/frag_colex.bsc.log


###### COMPRESSION ######

Size .fastq: 293596682.000000 bytes

Compression 3-components with partitions (sum parts): 0.33818
```
<img align="center" src="resources/c3bsc.png?raw=true" />
</a>
<img align="center" src="resources/t3bsc.png?raw=true" />
</a>