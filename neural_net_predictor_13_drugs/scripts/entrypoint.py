import tensorflow as tf
import pandas as pd
import sys
import argparse

# ignore tf warnings
tf.get_logger().setLevel("ERROR")

parser = argparse.ArgumentParser(
    description="""
        A Neural Network classifier to predict Mtb resistance against 13 drugs from
        sequence data. Expects the name of a CSV file holding the one hot-encoded
        sequence data (with columns A, C, G, T) as single argument.
        """
)
parser.add_argument(
    "file",
    metavar="FILE",
    type=str,
    nargs=1,
    help="Input CSV file with one hot-encoded sequence data [required]",
)
args = parser.parse_args()

drugs = [
    "AMIKACIN",
    "CAPREOMYCIN",
    "CIPROFLOXACIN",
    "ETHAMBUTOL",
    "ETHIONAMIDE",
    "ISONIAZID",
    "KANAMYCIN",
    "LEVOFLOXACIN",
    "MOXIFLOXACIN",
    "OFLOXACIN",
    "PYRAZINAMIDE",
    "RIFAMPICIN",
    "STREPTOMYCIN",
]

# load the model
m = tf.keras.models.load_model("/model", compile=False)

# read the input data
input = pd.read_csv(args.file)
if list(input.columns) != list("ACGT"):
    raise ValueError(
        f"Input file must have columns {list('ACGT')}, but has {list(input.columns)}"
    )

# predict
res = pd.Series(
    tf.sigmoid(m.predict(tf.expand_dims(input, 0))).numpy().flatten(), index=drugs
)

# write the result
res.to_csv(sys.stdout, index_label="drug", header=["probability"])
