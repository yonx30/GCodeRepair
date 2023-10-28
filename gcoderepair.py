import os
import math
import numpy as np
import pandas as pd

defaultFileDirectory = r"C:\Users\yonx3\Documents\Crossbow\GCodes"
defaultFileName = "CE3_3DBenchy.gcode"

startLayerSafetyMargin = 0 # Number of extra layers to start printing above last printed layer
lastInitGcode = "M420 S1" # Last non-movement GCode after homing

class gcodereader:

    def __init__(self, filepath):
        self.filepath = filepath
        self.lines = None
        self.layerCount = None
        self.lastLayer = None
        self.totalHeight = None
        self.failureLayer = None
       
        self.read()

    # Reads a GCode file into a numpy array
    def read(self):
        with open(self.filepath, "r") as file:
            lines = (line.strip() for line in file.readlines() if line.strip())
            self.lines = np.array(tuple(lines))
        self.get_layer_height()
        # self.get_last_layer()

    # Retrieves a value (eg. Layer Height) from the GCode, where targetStr is the GCode command or descriptor
    def get_gcode_val(self, targetStr:str):
        df = pd.Series(self.lines).str.contains(targetStr)
        idx = np.where(np.array(df) != 0)[0][0]
        line = self.lines[idx]
        linestr = line.strip(" ")
        idx = linestr.find(":")
        return float(linestr[idx+1:])  

    # Find the index of a the first instance of a specific GCode command 
    def find_gcode_idx(self, targetGCode:str, mode:str="find", mod=None):
        
        if not mod:
            array = self.lines
        else:
            array = self.lines[:mod][::-1]

        if mode.lower() == "find":
            boolArray = np.char.find(array, targetGCode, start=0, end=None)
            idx = np.where(np.array(boolArray) != -1)[0][0]    

        elif mode.lower() == "contains":
            df = pd.Series(array).str.contains(targetGCode)
            idx = np.where(np.array(df) != 0)[0][0]
        return idx
                                 
    # Gets the layer height of the part    
    def get_layer_height(self):
        layerHeight = self.get_gcode_val(targetStr=";Layer height")
        self.layerHeight = layerHeight
        print(f"Layer Height: {self.layerHeight}")

    # Gets the last layer of the complete    
    def get_last_layer(self):
        lastLayer = self.get_gcode_val(targetStr=";LAYER_COUNT:") - 1
        self.lastLayer = lastLayer
        print(f"Layer Count: {self.lastLayer}")

    # Gets the last layer printed of the part, based on the measured part height
    def get_failure_layer(self, zHeight:float or int):
        failureLayer = math.ceil(zHeight / self.layerHeight) 
        self.failureLayer = failureLayer
        print(f"Failure Layer: {self.failureLayer}")

    # Modifies the GCode to home, then start printing one layer after the last printed (failed) layer
    def modify_gcode(self):
        # startIdx is the numpy index of the last non movement GCode after initial homing
        startIdx = self.find_gcode_idx(lastInitGcode, "contains")

        # endIdx is the numpy index of the next layer to be printed, with failureLayer plus a specific safety margin (default 0)
        endIdx = self.find_gcode_idx(f";LAYER:{self.failureLayer + startLayerSafetyMargin}", "find")  

        # restartIdx is the numpy index of the last Z axis movement, to bring the Z axis up to the next layer to print after the
        # last failed layer
        restartIdx = self.find_gcode_idx("Z", "contains", mod=endIdx)
        restartIdx = endIdx - restartIdx - 1

        # Cut off the line represented by restartIdx to only include Z axis movements
        # Do this to avoid printhead crashing into incomplete print before rising to the correct Z height
        restartLine = self.lines[restartIdx].split(" ")
        newLine = []
        for command in restartLine:
            if not command.startswith("X") and not command.startswith("Y"):
                newLine.append(command)
        self.lines[restartIdx] = " ".join(newLine)

        # Combine the different GCode parts to remove the unneeded layers
        modifiedGCode = np.concatenate((self.lines[:startIdx], [self.lines[restartIdx]], ["M0 Please replace print bed then click to continue ; Stop for user input"], self.lines[restartIdx+1:]))

        # Save modifiedGCode as a new Gcode file
        modifiedFile = open(fileDirectory + fileName + " - Repaired.gcode", "w")
        for line in modifiedGCode:
            modifiedFile.write(f"{line}\n")
        
        print("GCode Modified!")
        

def main():
    while True:
        global filepath, fileDirectory, fileName
        fileDirectory = input("Please enter file directory: ") + "/"
        if fileDirectory == "/":
            fileDirectory = defaultFileDirectory + "/"
        fileName = input("Please enter file name: ")

        if not fileName:
            fileName = defaultFileName
        filepath = fileDirectory + fileName

        if not os.path.exists(filepath):
            print(f"Error, file at {filepath} not found. Please re-enter file directory and name!")
        else:
            break


    gcodeobj = gcodereader(filepath)

    while True:
        try:
            failurePartHeight = float(input("Enter part height: "))
        except ValueError or TypeError:
            continue
        else:
            break

    gcodeobj.get_failure_layer(failurePartHeight)
    gcodeobj.modify_gcode()


if __name__ == "__main__":
    print("Starting...")
    main()
    
    