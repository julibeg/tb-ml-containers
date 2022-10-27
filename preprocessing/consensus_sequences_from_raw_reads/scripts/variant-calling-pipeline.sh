#!/bin/bash

fw_reads=$1
rv_reads=$2
refgenome=$3
targets=$4
threads=${5:-1}

# READ TRIMMING
trimmomatic PE "$fw_reads" "$rv_reads" \
    -threads "$threads" \
    -phred33 \
    -baseout trimmed.fq.gz \
    LEADING:3 \
    TRAILING:3 \
    SLIDINGWINDOW:4:20 \
    MINLEN:36

# MAPPING
bwa-mem2 index "$refgenome" > /dev/null

bwa-mem2 mem \
    -t "$threads" \
    -R "@RG\tID:sample\tSM:sample\tPL:Illumina" \
    "$refgenome" \
    trimmed_1P.fq.gz \
    trimmed_2P.fq.gz |
    samtools fixmate -@ "$threads" -m - - |
    samtools sort -@ "$threads" - -o reads.sorted.bam

samtools index reads.sorted.bam

# VARIANT-CALLING
freebayes reads.sorted.bam \
    -f "$refgenome" \
    -t "$targets" \
    -p 1 |
    bcftools sort -Ou |
    bcftools norm -f "$refgenome" -m- -Ou |
    bcftools norm -d none \
        -Oz -o variants.vcf.gz \
        2> >(grep -v ^Lines)

bcftools index variants.vcf.gz -f
