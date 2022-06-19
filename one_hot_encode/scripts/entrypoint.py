import argparse
import subprocess
import pandas as pd
import os
import io

ref_file = "/internal_data/refgenome.fa"

parser = argparse.ArgumentParser(
    description="TODO",
)
parser.add_argument(
    "-b",
    "--bam",
    type=str,
    help="BAM file",
    required=True,
)
parser.add_argument(
    "-r",
    "--regions",
    type=str,
    help="Regions bed file",
    required=True,
)
args = parser.parse_args()

# check if the aligned reads are in a BAM file and create one if not
if not args.bam.endswith(".bam"):
    subprocess.run(
        ["samtools", "view", "-bT", ref_file, "-o", "reads.bam", args.bam],
    )
    args.bam += ".bam"
else:
    os.rename(args.bam, "reads.bam")
# sort the BAM file
subprocess.run(["samtools", "sort", "reads.bam", "-o", "reads.sorted.bam"])
# index the sorted BAM file
subprocess.run(["samtools", "index", "reads.sorted.bam"])

# now run sambamba and parse the output to produce one-hot encoding
sambamba_output = pd.read_csv(
    io.StringIO(
        subprocess.run(
            [
                "sambamba",
                "depth",
                "base",
                "-L",
                "/test/dev/H37RV_loci_coords_from_table_in_paper.bed",
                "/test/dev/reads.sorted.bam",
            ],
            capture_output=True,
            text=True,
        ).stdout
    ),
    sep="\t",
    usecols=["REF", "POS", "A", "C", "G", "T", "DEL"],
    index_col=[0, 1],
)
print(sambamba_output.head())
# res = pd.get_dummies(sambamba_output.idxmax(axis=1)).query("DEL == 0")[
#     ["A", "C", "G", "T"]
# ]
# print(res.head(20).to_csv(index_label=["CHR", "POS"]))
