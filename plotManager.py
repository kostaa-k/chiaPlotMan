from subprocess import Popen, PIPE, CalledProcessError

import psutil
import utilFunctions
import time
from copy import deepcopy
from plot import Plot

class PlotManager:
    
    def __init__(self, outputDirectories):
        self.runningPlots = []
        self.waitingPlots = []
        self.outputDirectories = outputDirectories

        self.plotsPerOutputLocation = {}
        for outputDirectory in outputDirectories:
            self.plotsPerOutputLocation[outputDirectory] = 0

    def createPlot(self, numPlots, numThreads, ramMB, tempLocation, kSize=31, staggered=False):
        tempPlot = Plot(numPlots, numThreads, ramMB, tempLocation, kSize, staggered)
        self.waitingPlots.append(deepcopy(tempPlot))

        return tempPlot

    def startPlotting(self):
        self.removeFullDirectories()
        while(len(self.outputDirectories) > 0):
            plotToRun = self.waitingPlots.pop()
            self.runPlot(plotToRun)
            self.plotUpdater()
            self.removeFullDirectories()

    def plotUpdater(self):
        while(self.canRunNextPlot() is False):
            time.sleep(120)
            self.updatePlotStages()
            self.outputStatusOfPlots()

    def updatePlotStages(self):
        allPlotsStages = self.getAllPlotStages()

        for key, value in allPlotsStages.items():
            if(value > 4):
                self.finishPlot(key)


    def finishPlot(self, plot):
        del self.runningPlots[self.runningPlots.index(plot)]
        self.createPlot(plot.numPlots, plot.numThreads, plot.ramMB, plot.tempLocation)

    def canRunNextPlot(self):
        if(len(self.waitingPlots) == 0):
            return False

        for key, value in self.getAllPlotStages().items():
            if(value == 1):
                return False

        return True
        
    def outputStatusOfPlots(self):
        for key, value in self.getAllPlotStages.items():
            print(key.tempLocation, " at Stage: ", value)

    def getAllPlotStages(self):
        plotStagesDict = {}
        for tempPlot in self.runningPlots:
            plotStagesDict[tempPlot] = self.getPlotStage(tempPlot)

        return plotStagesDict

    def selectOutputDirectory(self):
        self.removeFullDirectories()
        minPlots = 100
        outputDirectory = None
        for key, value in self.plotsPerOutputLocation.items():
            if(value < minPlots):
                outputDirectory = key
                minPlots = value

        return outputDirectory 

    def removeFullDirectories(self):
        spaceOutputDirectories = []
        for outputDirectory in self.outputDirectories:
            if(utilFunctions.get_free_space_gb(outputDirectory) > 300):
                spaceOutputDirectories.append(outputDirectory)
            else:
                del self.plotsPerOutputLocation[outputDirectory]
       
        self.outputDirectories = []
        self.outputDirectories = deepcopy(spaceOutputDirectories)

    def runPlot(self, plot):
        if(self.selectOutputDirectory is not None):
            plot.finalLocation = self.selectOutputDirectory()
        else:
            raise Exception('runPlot failed: selectOutputDirectory returned null')

        print("command str: ", plot.getCommandStr())
        p = Popen(plot.getCommandStr(), stdout=PIPE, bufsize=1, universal_newlines=True, shell=True)
        plot.setProcessId(p.pid)
        plot.stage = 1
        self.runningPlots.append(plot)

        time.sleep(5)
        
        return plot

    def getPlotFromId(self, plotId):
        for tempPlot in self.runningPlots:
            if(tempPlot.id == plotId):
                return tempPlot

        return None

    def killPlot(self, plot):
        plot = self.getPlotFromId(plot.id)
        print("kiling Process id: ", plot.processId)
        process = psutil.Process(plot.processId)
        for proc in process.children(recursive=True):
            proc.kill()
        process.kill()

    def getPlotStage(self, plot):
        maxStage = 1
        with open(plot.logLocation, 'r') as infile:
            for cnt, line in enumerate(infile):
                if("starting phase " in line.lower()):
                    tempStage = (int)(line.lower().split("starting phase ")[1][0])
                    if(tempStage > maxStage):
                        maxStage = tempStage

        return maxStage

    def isSpaceOnDrive(self, driveLetter, thresholdGB=300):
        spaceLeft = utilFunctions.get_free_space_mb(utilFunctions.getDiskMountPointFromLetter(driveLetter))
        for runningPlot in self.runningPlots:
            if (runningPlot.getOutputDriveLetter == driveLetter):
                spaceLeft = spaceLeft - runningPlot.finalPlotSize

        return spaceLeft > thresholdGB