# Docker container to call variants with Freebayes from a SAM/BAM/CRAM file

This example container uses [Freebayes](https://github.com/freebayes/freebayes)
to call variants from a sorted BAM/CRAM file with reads aligned against H37Rv
ASM19595v2. In addition to the aligned reads, it also expects a CSV with target
variants for which there must be a genotype in the output file. This is needed
for prediction containers relying on a pre-determined set of variants as input
data. The header line of the CSV should be `POS,REF,ALT,AF` with the `AF` column
holding allele frequencies that can be used to replace non-calls. 

It will write the called variants to a CSV with the columns `POS,REF,ALT,GT`.

## Usage

The container uses `/data` as working directory and will create the output file
there. It can be called like this:

```bash
docker run -v $PWD:/data \
    julibeg/tb-ml-freebayes-vc-from-cram:v0.2.0 \
    -b aligned-reads.bam -t target-vars.csv -o called-variants.csv
```
