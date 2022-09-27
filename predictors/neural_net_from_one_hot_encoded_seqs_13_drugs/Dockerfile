FROM tensorflow/tensorflow:2.7.0

LABEL software.version="0.7.0"
LABEL image.name="julibeg/tb-ml-neural-net-from-one-hot-encoded-seqs-13-drugs"

RUN pip install pandas==1.4.2

# copy the target loci, model, and scripts
RUN mkdir /internal_data /data
COPY model /internal_data/model
COPY data_files/target_loci.csv /internal_data
COPY scripts/main.py /
COPY scripts/entrypoint.sh /

WORKDIR /data

ENTRYPOINT ["/bin/bash", "/entrypoint.sh"]
