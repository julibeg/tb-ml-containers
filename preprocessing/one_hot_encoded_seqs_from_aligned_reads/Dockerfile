FROM mambaorg/micromamba:0.24.0

LABEL software.version="0.4.0"
LABEL image.name="julibeg/tb-ml-one-hot-encoded-seqs-from-aligned-reads"

RUN micromamba install -n base -c bioconda -c conda-forge -y \
    sambamba=0.6.8 \
    samtools=1.12 \
    pandas=1.4.2 && \
    micromamba clean --all --yes

# create a directory for the internal data used by the container
USER root
RUN mkdir /internal_data /data
# copy the reference genome
COPY data_files/MTB-h37rv_asm19595v2-eg18.fa /internal_data/refgenome.fa

# copy the python main and bash entrypoint scripts
COPY scripts/entrypoint.sh /
COPY scripts/main.py /

# set `/data` as working directory so that the output is written to the
# mount point when run with `docker run -v $PWD:/data ... -o output.csv`
WORKDIR /data

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]