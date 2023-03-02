# Docker container to create consensus sequences of target loci from raw reads

This container generates consensus sequences of _M. tuberculosis_ raw reads in a list of target regions. It requires the reads, a CSV file with coordinates of the target regions, and a name for the output FASTA file. `bwa-mem2` is used for aligning the reads against H37Rv (asm19595v2) and variants are called with `freebayes`. The CSV file with the target regions should have the header line 'locus,start,end'.

## Usage

FASTQ files with forward and reverse _M tuberculosis_ reads and a CSV file specifying the target loci are required as input. The container uses `/data` as working directory and will create the output file there.

```bash
docker run -v $PWD:/data \
    julibeg/tb-ml-consensus-seqs-from-raw-reads:v0.1.1 \
    -r target_loci.csv \
    -o consensus_seqs.fasta \
    my-sample_1.fastq.gz \
    my-sample_2.fastq.gz
```
