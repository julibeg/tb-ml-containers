FROM mambaorg/micromamba:0.27.0

LABEL software.version="0.1.0"
LABEL image.name="julibeg/tb-ml-aggreen-mtb-cnn"

RUN micromamba install -y -n base -c conda-forge -c bioconda \
    pandas=1.4.1 \
    numpy=1.23.4 \
    tensorflow=2.4.1 \
    biopython=1.79 \
    samtools=1.15 \
    mafft=7.508 \
    && micromamba clean --all --yes

# copy the target loci, model, and scripts
USER root
ADD model/MDCNN_saved_model.tar.gz /internal_data/
COPY data_files /internal_data
COPY scripts /scripts

RUN mkdir /data
WORKDIR /data

ENTRYPOINT ["/bin/bash", "/scripts/entrypoint.sh"]
