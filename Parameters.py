# Parameters.py
#
# Written by Larry Holder (holder@wsu.edu).
#
# Copyright (c) 2017. Washington State University.

import os

class Parameters:

    def __init__(self):
        # User-defined parameters
        self.inputFileName = ""       # Store name of input file
        self.outputFileName = ""      # Same as inputFileName, but with .json removed from end if present
        self.beamWidth = 4            # Number of substructures to retain after each expansion of previous substructures; based on value.
        self.iterations = 1           # Iterations of Subdue's discovery process. If more than 1, Subdue compresses graph with best substructure before next run. If 0, then run until no more compression (i.e., set to |E|).
        self.limit = 0                # Number of substructures considered; default (0) is |E|/2.
        self.maxSize = 0              # Maximum size (#edges) of a substructure; default (0) is |E|/2.
        self.minSize = 1              # Minimum size (#edges) of a substructure; default is 1.
        self.numBestSubs = 3          # Number of best substructures to report at end; default is 3.
        self.prune = False            # Remove any substructures that are worse than their parent.
        self.valueBased = False       # Retain all substructures with the top beam best values.
        self.writeCompressed = False  # Write compressed graph after iteration i to file inputFileName-cmp-i.json
        self.writeSub = False         # Write best substructure at iteration i to file inputFileName-sub-i.json
        self.writeInsts = False       # Write instances of best substructure at iteration i as one graph to file inputFileName-insts-i.json
        self.temporal = False         # Discovery static (False) or temporal (True) patterns
    
    def set_parameters (self, args):
        """Set parameters according to given command-line args list."""
        self.inputFileName = args[-1]
        filename, file_extension = os.path.splitext(self.inputFileName)
        if (file_extension == '.json'):
            self.outputFileName = filename
        else:
            self.outputFileName = self.inputFileName
        index = 1
        numArgs = len(args)
        while index < (numArgs - 1):
            optionName = args[index]
            if optionName == "--beam":
                index += 1
                self.beamWidth = int(args[index])
            if optionName == "--iterations":
                index += 1
                self.iterations = int(args[index])
            if optionName == "--limit":
                index += 1
                self.limit = int(args[index])
            if optionName == "--maxsize":
                index += 1
                self.maxSize = int(args[index])
            if optionName == "--minsize":
                index += 1
                self.minSize = int(args[index])
            if optionName == "--numsubs":
                index += 1
                self.numBestSubs = int(args[index])
            if optionName == "--prune":
                self.prune = True
            if optionName == "--valuebased":
                self.valueBased = True
            if optionName == "--writecompressed":
                self.writeCompressed = True
            if optionName == "--writesub":
                self.writeSub = True
            if optionName == "--writeinsts":
                self.writeInsts = True
            if optionName == "--temporal":
                self.temporal = True
            index += 1
        
