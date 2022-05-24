FROM continuumio/miniconda3:latest

LABEL software.version="0.1.0"
LABEL image.name="julibeg/tb-ml-freebayes-vc-from-cram"

RUN conda install -c bioconda -c conda-forge -y \
    pandas=1.4.1 \
    freebayes=1.3.6 \
    bcftools=1.15 \
    samtools=1.14

RUN mkdir /internal_data

# copy the refgenome and the header for the dummy VCF
COPY data_files/MTB-h37rv_asm19595v2-eg18.fa /internal_data/refgenome.fa
RUN samtools faidx /internal_data/refgenome.fa
COPY data_files/vcf_header.txt /internal_data

# copy the entrypoint script and the python helper script
COPY scripts/entrypoint.py /
COPY scripts/get_genotypes.sh /

ENTRYPOINT ["python", "/entrypoint.py"]