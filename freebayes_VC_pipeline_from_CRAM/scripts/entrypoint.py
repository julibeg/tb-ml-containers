import pandas as pd
import argparse
import subprocess
import sys
import io

"""
Entrypoint for a Docker container holding a simple variant calling pipeline: Parses
arguments and then calls a shell script containing the pipeline. Expects the name of a
sorted BAM/CRAM file with M. tuberculosis reads aligned against the reference strain
H37Rv (ASM19595v2) and a CSV file with target variants (i.e. variants for which we want
genotypes) in the format `POS,REF,ALT,AF`. This CSV file should also hold allele
frequencies in the last column which are used to replace missing genotypes / non-calls.
The container writes the called variants in the format `POS,REF,ALT,GT` to the output
file. It will also print some simple stats (e.g. the number of missing variants,
noncalls, etc.) to STDOUT.
"""

parser = argparse.ArgumentParser(
    description="""
    Variant calling pipeline accepting a sorted BAM/CRAM file with reads aligned against
    the M. tyberculosis reference genome H37Rv (ASM19595v2) and a CSV of target variants
    (and allele frequencies) in the format `POS,REF,ALT,AF` as input. Calls the
    genotypes specified in the CSV and replaces missing genotypes / noncalls with the
    corresponding allele frequencies. Writes some basic stats to STDOUT and the variants
    as `POS,REF,ALT,GT` to the output file (specified by '-o').
    """,
)
parser.add_argument(
    "-b",
    "--bam",
    type=str,
    required=True,
    help="Sorted BAM/CRAM file of reads aligned against a reference [required]",
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
    "-o",
    "--output",
    type=str,
    required=True,
    metavar="FILE",
    help="File to write the called variants to [required]",
)
parser.add_argument(
    "--DP-threshold",
    type=int,
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
try:
    variants = pd.read_csv(
        io.StringIO(
            (
                p := subprocess.run(
                    ["/bin/bash", "/get_genotypes.sh", args.bam, args.target_vars],
                    capture_output=True,
                    text=True,
                )
            ).stdout
        ),
        index_col=["POS", "REF", "ALT"],
    )
except pd.errors.EmptyDataError:
    raise RuntimeError(f"No variants produced by pipeline. Error?\n{p.stderr}")
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

# write to the variants to the output file and the stats to STDOUT
variants.name = "GT"
variants.to_csv(args.output)
stats.to_csv(sys.stdout, header=False)
