FROM mambaorg/micromamba:0.24.0

LABEL software.version="0.3.0"
LABEL image.name="julibeg/tb-ml-simple-rf-predictor-streptomycin"

RUN micromamba install -y -n base -c conda-forge \
    pandas=1.4.1 \
    joblib=1.1.0 \
    scikit-learn=1.0.2 && \
    micromamba clean --all --yes

# create a directory for the internal data used by the container
USER root
RUN mkdir /internal_data /data
# copy the model / data files and the script for performing the prediction
COPY data_files/SM_RF_fitted.pkl /internal_data/model.pkl
COPY data_files/SM_RF_target_vars_AFs.csv /internal_data/target_vars.csv
COPY scripts/entrypoint.py /

# set `/data` as working directory so that the output is written to the
# mount point when run with `docker run -v $PWD:/data ... -o output.csv`
WORKDIR /data

ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "python", "/entrypoint.py"]
