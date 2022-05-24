import pandas as pd
import argparse
import subprocess
import io

"""
Parses arguments and then calls a Bash script containing a variant calling pipeline.
Expects the name of a BAM file and a CSV file with target variants (i.e. variants for
which we want genotypes) in the format `POS,REF,ALT,AF`. This CSV file also holds allele
frequencies in the last column which are used to replace non-calls later.
Prints the processed variants in the format `POS,REF,ALT,GT` alongside some simple stats
(e.g. the number of missing variants, noncalls, etc.) to STDOUT. The stats are printed
as comments (i.e. prepended by `#`) before printing the variants.
"""

parser = argparse.ArgumentParser(
    description="""
    Variant calling pipeline accepting a BAM file with reads aligned against a reference
    and a CSV of target variants (and allele frequencies) in the format `POS,REF,ALT,AF`
    as input. Calls the genotypes specified in the CSV and replaces missing variants /
    noncalls with the corresponding allele frequencies. Prints some basic stats (as
    header lines starting with `#`) and the variants as `POS,REF,ALT,GT` to STDOUT.
    """,
)
parser.add_argument(
    "-b",
    "--bam",
    type=str,
    required=True,
    help="Sorted BAM file of reads aligned against a reference [required]",
    metavar="FILE",
)
parser.add_argument(
    "-t",
    "--target-vars",
    type=str,
    required=True,
    help="CSV with target variants (and allele frequencies) [required]",
    metavar="FILE",
)
parser.add_argument(
    "--DP-threshold",
    type=int,
    required=False,
    help=(
        "DP threshold (variant calls with lower DP value will be replaced by the "
        "correspoding allele frequency) [default: %(default)d]"
    ),
    default=10,
    metavar="INT",
)

args = parser.parse_args()
# read the data
AFs = pd.read_csv(args.target_vars, index_col=["POS", "REF", "ALT"]).squeeze()
variants = pd.read_csv(
    io.StringIO(
        subprocess.run(
            ["/bin/bash", "/get_genotypes.sh", args.bam, args.target_vars],
            capture_output=True,
            text=True,
        ).stdout
    ),
    index_col=["POS", "REF", "ALT"],
)
# get the first char from the `x/x` genotype field and replace non-calls with NA
variants["GT"] = variants["GT"].apply(lambda x: x[0]).replace(".", pd.NA)
# declare variants with DP < threshold also as non-calls
variants.loc[
    variants["DP"].replace(".", -1).astype(int) < args.DP_threshold, "GT"
] = pd.NA
# collect basic stats on how many variants had to be replaed etc.
stats = pd.Series(dtype=object)
stats["shared_variants"] = len(AFs.index.intersection(variants.index))
stats["dropped_variants"] = len(variants.index.difference(AFs.index))
stats["missing_variants"] = len(AFs.index.difference(variants.index))
stats["noncalls"] = variants["GT"].isna().sum()
stats["variants_set_to_AF"] = stats[["noncalls", "missing_variants"]].sum()
# replace non-calls and missing variants with the corresponding AF values
variants = variants["GT"].fillna(AFs).astype(float)
variants = pd.concat((variants, AFs[AFs.index.difference(variants.index)]))
# make sure the order is as expected by the model
variants = variants[AFs.index]

# write to STDOUT --> first the stats as comments and then the variants
stats_str = stats.to_csv(header=["value"], index_label="parameter")
for line in stats_str.strip().split("\n"):
    print(f"#{line.strip()}")
variants.name = "GT"
print(variants.to_csv(), end="")
