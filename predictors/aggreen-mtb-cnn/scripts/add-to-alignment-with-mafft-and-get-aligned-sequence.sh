#!/bin/bash

input_fasta=$1
alignment_file=$2

input_seq_id=$(sed -n '1s/>//p' "$input_fasta")

# add the consensus to the MSA
mafft --add "$input_fasta" \
    --keeplength \
    "$alignment_file" \
    >alignment.fa

samtools faidx alignment.fa
samtools faidx alignment.fa "$input_seq_id" | sed 1d
