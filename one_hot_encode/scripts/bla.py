import argparse
import pandas as pd
import io
import subprocess
import os

# now run sambamba and parse the output
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
res = pd.get_dummies(sambamba_output.idxmax(axis=1)).query("DEL == 0")[
    ["A", "C", "G", "T"]
]
print(res.head(20).to_csv(index_label=["CHR", "POS"]))
