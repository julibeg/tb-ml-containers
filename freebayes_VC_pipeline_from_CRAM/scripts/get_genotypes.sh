#!/bin/bash
# set flags for "strict" mode
set -Eeuxo pipefail

# store paths in variables
bam_file=$1
target_vars_file=$2
vcf_header=/internal_data/vcf_header.txt
refgenome=/internal_data/refgenome.fa

# write the target variants to a dummy VCF and a dummy BED file
cp $vcf_header vars.vcf
sed '1d' "$target_vars_file" | awk -F',' \
    'BEGIN{OFS="\t"}
    {print "Chromosome", $1, ".", $2, $3, ".", ".", "AF=1"}' |
    sort -k2,2 -n >>vars.vcf
grep -v "#" vars.vcf | awk -F'\t' \
    'BEGIN{OFS="\t"}
    {print "Chromosome", $2-1, $2, ".", ".", $3, $4, ".", "AF=1"}' |
    sort -k2,2 -n >vars.bed

# extract the reads overlapping with the variants of interest
samtools index "$bam_file"
samtools view -bML vars.bed "$bam_file" -T $refgenome >extracted.bam

# print the header for the result
echo 'POS,REF,ALT,GT,DP'
# now run freebayes and format the output
freebayes -f $refgenome extracted.bam \
    --variant-input vars.vcf \
    --only-use-input-alleles |
    bcftools norm -f $refgenome -m - 2> >(grep -v ^Lines) |
    bcftools query -f '%POS,%REF,%ALT,[%GT,%DP]\n'
