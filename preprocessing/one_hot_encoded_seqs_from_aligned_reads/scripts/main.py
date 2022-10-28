import argparse
import subprocess
import pandas as pd
import io

"""
Entrypoint for a Docker container which uses `sambamba` to generate one-hot-encoded
sequences from a SAM/BAM file. The start and end coordinates of the sequences are read
from a CSV file (which is required and should have the header line 'locus,start,end').
The sequences are concatenated without any gaps.
"""

parser = argparse.ArgumentParser(
    description="""Extract one-hot-encoded consensus sequences from aligned reads. Needs
                a SAM/BAM file and a CSV file with the coordinates of the regions
                to extract. Writes the output to a CSV file. Providing an output file is
                required."""
)
parser.add_argument(
    "-b",
    "--bam",
    type=str,
    metavar="FILE",
    help="alignment file (SAM/BAM) [required]",
    required=True,
)
parser.add_argument(
    "-r",
    "--regions",
    type=str,
    metavar="FILE",
    help="regions CSV file (with the header 'locus,start,end') [required]",
    required=True,
)
parser.add_argument(
    "-o",
    "--output",
    type=str,
    metavar="FILE",
    help="output file [required]",
    required=True,
)
args = parser.parse_args()

# check if the aligned reads are in a BAM file and create one if not
if not args.bam.endswith(".bam"):
    subprocess.run(
        ["samtools", "view", "-b", "-h", "-o", "reads.bam", args.bam],
    )
    input_reads = "reads.bam"
else:
    input_reads = args.bam
# sort the BAM file
subprocess.run(["samtools", "sort", input_reads, "-o", "reads.sorted.bam"])
# index the sorted BAM file
subprocess.run(["samtools", "index", "reads.sorted.bam"])
# get the name of the reference sequence that was used to generate the SAM/BAM file
ref_seq_name = subprocess.run(
    ["samtools", "idxstats", "reads.sorted.bam"], capture_output=True, text=True
).stdout.split()[0]

# sambamba needs a BED file --> convert the CSV
regions = pd.read_csv(args.regions)
regions["chr"] = ref_seq_name
regions[["start", "end"]] -= 1
regions[["chr", "start", "end", "locus"]].to_csv(
    "regions.bed", index=False, header=False, sep="\t"
)

# now run sambamba and parse the output to produce one-hot encoding
sambamba_output = pd.read_csv(
    io.StringIO(
        subprocess.run(
            ["sambamba", "depth", "base", "-L", "regions.bed", "reads.sorted.bam"],
            capture_output=True,
            text=True,
        ).stdout
    ),
    sep="\t",
    usecols=["REF", "POS", "A", "C", "G", "T", "DEL"],
    index_col=[0, 1],
)
consensus_seq = sambamba_output.idxmax(axis=1)
# drop deletions if there were any
consensus_seq = consensus_seq[consensus_seq != "DEL"]
res = pd.get_dummies(consensus_seq)[["A", "C", "G", "T"]]
res.to_csv(args.output, index=False)
