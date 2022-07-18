FROM mambaorg/micromamba:0.24.0

LABEL software.version="0.3.0"
LABEL image.name="julibeg/tb-ml-freebayes-vc-from-cram"

RUN micromamba install -n base -c bioconda -c conda-forge -y \
    pandas=1.4.1 \
    freebayes=1.3.6 \
    bcftools=1.15 \
    samtools=1.14 && \
    micromamba clean --all --yes

# create a directory for the internal data used by the container
USER root
RUN mkdir /internal_data /data
# copy the refgenome and the header for the dummy VCF
COPY data_files/MTB-h37rv_asm19595v2-eg18.fa /internal_data/refgenome.fa
COPY data_files/MTB-h37rv_asm19595v2-eg18.fa.fai /internal_data/refgenome.fa.fai
COPY data_files/vcf_header.txt /internal_data

# copy the entrypoint script and the shell helper script
COPY scripts/entrypoint.py /
COPY scripts/get_genotypes.sh /

# set `/data` as working directory so that the output is written to the
# mount point when run with `docker run -v $PWD:/data ... -o output.csv`
WORKDIR /data

ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "python", "/entrypoint.py"]
