# Docker container to one-hot-encode consensus sequences from raw reads

This container uses `bwa-mem2 mem` to align raw reads to the _M tuberculosis_ H37Rv reference genome (ASM19595v2) and afterwards extracts one-hot-encoded consensus sequences of a list of target loci. The start and end coordinates of the target sequences are read from a CSV file which is required and must have the header line `locus,start,end`. The sequences are concatenated without gaps.

## Usage

FASTQ files with forward and reverse _M tuberculosis_ reads and a CSV file specifying the target loci are required as input. The container uses `/data` as working directory and will create the output file there.

```bash
docker run -v $PWD:/data \
    julibeg/tb-ml-one-hot-encoded-seqs-from-raw-reads:v0.1.0 \
    -r target_loci.csv \
    -o one_hot_seqs.csv \
    my-sample_1.fastq.gz \
    my-sample_2.fastq.gz
```
