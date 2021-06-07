import uuid
import os

class Plot:
    

    kSizeDict = {31: 1, 32: 108, 33: 256}

    def __init__(self, numThreads, ramMB, tempLocation , kSize=32, staggered=False):
        self.processId = ""
        self.stage = 0
        self.finalLocation = ""
        self.tempLocation = tempLocation
        self.ramMB = ramMB
        self.numThreads = numThreads
        self.id = (str)(uuid.uuid4())
        self.kSize = kSize
        self.logLocation = os.path.dirname(os.path.realpath(__file__))+"\\logs\\"+self.id+".txt"
        self.finalPlotSize = self.kSizeDict[kSize]
        

    def getCommandStr(self, isTesting=False):
        commandStr = "chia plots create -k "+(str)(self.kSize)+" -b "+(str)(self.ramMB)+" -t "+self.tempLocation+" -d "+self.finalLocation+" -r "+(str)(self.numThreads)
        if(isTesting):
            commandStr = commandStr+" --override-k"
        return commandStr+" > "+self.logLocation

    def setProcessId(self, processId):
        self.processId = processId

    def getOutputDriveLetter(self):
        return self.finalLocation[0]