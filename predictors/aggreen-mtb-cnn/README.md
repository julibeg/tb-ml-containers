# Docker container holding a convolutional neural network (CNN) for predicting antimicrobial resistance against 13 drugs from consensus sequences of _Mycobacterium tuberculosis_

The [model](https://github.com/aggreen/MTB-CNN) was taken from [Green & Yoon et al., Nat Comms (2022)](https://doi.org/10.1038/s41467-022-31236-0).

The start and end coordinates of the 13 target loci can be found in `data_files/target_loci.csv` or queried from the container by passing the `--get-target-loci` argument (see below). Consensus sequences from raw reads can be created with [this Docker container](https://github.com/julibeg/tb-ml-containers/tree/main/preprocessing/consensus_sequences_from_raw_reads)

## Example usage

Get coordinates of target loci

```bash
docker run -v $PWD:/data \
    julibeg/tb-ml-aggreen-mtb-cnn:v0.1.0 \
    --get-target-loci \
    -o nn_target_loci.csv
```

Predict resistance against 13 drugs from target consensus sequences (passed as FASTA file)

```bash
docker run -v $PWD:/data \
    julibeg/tb-ml-aggreen-mtb-cnn:v0.1.0 \
    input_seqs.fa
```
