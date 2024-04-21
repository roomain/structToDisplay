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


def writeCallDisplay(file, description, prefix, variable):
    file.write("{}a_displayer.pushCategory(\"{}\");\n".format(prefix, description))
    file.write("{}display(a_displayer, {});\n".format(prefix, variable))
    file.write("{}a_displayer.popCategory();\n".format(prefix))

def writeValue(file, description, variable, prefix, isPointer, isEnum, isFlag, type, structList) :
    if isPointer :
        #typeDef = re.search("(.*)\\*", type).group(1)
        file.write("{}//Pointer : a_displayer.setCapability(\"{}\", {});\n".format(prefix, description, variable))
    elif isEnum :
        file.write("{}a_displayer.setCapability(\"{}\", to_string({}));\n".format(prefix, description, variable))
    elif isFlag :
        typFlag = re.search("(.*)Flags", type).group(1) + "FlagBits"
        file.write("{}a_displayer.setCapability(\"{}\", Flag<{}>::to_string({}));\n".format(prefix, description, typFlag, variable))
    elif type in  structList:
        writeCallDisplay(file, description, prefix, variable)
    else:
        file.write("{}a_displayer.setCapability(\"{}\", {});\n".format(prefix, description,  variable))

def writeValueTable(file, description, variable, prefix, isPointer, isEnum, isFlag, type, structList) :
    file.write("{}for(const auto propVal : {})\n".format(prefix, variable))
    file.write("{}".format(prefix))
    file.write("{\n")
    prefixAux = prefix + "\t"
    writeValue(file, description, "propVal", prefixAux, isPointer, isEnum, isFlag, type, structList)
    file.write("{}".format(prefix))
    file.write("}\n\n")



def displayLine(line, file, structList, enumList) :
    isTable = "[" in line
    if isTable :
        variable = re.search(".*\\s(.*)\\[.*;", line).group(1)
    else :
        variable = re.search(".*\\s(.*);", line).group(1)
    typeVar = re.search("(.*)\\s(.*);", line).group(1).strip()
    isEnum = typeVar in enumList
    isFlag = typeVar.endswith("Flags")
    isPointer = typeVar.endswith('*')
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
    variableName = "a_prop.{}".format(variable)
    if isTable:
        writeValueTable(file, description, variableName, "\t", isPointer, isEnum, isFlag, typeVar, structList)
    else :
        writeValue(file, description, variableName, "\t", isPointer, isEnum, isFlag, typeVar, structList)


structList = []
enumList = []
inputfile = ParsedFile(sys.argv[1])
outputfile = open(sys.argv[2], 'w')
isStruct = False
while not inputfile.atEnd() :
    line = inputfile.nextTrimmedLine()
    if "#define" in line:
        continue
    elif "typedef enum" in line:
        enumList.append( re.search(".*enum\\s(.+)\\s{.*", line).group(1))
    elif "typedef struct" in line :
        isStruct = True
        #print(line)
        structName = re.search(".*struct\\s(.+)\\s{.*", line).group(1)
        structList.append(structName)
        outputfile.write("void display(IRHICapabilitiesDisplayer& a_displayer, const {}& a_prop)\n".format(structName))
        outputfile.write("{\n")
    elif "}" in line:
        if isStruct :
            outputfile.write("}\n\n")
        isStruct = False
    elif isStruct :
        displayLine(line, outputfile, structList, enumList)



