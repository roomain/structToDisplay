import re
import sys

class BracketCounter:
    start = 0
    end = 0
    def isValid(self):
        return self.start > 0
    def isFinished(self):
        return self.isValid() and (self.start == self.end)

    def count(self, line):
        self.start += line.count('{')
        self.end += line.count('}')

class ParsedFile:
    def __init__(self, file):
        self.file = open(file)
        self.lines = self.file.readlines()
        self.lineCount = len(self.lines)
        self.lineIter = 0

    def nextLine(self):
        if self.lineIter >= self.lineCount:
            return ""
        line = self.lines[self.lineIter]
        self.lineIter += 1
        return line

    def nextTrimmedLine(self):
        return self.nextLine().strip()
    def atEnd(self):
        return self.lineIter >= self.lineCount



def displayLine(line, file, structList) :
    isTable = "[" in line
    if isTable :
        variable = re.search(".*\\s(.*)\\[.*;", line).group(1)
    else :
        variable = re.search(".*\\s(.*);", line).group(1)
    typeVar = re.search("(.*)\\s(.*);", line).group(1).strip()
    variableDescript = variable
    description = ""
    regex = ".+([A-Z]+.+)"
    search = re.search(regex, variableDescript)
    while search is not None :
        description = search.group(1) + " " + description
        variableDescript = re.search("(.+)[A-Z]+.+", variableDescript).group(1)
        search = re.search(regex, variableDescript)
    description = variableDescript + " " + description
    description = description.strip()
    if isTable:
        file.write("\tfor(const auto propVal : a_prop.{})\n".format(variable))
        file.write("\t{\n")
        if typeVar in structList:
            file.write("\t\tdisplay(a_displayer, propVal);\n")
        else:
            file.write("\t\ta_displayer.setCapability(\"{}[]\", propVal);\n".format(description))
        file.write("\t}\n\n")
    else :
        if typeVar in structList:
            file.write("\tdisplay(a_displayer, a_prop.{});\n".format(description, variable))
        else:
            file.write("\ta_displayer.setCapability(\"{}\", a_prop.{});\n".format(description, variable))


structList = []
inputfile = ParsedFile(sys.argv[1])
outputfile = open(sys.argv[2], 'w')
isStruct = False
while not inputfile.atEnd() :
    line = inputfile.nextTrimmedLine()
    if "#define" in line:
        continue
    elif "typedef struct" in line :
        isStruct = True
        print(line)
        structName = re.search(".*struct\\s(.+)\\s{.*", line).group(1)
        structList.append(structName)
        outputfile.write("void display(IRHICapabilitiesDisplayer& a_displayer, const {}& a_prop)\n".format(structName))
        outputfile.write("{\n")
    elif "}" in line:
        if isStruct :
            outputfile.write("}\n\n")
        isStruct = False
    elif isStruct :
        displayLine(line, outputfile, structList)



