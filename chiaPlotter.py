from plot import Plot
from plotManager import PlotManager
import time

def main():

    plotManager = PlotManager(["D:\chiaFinal", "D:\chiaFinal"], numConcurrentPlots=6)

    for i in range(0, 3):

        for k in range(0, 2):
            tempPlot1 = plotManager.createPlot(4, 4000, "F:\chiaTemp")

            tempPlot1 = plotManager.createPlot(4, 4000, "G:\chiaTemp")

            tempPlot1 = plotManager.createPlot(4, 4000, "Q:\chiaTemp")

    plotManager.startPlotting()

    #time.sleep(10)
    #plotManager.killPlot(plot1)

if __name__=="__main__":
    main()