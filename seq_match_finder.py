# CSC 480 Assignment 2
# Nick Frogley
# 2/3/18
#
# Gets information about direct matches for a target sequence in a provided
# FASTA file of sequences and writes it to a CSV file

from Bio import SeqIO # to parse sequence data
from Bio.Seq import Seq
import sys
import os

import owcheck      # custom module

# this class stores info about a match we find and allows for it to be
# printed or returned as a CSV row string
class MatchRecord :

    id_str = ""         # the id from the FASTA record
    match_pos = 0       # the index of the match in the sequence (starts at 0)
    strand = -1         # strand; 0 = original, 1 = reverse complement
    upstream_str = ""   # the sequence 200 bp upstream from the match (if 200 bp upstream exists)

    # set values
    def __init__(self, new_id, new_pos, new_strand, new_upstream = "") :    
        self.id_str = new_id
        self.match_pos = new_pos
        self.strand = new_strand
        self.upstream_str = new_upstream
        self.upstream_len = len(self.upstream_str)
        
    # print values
    def printValues(self) :
        print("ID: " + self.id_str)
        print("POSITION: " + str(self.match_pos + 1))
        if (self.strand == 0) :
            print("FOUND IN ORIGINAL")
        else :
            print("FOUND IN REVERSE COMPLEMENT")
        print("UPST LENGTH: " + self.upstream_len)
        print("UPSTREAM (first 100bp): " + self.upstream_str[:100:])
        

    # return values as CSV row
    def getCSV(self) :
        csv_str =   self.id_str + ","
        csv_str +=  str(self.match_pos + 1) + ","
        if (self.strand == 0) :
            csv_str += "ORIGINAL" + ","
        else :
            csv_str += "REVERSE COMPLEMENT" + ","
        csv_str += str(self.upstream_len) + ","
        csv_str += self.upstream_str
        return csv_str

# this class stores info about an alignment
class AlignmentRecord :

    id_str = ""         # the id from the FASTA record
    score = 0           # alignment score
    strand = -1         # strand; 0 = original, 1 = reverse complement
    
    # set values
    def __init__(self, new_id, new_score, new_strand) :    
        self.id_str = new_id
        self.score = new_score
        self.strand = new_strand

    # print values
    def printValues(self) :
        print("ID: " + self.id_str)
        print("SCORE: " + str(self.score))
        if (self.strand == 0) :
            print("FOUND IN ORIGINAL")
        else :
            print("FOUND IN REVERSE COMPLEMENT")

    # return values as CSV row
    def getCSV(self) :
        csv_str =   self.id_str + ","
        csv_str +=  str(self.score) + ","
        if (self.strand == 0) :
            csv_str += "ORIGINAL" + ","
        else :
            csv_str += "REVERSE COMPLEMENT" + ","
        return csv_str

# get matches between target sequences and sequences from a file that are
# in fasta format
def getHits(target_seq, file) :

    # parse sequences in 'fasta' format; this returns an iterator, which stores
    # a sequence of elements
    sequences = SeqIO.parse(file, 'fasta')

    records = list()    # stores our MatchRecord objects (sequence matches)

    target_seq_len = len(target_seq)

    # loop through sequence records in the file
    for s in sequences:
    
        if len(s) < target_seq_len:    
            continue

        # look for a match in the original version of this sequence
        hit_pos = s.seq.find(target_seq)
        if (hit_pos != -1) :    # match found, record it
            upstream = ""
            if hit_pos + target_seq_len + 200 < len(s.seq):
                upstream = s.seq[hit_pos + target_seq_len + 200::]
            records.append(MatchRecord(s.id, hit_pos, 0, str(upstream)))

        # look for a match in the reverse complement of this sequence
        rev_comp = s.seq.reverse_complement()
        hit_pos = rev_comp.find(target_seq)
        if (hit_pos != -1) :    
            upstream = ""
            if hit_pos + target_seq_len + 200 < len(s.seq):
                upstream = s.seq[hit_pos + target_seq_len + 200::]
            records.append(MatchRecord(s.id, hit_pos, 1, str(upstream)))
    print("# matches found:", len(records))
    return records                



def outputRecords(records, file = None, alignments = False) :
    if file == None :
        for r in records :
            r.printValues()        
    else :
        # output matches to CSV file
        outfile = open(file,"w")
        if (alignments == False) :
            outfile.write("ID,POSITION,STRAND,UPST LENGTH,UPSTREAM\n")
        else :
            outfile.write("ID,SCORE,STRAND\n")
        for r in records :
            outfile.write(r.getCSV() + "\n")
        outfile.close();

seq_dict = {}

seq_dict['el1'] = "ccgaggtgagtccggaaatgggctcaaaactgcggtgaaacc".upper()
seq_dict['el2'] = "actgacatccggacagcgttgcgacagtggcgcttttagcgcagcccgggggtttttacaggatacc".upper()        
seq_dict['el3'] = "gtggcgcttttagcgcagcccgggggtttttacaggatacca".upper()
seq_dict['el312'] = "AATTGAGGTGGATCGGTGGATCGGTGGATCAGTTCATTTCGGAACTGAAATGAGCCGTGTCCGAGGTGAGTCCGGAAATGGGCTCAAAACTGCGGTGAAACCACTGACATCCGGACAGCGTTGCGACAGTGGCGCTTTTAGCGCAGCCCGGGGGTTTTTACAGGATACC"


if len(sys.argv) == 3 :
    print("Running with provided args")
    hits = getHits(seq_dict[sys.argv[2]], sys.argv[1])
    input_filename = os.path.split(sys.argv[1])[1]
    output_filename = "matches-" + input_filename + "-" + sys.argv[2] + ".csv"        
    if owcheck.overwriteFile(output_filename) :
        outputRecords(hits, output_filename, False)
else:
    print("Missing args (FASTA file, contig name), running with hardcoded values")
    hits = getHits(seq_dict['el312'], "seqs.fa")
    outputRecords(hits, "direct_matches.csv", False)
