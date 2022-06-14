import tensorflow as tf
import pandas as pd
import sys
import argparse

tf.get_logger().setLevel('ERROR')

parser = argparse.ArgumentParser(
    description="""
        A Neural Network classifier to predict Mtb resistance to 13 drugs from sequence
        data. Expects the name of a CSV file with the one hot-encoded sequence data
        (with columns A, C, G, T) as single argument.
        """
)
parser.add_argument(
    "file",
    metavar="FILE",
    type=str,
    nargs="?",
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

m = tf.keras.models.load_model("/model", compile=False)

input = pd.read_csv(args.file)
assert list(input.columns) == list('ACGT'), "Input file must have columns A, C, G, T."

res = pd.Series(
    tf.sigmoid(m.predict(tf.expand_dims(input, 0))).numpy().flatten(), index=drugs
)

res.to_csv(sys.stdout, index_label="drug", header=["probability"])
