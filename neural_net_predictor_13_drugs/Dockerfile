FROM tensorflow/tensorflow:2.7.0

LABEL software.version="0.5.0"
LABEL image.name="julibeg/tb-ml-neural-net-predictor-13-drugs"

RUN pip install pandas==1.4.2

# copy the target loci, model, and the script for performing the prediction
RUN mkdir /internal_data /data
COPY model /internal_data/model
COPY data_files/target_loci.csv /internal_data
COPY scripts/entrypoint.py /

WORKDIR /data

ENTRYPOINT ["python", "/entrypoint.py"]
