from subprocess import Popen, PIPE, CalledProcessError

import os
import psutil
import utilFunctions
import time
from copy import deepcopy
from plot import Plot
import os

class PlotManager:
    
    def __init__(self, outputDirectories, numConcurrentPlots=1):
        self.runningPlots = []
        self.waitingPlots = []
        self.outputDirectories = outputDirectories
        self.numConcurrentPlots = numConcurrentPlots
        self.plotsPerOutputLocation = {}
        self.numFinishedPlots = 0
        for outputDirectory in outputDirectories:
            self.plotsPerOutputLocation[outputDirectory] = 0

    def createPlot(self, numThreads, ramMB, tempLocation, kSize=32, staggered=False):
        tempPlot = Plot(numThreads, ramMB, tempLocation, kSize, staggered)
        self.waitingPlots.append(deepcopy(tempPlot))

        return tempPlot

    def startPlotting(self):
        for tempDir in self.outputDirectories:
            os.system("chia plots add -d "+tempDir)
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

    def getNumPlotsInStageOne(self):
        numPlotsStageOne = 0
        for key, value in self.getAllPlotStages().items():
            if(value == 1):
                numPlotsStageOne = numPlotsStageOne+1

        return numPlotsStageOne


    def finishPlot(self, plot):
        del self.runningPlots[self.runningPlots.index(plot)]
        self.createPlot(plot.numThreads, plot.ramMB, plot.tempLocation, kSize=plot.kSize)
        self.numFinishedPlots = self.numFinishedPlots+1

    def canRunNextPlot(self):
        if(len(self.waitingPlots) == 0):
            return False

        if(self.getNumPlotsInStageOne() >= self.numConcurrentPlots):
            return False

        return True
        
    def outputStatusOfPlots(self):
        utilFunctions.clearCommandLine()
        print()
        print("Running Plots: ", len(self.runningPlots))
        print()
        for key, value in self.getAllPlotStages().items():
            print(key.tempLocation, " at Stage: ", value, "Plot Process id: ", key.processId)

        print()
        print()
        print("Plots per output directories: ", self.getPlotsPerOutputLocation())
        print("Num of waiting plots: ", len(self.waitingPlots))
        print("Num of finished plots: ", self.numFinishedPlots)
        print("Output directories: ", self.outputDirectories)


    def getAllPlotStages(self):
        plotStagesDict = {}
        for tempPlot in self.runningPlots:
            plotStagesDict[tempPlot] = self.getPlotStage(tempPlot)

        return plotStagesDict

    def getPlotsPerOutputLocation(self):

        plotsDirectoryDict = {}

        for tempDir in self.outputDirectories:
            plotsDirectoryDict[tempDir]= 0

        for tempPlot in self.runningPlots:
            if(tempPlot.finalLocation in plotsDirectoryDict):
                plotsDirectoryDict[tempPlot.finalLocation] = plotsDirectoryDict[tempPlot.finalLocation]+1

        return plotsDirectoryDict

    def selectOutputDirectory(self):
        self.removeFullDirectories()
        minPlots = 100
        outputDirectory = None
        for key, value in self.getPlotsPerOutputLocation().items():
            if(value < minPlots):
                outputDirectory = key
                minPlots = value

        return outputDirectory 

    def removeFullDirectories(self):
        spaceOutputDirectories = []
        for outputDirectory in self.outputDirectories:
            freeSpace = utilFunctions.get_free_space_gb(outputDirectory)
            for tempPlot in self.runningPlots:
                if(tempPlot.tempLocation == outputDirectory):
                    freeSpace = freeSpace - 100

            if(freeSpace > 400):
                spaceOutputDirectories.append(outputDirectory)
            else:
                del self.plotsPerOutputLocation[outputDirectory]
       
        self.outputDirectories = []
        self.outputDirectories = deepcopy(spaceOutputDirectories)

    def runPlot(self, plot):
        if(self.selectOutputDirectory() is not None):
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
                
                if("renamed final file" in line.lower()):
                    return 5

        return maxStage

    def isSpaceOnDrive(self, driveLetter, thresholdGB=300):
        spaceLeft = utilFunctions.get_free_space_mb(utilFunctions.getDiskMountPointFromLetter(driveLetter))
        for runningPlot in self.runningPlots:
            if (runningPlot.getOutputDriveLetter == driveLetter):
                spaceLeft = spaceLeft - runningPlot.finalPlotSize

        return spaceLeft > thresholdGB
