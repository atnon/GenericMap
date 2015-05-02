import os
import sys
import re
import argparse

CompiledPattern = re.compile(
    # An almost retardedly complex RegEx.
    # Would probably be better off with a proper parser,
    # if I knew how to construct one.
    r"""
    (?P<InstName>[a-z0-9_]+)        # Component instatiation name
    (?:\s|\n)*:(?:\s|\n)*
    (?:entity(?:\s|\n)*(?P<LibName>.*?)\.)?(?P<CompName>[a-z0-9_]+)    # Component name
    (?:\s|\n)*(?:--(?P<Comment>.*?))?(?:\s|\n)+                       # Possible comment
    generic\smap(?:\s|\n)*\(                   # Start of generic map
    (?P<Generics>.*?)                               # Generic stuff.
    \)(?!\s*=)                          # End of generic map
    """, re.MULTILINE|re.IGNORECASE|re.VERBOSE)

def parseArgs():
    parser = argparse.ArgumentParser(
        description="Extract generic mappings from VHDL file."
        )

    parser.add_argument(
        "infile",
        type=argparse.FileType("r"),
        help="Input file to read."
        )

    return parser.parse_args()

def dumpData(filename, data):
    with open(filename, "w") as File:
        File.write(data)

class ParseGenerics:
    def __init__(self, InputFile):
        self.InputFile = InputFile

    def readFile(self):
        with self.InputFile as InFile:
            Data = InFile.read()
        return Data

    def parseVHDL(self):
        InputData = self.readFile()
        CleanedData = " ".join(InputData.split())
        Matches = CompiledPattern.findall(CleanedData)
        for match in Matches:
            print match

if __name__ == "__main__":
    args = parseArgs()
    parser = ParseGenerics(args.infile)
    parser.parseVHDL()
