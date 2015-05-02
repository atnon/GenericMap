import os
import sys
import re
import argparse
import pprint
import ast
import operator as op

def parseArgs():
    parser = argparse.ArgumentParser(
        description="Extract generic mappings from VHDL file."
        )

    parser.add_argument(
        "infile",
        type=argparse.FileType("r"),
        help="Input file to read."
        )

    parser.add_argument(
        "-c", "--config",
        help="LEON3 Configuration file, usually config.vhd"
    )

    return parser.parse_args()

def dumpData(filename, data):
    with open(filename, "w") as File:
        File.write(data)


operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
             ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
             ast.USub: op.neg}

def eval_expr(expr, firstRun = True, Mode = "integer"):
    """
    If this isn't an ugly hack, then I don't know what is.
    Based on http://stackoverflow.com/a/9558001
    """

    if firstRun:
        HexCheck = re.search(r"16#(.*?)#", expr)
        Mode = "integer"
        if HexCheck != None:
            expr = "0x" + HexCheck.group(1)
            Mode = "hex"
        node = ast.parse(expr, mode='eval').body
    else:
        node = expr

    if isinstance(node, ast.Num): # <number>
        if Mode == "hex":
            return hex(node.n)
        else:
            return node.n
    elif isinstance(node, ast.BinOp): # <left> <operator> <right>
        return operators[type(node.op)](eval_expr(node.left, False, Mode), eval_expr(node.right, False, Mode))
    elif isinstance(node, ast.UnaryOp): # <operator> <operand> e.g., -1
        return operators[type(node.op)](eval_expr(node.operand, False, Mode))
    else:
        if firstRun:
            return expr
        else:
            if Mode == "hex":
                return hex(node.Name)
            else:
                return node.Name


class ParseLEON3:
    """
    Class with stuff to try and parse LEON3-specific constants from config.vhd.
    """
    def __init__(self, InputFile):
        self.InputFile = InputFile

    def readFile(self):
        with open(self.InputFile) as InFile:
            Data = InFile.read()
        return Data

    def parseConfig(self):
        CompiledPattern = re.compile(r"constant\s+?(?P<name>CFG_.*?)\s*?:\s*?integer\s*?:=\s*?(?P<value>.*?);", re.MULTILINE|re.IGNORECASE)

        InputData = self.readFile()
        Matches = CompiledPattern.finditer(InputData)
        ConfigDict = {}
        for Match in Matches:
            MatchDict = Match.groupdict()
            (Name, Value) = (MatchDict["name"], MatchDict["value"])

            ConfigDict.update({Name.strip() : eval_expr(Value.strip())})

        pprint.pprint(ConfigDict)
        return ConfigDict



class ParseGenerics:
    def __init__(self, InputFile, ConfigFile = None):
        self.InputFile = InputFile
        self.ConfigFile = ConfigFile

        if self.ConfigFile:
            self.ConfParser = ParseLEON3(self.ConfigFile)
            self.ConfigDict = self.ConfParser.parseConfig()

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
            ArgNum = len(List)
            if ArgNum == 2:
                (Key, Value) = List
            else:
                (Key, Value) = (GenericCounter, List[0])

            if self.ConfigDict and re.search(r"(CFG_.*?)", Value):
                CfgVal = self.ConfigDict.get(Value)
                if CfgVal != None:
                    if ArgNum == 2:
                        Value = str(CfgVal)
                    else:
                        Value = Value +"="+ str(CfgVal)

            GenericDict.update({Key : Value})
            GenericCounter = GenericCounter + 1
        return GenericDict


    def parseVHDL(self):
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

        InputData = self.readFile()
        CleanedData = " ".join(InputData.split())
        Matches = CompiledPattern.finditer(CleanedData)
        ComponentDict = {}
        for match in Matches:
            MatchDict = match.groupdict()
            ParsedGenerics = self.parseGenMap(MatchDict["Generics"])
            if ParsedGenerics.get("paddr"):
                # Unit is on APB bus.
                Bus = "APB"
            elif ParsedGenerics.get("haddr"):
                Bus = "AHB"
            else:
                Bus = None
            if ParsedGenerics.get("tech") != "padtech":
                ComponentDict.update({
                    MatchDict["InstName"] :
                        {
                            "Bus" : Bus,
                            "CompName" : MatchDict["CompName"],
                            "Comment" : MatchDict["Comment"],
                            "LibName" : MatchDict["LibName"],
                            "Generics" : ParsedGenerics
                        }
                    })
        pprint.pprint(ComponentDict)

if __name__ == "__main__":
    args = parseArgs()
    parser = ParseGenerics(args.infile, args.config)
    parser.parseVHDL()
