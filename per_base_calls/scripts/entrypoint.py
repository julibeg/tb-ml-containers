import argparse
import subprocess as sp

def main(args):
    """
    Main entrypoint for the per_base_calls script.
    """
    sp.call(["samtools","index","-@","1",args.bam])
    print("Chr,Pos,A,C,G,T,N")
    for l in sp.Popen(["sambamba","depth","base","-L",args.regions,args.bam],stdout=sp.PIPE).stdout:
        row = l.decode("utf-8").strip().split("\t")
        if row[0]=="REF": continue
        acgtx = [int(x) for x in row[3:8]]
        acgtx_bin = [0,0,0,0,0]
        acgtx_bin[acgtx.index(max(acgtx))] = 1
        result = ["Chromosome",int(row[1])+1]+acgtx_bin
        print(",".join([str(x) for x in result]))
    

parser = argparse.ArgumentParser(description='add required annotations',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--bam',default="/data/aligned_reads",type=str,help='BAM file')
parser.add_argument('--regions',default="/data/regions.bed",type=str,help='Regions bed file')
parser.set_defaults(func=main)
args = parser.parse_args()
args.func(args)
