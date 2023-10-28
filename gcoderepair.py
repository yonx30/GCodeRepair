import os, sys
import math
import numpy as np
import pandas as pd


startLayerSafetyMargin = 0
lastInitGcode = "M420 S1"

class gcodereader:

    def __init__(self, filename):
        if not os.path.exists(filename):
            print("{} does not exist!".format(filename))
            sys.exit(1)
        self.filename = filename
        self.lines = None
        self.layerCount = None
        self.lastLayer = None
        self.totalHeight = None
        self.failureLayer = None
       


        self.read()

    def read(self):
        with open(self.filename, "r") as file:
            lines = (line.strip() for line in file.readlines() if line.strip())
            self.lines = np.array(tuple(lines))
        self.get_layer_height()
        self.get_last_layer()


    def get_gcode_val(self, targetStr:str):
        df = pd.Series(self.lines).str.contains(targetStr)
        idx = np.where(np.array(df) != 0)[0][0]
        line = self.lines[idx]
        linestr = line.strip(" ")
        idx = linestr.find(":")
        return float(linestr[idx+1:])  
     
    def find_gcode_idx(self, targetStr:str, mode:str="find", mod=None):
        
        if not mod:
            array = self.lines
        else:
            array = self.lines[:mod][::-1]

        if mode.lower() == "find":
            boolArray = np.char.find(array, targetStr, start=0, end=None)
            idx = np.where(np.array(boolArray) != -1)[0][0]    

        elif mode.lower() == "contains":
            df = pd.Series(array).str.contains(targetStr)
            idx = np.where(np.array(df) != 0)[0][0]
        return idx
        

                                 
        
    def get_layer_height(self):
        layerHeight = self.get_gcode_val(targetStr=";Layer height")
        self.layerHeight = layerHeight
        print(f"Layer Height: {self.layerHeight}")

    def get_last_layer(self):
        lastLayer = self.get_gcode_val(targetStr=";LAYER_COUNT:") - 1
        self.lastLayer = lastLayer
        print(f"Layer Count: {self.lastLayer}")


    def get_failure_layer(self, zHeight:float or int):
        failureLayer = math.ceil(zHeight / self.layerHeight) 
        self.failureLayer = failureLayer
        print(f"Failure Layer: {self.failureLayer}")

    def modify_gcode(self):
        startIdx = self.find_gcode_idx(lastInitGcode, "contains")

        endIdx = self.find_gcode_idx(f";LAYER:{self.failureLayer + startLayerSafetyMargin}", "find")  

        restartIdx = self.find_gcode_idx("Z", "contains", mod=endIdx)
        restartIdx = endIdx - restartIdx - 1

        restartLine = self.lines[restartIdx].split(" ")
        newLine = []
        for command in restartLine:
            if not command.startswith("X") and not command.startswith("Y"):
                newLine.append(command)

        self.lines[restartIdx] = " ".join(newLine)

        modifiedGCode = np.concatenate((self.lines[:startIdx], [self.lines[restartIdx]], ["M0 Please replace print bed then click to continue ; Stop for user input"], self.lines[restartIdx+1:]))

        modifiedFile = open(r"C:\Users\yonx3\Documents\Crossbow\GCodes\Modified.gcode", "w")
        for line in modifiedGCode:
            modifiedFile.write(f"{line}\n")
        
        print("GCode Modified!")
        

def main():
    gcodeobj = gcodereader(filename = r"C:\Users\yonx3\Documents\Crossbow\GCodes\CE3_3DBenchy.gcode")

    while True:
        try:
            failurePartHeight = 22.5#float(input("Enter part height: "))
        except ValueError or TypeError:
            continue
        else:
            break

    gcodeobj.get_failure_layer(failurePartHeight)
    gcodeobj.modify_gcode()


if __name__ == "__main__":
    print("Starting")
    main()
    
    