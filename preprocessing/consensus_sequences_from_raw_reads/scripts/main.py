import argparse
import subprocess
import pandas as pd

ref_file = "/internal_data/refgenome.fa"

"""
Entrypoint for a Docker container that generates consensus sequences of M. tuberculosis
raw reads in a list of target regions. It requires the reads, a CSV file with
coordinates of the target regions, and a name for the output FASTA file. `bwa-mem2` is
used for aligning the reads against H37Rv (asm19595v2) and variants are called with
`freebayes`. The CSV file with the target regions is required and should have the header
line 'locus,start,end'.
"""


def check_positive_int(val):
    try:
        val = int(val)
        assert val >= 1
    except (ValueError, AssertionError):
        raise argparse.ArgumentTypeError(
            f"invalid value (must be positive int): '{val}'"
        )
    return val


parser = argparse.ArgumentParser(
    description="""
        Aligns raw reads to the M. tuberculosis H37Rv genome (asm19595v2) and then
        extracts consensus sequences for a list of loci. Expects a FASTQ
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
    help="output FASTA file [required]",
    required=True,
)
# parse arguments
args = parser.parse_args()

# transform targets csv to bed file
targets = pd.read_csv(args.regions, index_col=0)
targets.sub(1).reset_index().eval('locus = "Chromosome"').to_csv(
    "target_loci.bed", index=False, header=False, sep="\t"
)

# run variant-calling pipeline
subprocess.run(
    [
        "/bin/bash",
        "/scripts/variant-calling-pipeline.sh",
        args.forward_reads,
        args.reverse_reads,
        ref_file,
        "target_loci.bed",
        str(args.threads),
    ]
)

# get the consensus sequence for each target locus and write all to multi-fasta file
with open(args.output, "w") as f:
    for locus, (start, end) in targets.iterrows():
        seq = subprocess.run(
            [
                "/bin/bash",
                "/scripts/get-aligned-consensus-sequence.sh",
                ref_file,
                "variants.vcf.gz",
                f"Chromosome:{start}-{end}",
                f"alignment-files/{locus}.fasta",
            ],
            capture_output=True,
            text=True,
        ).stdout
        f.write(f">{locus}\n")
        f.write(seq)
