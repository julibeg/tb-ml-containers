import argparse
import subprocess
import pandas as pd
import io
import os

ref_file = "/internal_data/refgenome.fa"

"""
Entrypoint for a Docker container which uses `sambamba` to generate one-hot-encoded
sequences from raw reads (after aligning them to a reference with `bwa-mem2`). The start
and end coordinates of the sequences are read from a CSV file (which is required and
should have the header line 'locus,start,end'). The sequences are concatenated without
any gaps.
"""

parser = argparse.ArgumentParser(
    description="""
        Aligns raw reads to the M. tuberculosis H37Rv genome (asm19595v2) and then
        extracts one-hot-encoded consensus sequences for a list of loci. Expects a FASTQ
        file and a CSV file with the 1-based coordinates of the regions to extract.
        Writes the output to a CSV file. Providing a filename for the output file is
        required.
        """
)
parser.add_argument(
    "forward_reads",
    type=str,
    metavar="FASTQ_FILE_FW",
    help="forward reads [required]",
)
parser.add_argument(
    "reverse_reads",
    type=str,
    metavar="FASTQ_FILE_REV",
    help="reverse reads [required]",
)


def check_positive_int(val):
    try:
        val = int(val)
        assert val >= 1
    except (ValueError, AssertionError):
        raise argparse.ArgumentTypeError(
            f"invalid value (must be positive int): '{val}'"
        )
    return val


parser.add_argument(
    "-t",
    "--threads",
    type=check_positive_int,
    metavar="INT",
    help="number of threads to use",
    default=1,
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
# parse arguments
args = parser.parse_args()

# trim reads
subprocess.run(
    [
        "trimmomatic",
        "PE",
        "-threads",
        str(args.threads),
        "-phred33",
        "-baseout",
        "./trimmed",
        args.forward_reads,
        args.reverse_reads,
        "LEADING:3",
        "TRAILING:3",
        "SLIDINGWINDOW:4:20",
        "MINLEN:36",
    ]
)

# mapping
subprocess.run(
    [
        "bash",
        "/mapping-pipeline.sh",
        "trimmed_1P",
        "trimmed_2P",
        "/internal_data/refgenome.fa",
        str(args.threads),
    ]
)

# sambamba needs a BED file --> convert the CSV
regions = pd.read_csv(args.regions)
regions["chr"] = "Chromosome"
regions[["start", "end"]] -= 1
regions[["chr", "start", "end", "locus"]].to_csv(
    "regions.bed", index=False, header=False, sep="\t"
)

# now run sambamba and parse the output to produce the one-hot encoding
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

# clean up
for file in [
    "trimmed_1P",
    "trimmed_1U",
    "trimmed_2P",
    "trimmed_2U",
    "reads.sorted.bam",
    "reads.sorted.bam.bai",
    "regions.bed",
]:
    os.remove(file)
