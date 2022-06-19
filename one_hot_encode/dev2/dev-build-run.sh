#!/bin/bash

name="sambamba-test"

base_dir="$(dirname "$(dirname "$(readlink -f "$0")")")"

docker build -t "$name":latest --rm "$base_dir"

(
    if [[ -n $1 ]] && [[ "singularity" =~ ^$1 ]]; then
        singularity build -F "$name".sif docker-daemon:"$name":latest
        singularity run "$name".sif "$base_dir"/dev/test.csv
    else
        docker run \
            -v "$base_dir/dev":/test \
            "$name":latest \
            -b /test/SRR2100118.bqsr.cram \
            -r /test/H37RV_loci_coords_from_table_in_paper.bed
    fi
) | head -n20