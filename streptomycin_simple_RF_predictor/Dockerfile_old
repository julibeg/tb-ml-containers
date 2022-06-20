FROM continuumio/miniconda3:latest

LABEL software.version="0.1.0"
LABEL image.name="julibeg/tb-ml-simple-rf-predictor-streptomycin"

RUN conda install -c conda-forge -y \
    numpy=1.22.3 \
    pandas=1.4.1 \
    joblib=1.1.0 \
    scikit-learn=1.0.2

# copy the model / data files and the script for performing the prediction
RUN mkdir /internal_data
COPY data_files/SM_RF_fitted.pkl /internal_data/model.pkl
COPY data_files/SM_RF_target_vars_AFs.csv /internal_data/target_vars.csv
COPY scripts/entrypoint.py /

ENTRYPOINT ["python", "/entrypoint.py"]
