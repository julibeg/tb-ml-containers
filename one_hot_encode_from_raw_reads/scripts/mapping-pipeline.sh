#!/bin/bash

fw_reads=$1
rv_reads=$2
ref_fasta=$3

bwa-mem2 index "$ref_fasta"

bwa-mem2 mem \
    -t 1 \
    -R "@RG\tID:trimmed_\tSM:trimmed_\tPL:Illumina" \
    "$ref_fasta" \
    "$fw_reads" \
    "$rv_reads" \
    | samtools view -@ 1 -b - \
    | samtools fixmate -@ 1 -m - - \
    | samtools sort -@ 1 - -o reads.sorted.bam

samtools index reads.sorted.bam