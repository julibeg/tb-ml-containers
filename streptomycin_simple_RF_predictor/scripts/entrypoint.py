import argparse
import numpy as np
import pandas as pd
import joblib
import sys

"""
Entrypoint for a simple example prediction container with a random forest model fitted
on streptomycin-resistance data. It expects the following arguments: `get_target_vars`
or `predict FILE`. In the first case, it prints the target variants (including AFs in
the training set) to STDOUT so that people can check what format / features the input to
the model should have.
If the arguments are `predict FILE`, it reads genotypes from the file, runs the
prediction, and then prints the predicted resistance status to STDOUT.
"""

parser = argparse.ArgumentParser(
    description="""
        A Random Forest classifier to predict Mtb resistance to streptomycin from a
        CSV with variants in the format 'POS,REF,ALT,GT'. Either pass 'get_target_vars'
        to get the variants + allele frequencies of the training dataset or pass
        'predict' and a filename for predicting resistance.
        """
)
parser.add_argument(
    "option",
    choices=["get_target_vars", "predict"],
    help=(
        "Whether to print the target variants and allele frequencies or read "
        "variants from a file and predict resistance status [required]"
    ),
)
parser.add_argument(
    "file",
    metavar="FILE",
    type=str,
    nargs="?",
    help="Input file for prediction [required if 'predict']",
)
args = parser.parse_args()
if args.option == "predict" and args.file is None:
    parser.error("'predict' needs to be followed by a filename.")
if args.option == "get_target_vars" and args.file is not None:
    parser.error("Don't provide another argument for 'get_target_vars'.")

# get the variants the model has been fitted on
target_vars = pd.read_csv(
    "/internal_data/target_vars.csv", index_col=["POS", "REF", "ALT"]
).squeeze()

# print target variants if requested
if args.option == "get_target_vars":
    sys.stdout.write(target_vars.to_csv())
else:
    # `args.option` has to be 'predict' (argparse would have thrown an error otherwise)
    # and we checked for the presence of an input file name above --> all looks good, we
    # can load the model and predict
    m = joblib.load("/internal_data/model.pkl")
    # load the input variants
    X = pd.read_csv(args.file, index_col=["POS", "REF", "ALT"], comment="#")
    # make sure the dimensions match up and X has only one column
    if X.shape[1] != 1:
        raise ValueError(
            "ERROR: The input variants need to be provided in the format "
            "'POS,REF,ALT,GT' with a header line."
        )
    # make sure the variant order is as expected
    X = X.loc[target_vars.index]
    # the model was fitted on a genotype matrix that had feature names of the format:
    # `POS_REF_ALT` --> create a corresponding index (sklearn will throw a warning
    # otherwise)
    X.index = ["_".join(str(x) for x in idx) for idx in X.index]
    # the model expects a DataFrame with a single row --> transpose
    X = X.T
    # predict the probability for resistance and print the result
    ypred = m.predict_proba(X)[:, 1]
    print(np.squeeze(ypred))
