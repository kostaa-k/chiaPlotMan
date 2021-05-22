from plot import Plot
from plotManager import PlotManager
import time

def main():

    plotManager = PlotManager(["D:\chiaFinal", "D:\chiaFinal"])
    plot1 = plotManager.createPlot(2, 4, 4000, "D:\chiaTemp")
    plot1 = plotManager.createPlot(2, 4, 4000, "D:\chiaTemp")

    plotManager.startPlotting()

    #time.sleep(10)
    #plotManager.killPlot(plot1)

if __name__=="__main__":
    main()