

nameDict = {}

def load_spellcheck_data():
    global nameDict
    with open("Data/TrickNames.txt", 'r') as file:
        for line in file:
            corrected, misspelled = line.strip().split(', ')
            nameDict[corrected] = misspelled
    return nameDict

def check(trick):
    global nameDict
    if trick in nameDict:
        return trick
    else:
        for key,value in nameDict.items():
            if isinstance(value, list): 
                if trick in value:
                    return key
            elif value == trick:
                return key

    return "Not added Yet: " + trick

def checkHeader(header):
    global nameDict
    trick = header[3:]
    config = header[:3]
    if trick in nameDict:
        return config + trick
    else:
        for key,value in nameDict.items():
            if (isinstance(value, list) and trick in value) or value == trick:
                return config + key

    return config + "Not added Yet: " + trick
