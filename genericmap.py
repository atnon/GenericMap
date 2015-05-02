import os
import sys
import re
import argparse
import pprint

"""
An almost retardedly complex RegEx.
Would probably be better off with a proper parser,
if I knew how to construct one.
Available matching groups:
- InstName
- LibName
- CompName
- Comment
- Generics
"""
CompiledPattern = re.compile(
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

    def parseGenMap(self, generics):
        GenericList = generics.split(",")
        GenericDict = {}

        GenericCounter = 0
        for genericTuple in GenericList:
            List = map(str.strip, genericTuple.split("=>"))
            if len(List) == 2:
                (Key, Value) = List
                GenericDict.update({Key : Value})
            else:
                GenericDict.update({GenericCounter : List[0]})
            GenericCounter = GenericCounter + 1
        return GenericDict


    def parseVHDL(self):
        InputData = self.readFile()
        CleanedData = " ".join(InputData.split())
        Matches = CompiledPattern.finditer(CleanedData)
        ComponentDict = {}
        for match in Matches:
            MatchDict = match.groupdict()
            ParsedGenerics = self.parseGenMap(MatchDict["Generics"])
            if ParsedGenerics.get("tech") != "padtech":
                ComponentDict.update({
                    MatchDict["InstName"] :
                        {
                            "CompName" : MatchDict["CompName"],
                            "Comment" : MatchDict["Comment"],
                            "LibName" : MatchDict["LibName"],
                            "Generics" : ParsedGenerics
                        }
                    })
        pprint.pprint(ComponentDict)

if __name__ == "__main__":
    args = parseArgs()
    parser = ParseGenerics(args.infile)
    parser.parseVHDL()
