FROM tensorflow/tensorflow:2.7.0

LABEL software.version="0.1.0"
LABEL image.name="julibeg/tb-ml-neural-net-predictor-13-drugs"

RUN pip install pandas==1.4.2

# copy the model and the script for performing the prediction
COPY model /model
COPY scripts/entrypoint.py /

ENTRYPOINT ["python", "/entrypoint.py"]
