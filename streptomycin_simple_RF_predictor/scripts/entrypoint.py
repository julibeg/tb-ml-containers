import argparse
import pandas as pd
import joblib
import sys

"""
Entrypoint for a simple example prediction container with a random forest model fitted
on streptomycin-resistance data. It expects the following arguments: `--get-target-vars
-o outfile.csv` or `FILE -o outfile.csv`. In the first case, it writes the target
variants (including AFs in the training set) to the output file. In the second case, it
reads genotypes from FILE, runs the prediction, and then writes the predicted resistance
status to the output file (if one was provided) or to STDOUT otherwise.
"""

parser = argparse.ArgumentParser(
    description="""
        A Random Forest classifier to predict Mtb resistance to streptomycin from a CSV
        with variants in the format 'POS,REF,ALT,GT'. Either pass '--get-target-vars' to
        get the variants + allele frequencies of the training dataset (then you need to
        specify an output file with '-o' or '--output') or pass a filename for
        predicting resistance. In the latter case the output file is optional (the
        prediction is written to STDOUT if none is provided).
        """
)
parser.add_argument(
    "--get-target-vars",
    action="store_true",
    dest="get_target_vars",
    help=("Whether to print the target variants + allele frequencies and exit"),
)
parser.add_argument(
    "file",
    metavar="FILE",
    type=str,
    nargs="?",
    help=(
        "CSV file with input data for prediction "
        "(required if '--get-target-vars' was not passed)"
    ),
)
parser.add_argument(
    "-o",
    "--output",
    type=str,
    metavar="FILE",
    help=(
        "File to write the target variants or the prediction result to "
        "(required if '--get-target-vars' was passed; otherwise optional)"
    ),
)
args = parser.parse_args()
if not args.get_target_vars and args.file is None:
    parser.error("Provide a filename or pass '--get-target-vars'.")
if args.get_target_vars and args.file is not None:
    parser.error("Don't provide an input file when passing '--get-target-vars'.")
if args.get_target_vars and args.output is None:
    parser.error("Provide an output file when passing '--get-target-vars'.")

# get the variants the model has been fitted on
target_vars = pd.read_csv(
    "/internal_data/target_vars.csv", index_col=["POS", "REF", "ALT"]
).squeeze()

# write the target variants if requested
if args.get_target_vars:
    with open(args.output, "w") as f:
        f.write(target_vars.to_csv())
else:
    # "--get-target-vars" was not passed and we have an input file (as checked above)
    # --> all looks good, we can load the model and predict
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
    # predict the probability for resistance and write the result
    ypred = pd.Series(m.predict_proba(X)[:, 1], index=["resistance_probability"])
    ypred["resistance_status"] = "S" if ypred["resistance_probability"] < 0.5 else "R"
    ypred.to_csv(args.output or sys.stdout, header=False)
