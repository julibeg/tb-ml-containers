FROM mambaorg/micromamba:0.24.0

LABEL software.version="0.5.0"
LABEL image.name="julibeg/tb-ml-one-hot-encoded-seqs-from-aligned-reads"

RUN micromamba install -n base -c bioconda -c conda-forge -y \
    sambamba=0.6.8 \
    samtools=1.12 \
    pandas=1.4.2 && \
    micromamba clean --all --yes

USER root
# copy the python main and bash entrypoint scripts
COPY scripts/entrypoint.sh /
COPY scripts/main.py /

# set `/data` as working directory so that the output is written to the
# mount point when run with `docker run -v $PWD:/data ... -o output.csv`
RUN mkdir /data
WORKDIR /data

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
