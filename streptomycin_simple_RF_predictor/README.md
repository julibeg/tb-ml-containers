# Simple Random Forest example container predicting Mtb resistance against streptomycin

This container holds a random forest model trained on Mtb variants in order to predict resistance against streptomycin. It can be queried to give the list of variants required for prediction (see usage examples below). The workdir in the container is `/data` which is also where the output file will be generated (and thus it needs to be mounted as a volume on the host).

## Usage examples

### Getting the target variants necessary for prediction

This will create `target-vars.csv` with the list of variants required for
prediction and their allele frequencies in the training dataset (so that
non-calls can be replaced by the allele frequency of the corresponding variant).
The columns of the CSV will be `POS,REF,ALT,AF`.

```bash
docker run -v $PWD:/data \
    julibeg/tb-ml-simple-rf-predictor-streptomycin:v0.3.0 \
    --get-target-vars -o target-vars.csv
```

### Prediction

The container expects a CSV with the genotypes of the target variants and the
header line `POS,REF,ALT,GT`. The file needs to have the same `POS`, `REF`, and
`ALT` columns as the file written by `--get-target-vars`.

```bash
docker run -v $PWD:/data \
    julibeg/tb-ml-simple-rf-predictor-streptomycin:v0.3.0 \
    my-variants.csv
```
