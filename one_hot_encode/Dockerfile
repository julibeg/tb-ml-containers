FROM continuumio/miniconda3:latest

LABEL software.version="0.1.0"
LABEL image.name="julibeg/tb-ml-one-hot-encoded-from-cram"

RUN conda install -c bioconda -c conda-forge -y \
    sambamba \
    samtools=1.15 \
    pandas=1.4.2

# copy the reference genome
RUN mkdir /internal_data
COPY data_files/MTB-h37rv_asm19595v2-eg18.fa /internal_data/refgenome.fa

# copy the entrypoint script and the python helper script
COPY scripts/entrypoint.py /

ENTRYPOINT ["python", "/entrypoint.py"]