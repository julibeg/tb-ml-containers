# Docker container holding a neural network (NN) for predicting antimicrobial resistance against 13 drugs from one-hot-encoded sequences of _Mycobacterium tuberculosis_

The NN was trained using data from [MTB-CNN](https://github.com/aggreen/MTB-CNN) and uses a similar architecture with the distinction that no multi-sequence alignment is needed (for more details see [here](https://github.com/julibeg/TB-AMR-CNN)). Instead, it requires only the one-hot-encoded sequences of the relevant loci from a particular sample.

The start and end coordinates of the loci can be found in `data_files/target_loci.csv` or queried from the container by passing the `--get-target-loci` argument (see below). If you have a SAM/BAM file with reads aligned against H37Rv, you can use this [Docker container](https://github.com/julibeg/tb-ml-containers/tree/main/preprocessing/one_hot_encoded_seqs_from_aligned_reads) to extract the one-hot-encoded sequences. There is also a [container to create consensus sequences of the target loci from raw reads](https://github.com/julibeg/tb-ml-containers/tree/main/preprocessing/one_hot_encoded_seqs_from_raw_reads).

## Example usage

Get coordinates of target loci

```bash
docker run -v $PWD:/data \
    julibeg/tb-ml-neural-net-from-one-hot-encoded-seqs-13-drugs:v0.7.0 \
    --get-target-loci \
    -o nn_target_loci.csv
```

Predict resistance against 13 drugs from one-hot-encoded sequences (passed in a CSV file)

```bash
docker run -v $PWD:/data \
    julibeg/tb-ml-neural-net-from-one-hot-encoded-seqs-13-drugs:v0.7.0 \
    input_seqs.csv
```
