#!/bin/bash

refgenome=$1
vcf_file=$2
region_string=$3

# extract the consensus sequence
samtools faidx "$refgenome" "$region_string" |
    bcftools consensus "$vcf_file" -s sample |
    sed 1d
