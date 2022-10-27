# %% ###################################################################
import argparse
import subprocess
import pandas as pd
import numpy as np
import tensorflow as tf
import shutil
import sys
from Bio import SeqIO

"""
Entrypoint for a Docker container holding a convolutional neural network created by
Green et al. (https://doi.org/10.1101/2021.12.06.471431) for predicting resistance of M.
tuberculosis against 13 drugs. Expects a FASTA file with the consensus sequences of 18
target loci of the Mtb strain in question and writes the prediction of resistance status
for the 13 drugs to STDOUT.

Run with `--get-target-loci` to write the target loci in CSV format (with header
'locus,start,end') to the output file (specified with `-o` or `--output`).

Run with the name of the input FASTA file as sole argument to generate the prediction
and write the result to STDOUT.
"""

# mapping to use for one-hot encoding
ONE_HOT_BASE_ORDER = {"A": 0, "C": 1, "T": 2, "G": 3, "-": 4}
# order of loci as expected by the model
LOCUS_ORDER = [
    "acpM-kasA",
    "gid",
    "rpsA",
    "clpC",
    "embCAB",
    "aftB-ubiA",
    "rrs-rrl",
    "ethAR",
    "oxyR-ahpC",
    "tlyA",
    "katG",
    "rpsL",
    "rpoBC",
    "fabG1-inhA",
    "eis",
    "gyrBA",
    "panD",
    "pncA",
]
# order of drugs in the predicted vector of resistance status
DRUGS_ORDER = [
    "RIFAMPICIN",
    "ISONIAZID",
    "PYRAZINAMIDE",
    "ETHAMBUTOL",
    "STREPTOMYCIN",
    "LEVOFLOXACIN",
    "CAPREOMYCIN",
    "AMIKACIN",
    "MOXIFLOXACIN",
    "OFLOXACIN",
    "KANAMYCIN",
    "ETHIONAMIDE",
    "CIPROFLOXACIN",
]
# directory where the alignments are stored (not the complete MSAs but only the
# reference sequence; this is enough for introducing gaps into the target sequences with
# `mafft --add`)
ALIGNMENTS_DIR = "/internal_data/alignments"


# function of Green et al. used for one-hot encoding
# (https://github.com/aggreen/MTB-CNN/blob/d1a30ad7464334460dd807b71ea101d9ef6f5e13/sd_cnn/deeplift/tb_cnn_codebase.py#L47)
def get_one_hot(sequence):
    """
    Creates a one-hot encoding of a sequence
    Parameters
    ----------
    sequence: iterable of str
            Sequence containing only ACTG- characters

    Returns
    -------
    np.ndarray of int
            L (seq len) x 5 one-hot encoded sequence
    """

    seq_len = len(sequence)
    seq_in_index = [ONE_HOT_BASE_ORDER.get(b, b) for b in sequence]
    one_hot = np.zeros((seq_len, 5))

    # Assign the found positions to 1
    one_hot[np.arange(seq_len), np.array(seq_in_index)] = 1

    return one_hot


# parse command line arguments
parser = argparse.ArgumentParser(
    description="""
        A Neural Network classifier to predict M. tuberculosis resistance against 13
        drugs from sequence data (https://doi.org/10.1101/2021.12.06.471431). Expects
        the name of a FASTA file holding sequences of 18 target loci as single argument
        and prints the predictions to STDOUT. Instead of generating the predictions, can
        also be run with '--get-target-loci' to write the (1-based) coordinates of the
        target loci in CSV format to an output file.
        """
)
parser.add_argument(
    "--get-target-loci",
    action="store_true",
    dest="get_target_loci",
    help="write the coordinates of the target loci to the output file and exit",
)
parser.add_argument(
    "file",
    metavar="FILE",
    type=str,
    nargs="?",
    help="input FASTA file with sequences of the 18 target loci",
)
parser.add_argument(
    "-o",
    "--output",
    type=str,
    metavar="FILE",
    help="file to write the target loci to (required with '--get-target-loci')",
)
args = parser.parse_args()
# check if there are conflicting arguments
try:
    if args.get_target_loci:
        assert args.file is None and args.output is not None
        shutil.copyfile("/internal_data/target_loci.csv", args.output)
        sys.exit(0)
    else:
        assert args.file is not None and args.output is None
except AssertionError:
    parser.error(
        "Either provide a single FASTA file to generate predictions or call with "
        "'--get-target-loci' and an output file to get the coordinates of the target "
        "loci."
    )

# we need to add the individual sequences to the alignments used in training with
# `mafft --add input_seq.fa --keeplength MSA.fa` in order to make sure that gaps are at
# the right positions etc. --> read the input FASTA first
input_seqs = list(SeqIO.parse(args.file, "fasta"))
# make sure the input contains a sequence for each target locus
if set(r.id for r in input_seqs) != set(LOCUS_ORDER):
    raise ValueError("Sequence IDs in input FASTA not matching target loci")

# now, for each input sequence use mafft to add it to the corresponding alignment in
# order to introduce the gaps and one-hot-encode the resulting sequence
one_hot_seqs = {}
for seq in input_seqs:
    alignment_file = f"{ALIGNMENTS_DIR}/{seq.id}.fasta"
    SeqIO.write(seq, "input-seq.fa", "fasta")
    aligned_seq = "".join(
        subprocess.run(
            [
                "/bin/bash",
                "/scripts/add-to-alignment-with-mafft-and-get-aligned-sequence.sh",
                "input-seq.fa",
                alignment_file,
            ],
            capture_output=True,
            text=True,
        ).stdout.split()
    )
    one_hot_seqs[seq.id] = get_one_hot(aligned_seq.upper())

# make sure that the length of longest sequence is as expected
assert (
    max(len(x) for x in one_hot_seqs.values()) == 10291
), "Longest aligned sequence has unexpected length"

# combine one-hot-encoded sequences into single np.array of dimensions (1, 5, 10291, 18)
# while making sure that the order is as expected by the model
X = np.zeros((1, 5, 10291, 18))
for i, locus in enumerate(LOCUS_ORDER):
    one_hot_seq = one_hot_seqs[locus]
    X[0, :, : len(one_hot_seq), i] = one_hot_seq.T

# now load the model and predict resistance
m = tf.keras.models.load_model("/internal_data/MDCNN_saved_model", compile=False)
pred = m.predict(X).ravel()
# Green et al. encoded resistance as `0` and susceptibility as `1` --> reverse
res = pd.Series(1 - pred, index=DRUGS_ORDER)
# determine resistance status ('R', or 'S') and write result to STDOUT
res = pd.concat((res, res.apply(lambda x: "R" if x > 0.5 else "S")), axis=1)
res.index.name = "drug"
res.columns = ["prediction", "resistance_status"]
res.to_csv(sys.stdout)
