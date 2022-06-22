import tensorflow as tf
import pandas as pd
import sys
import argparse

"""
This is the entrypoint script for a Docker container holding a neural network that
predicts resistance of an M. tuberculosis sample against 13 drugs (Amikacin Capreomycin,
Ciprofloxacin, Ethambutol, Ethionamide, Isoniazid, Kanamycin, Levofloxacin,
Moxifloxacin, Ofloxacin, Pyrazinamide, Rifampicin, Streptomycin) from one-hot-encoded
sequence data covering the following loci:

acpM-kasA:2517695-2519365
gid:4407528-4408334
rpsA:1833378-1834987
clpC:4036731-4040937
embCAB:4239663-4249810
aftB-ubiA:4266953-4269833
rrs-rrl:1471576-1477013
ethAR:4326004-4328199
oxyR-ahpC:2725477-2726780
tlyA:1917755-1918746
katG:2153235-2156706
rpsL:781311-781934
rpoBC:759609-767320
fabG1-inhA:1672457-1675011
eis:2713783-2716314
gyrBA:4997-9818
panD:4043041-4045210
pncA:2287883-2289599

It expects a CSV file containing the one-hot-encoded sequences with ['A', 'C', 'G', 'T']
as columns.
"""

# ignore tf warnings
tf.get_logger().setLevel("ERROR")

parser = argparse.ArgumentParser(
    description="""
        A Neural Network classifier to predict Mtb resistance against 13 drugs from
        sequence data. Expects the name of a CSV file holding the one hot-encoded
        sequences (with columns A, C, G, T) as single argument.
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
# argparse stores positional arguments in lists, even if it's only one --> unpack
(args.file,) = args.file

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
m = tf.keras.models.load_model("/internal_data/model", compile=False)

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

res = pd.concat((res, res.apply(lambda x: 'R' if x > 0.5 else 'S')), axis=1)
# write the result
res.to_csv(sys.stdout, header=False)
