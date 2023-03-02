# Docker container to one-hot-encode consensus sequences from a SAM/BAM file

The container uses `sambamba` to transform target consensus sequences extracted from aligned reads into one-hot encoding. The start and end coordinates of the sequences are read from a CSV file which is required and must have the header line `locus,start,end`. The sequences are concatenated without gaps.

## Usage

A SAM/BAM/CRAM file with aligned reads against H37Rv and a CSV specifying target loci are required as input. The container uses `/data` as working directory and will create the output file there.

```bash
docker run -v $PWD:/data \
    julibeg/tb-ml-one-hot-encoded-seqs-from-aligned-reads:v0.4.0 \
    -b aligned_reads.cram \
    -r target_loci.csv \
    -o one_hot_seqs.csv
```
