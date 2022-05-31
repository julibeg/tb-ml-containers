FROM continuumio/miniconda3:latest

LABEL software.version="0.1.0"
LABEL image.name="jodyphelan/tb-ml-base-calls-from-cram"

RUN conda install -c bioconda -c conda-forge -y \
    sambamba \
    samtools=1.12

RUN mkdir /internal_data

# copy the entrypoint script and the python helper script
COPY scripts/entrypoint.py /

ENTRYPOINT ["python", "/entrypoint.py"]