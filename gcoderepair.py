import os, sys
import math


startLayerSafetyMargin = 0

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
       

        # # print(self.filetype)
        # self.n_segs = 0  # number of line segments
        # self.segs = None  # list of line segments [(x0, y0, x1, y1, z)]
        # self.n_layers = 0  # number of layers
        # # seg_index_bars and subpath_index_bars have the same format
        # # e.g. ith layer has segment indexes [seg_index_bars[i-1],
        # # seg_index_bars[i])
        # self.seg_index_bars = []
        # self.subpath_index_bars = []
        # self.summary = None
        # self.lengths = None
        # self.subpaths = None
        # self.xyzlimits = None
        # self.elements = None
        # self.elements_index_bars = []
        # # read file to populate variables
        self.read()

    def read(self):
        with open(self.filename, "r") as file:
            self.lines = list(line.strip() for line in file.readlines() if line.strip())
        
        self.get_layer_height()
        self.get_last_layer()


    def find_gcode(self, targetStr:str, reverse:bool=False):
        if not reverse:
            #print(lines)
            for line in self.lines:
                if line.startswith(targetStr):
                    linestr = line.strip(" ")
                    idx = linestr.find(":")
                    return float(linestr[idx+1:])       
        
        else:
            #print(tuple(lines))
            for line in reversed(self.lines):
                if line.startswith(targetStr):
                    linestr = line.strip(" ")
                    idx = linestr.find(":")
                    return float(linestr[idx+1:]) 
                                 
        
    def get_layer_height(self):
        layerHeight = self.find_gcode(targetStr=";Layer height")
        self.layerHeight = layerHeight
        print(f"Layer Height: {self.layerHeight}")

    def get_last_layer(self):
        lastLayer = self.find_gcode(targetStr=";LAYER_COUNT:") - 1
        self.lastLayer = lastLayer
        print(f"Layer Count: {self.lastLayer}")

    # def get_layer_height(self, lines):
    #     for line in lines:
    #         if line.startswith(";Layer height"):
    #             idx = line.find(":")
    #             self.layerHeight = float(line[idx+2:])
    #             print(f"Layer height:{self.layerHeight}")
    
    # def get_last_layer(self, lines):
    #     for line in reversed(lines):
    #         if line.startswith(";Layer:"):
    #             idx = line.find(":")
    #             self.lastLayer = int(line[idx+1:])
    #             print(f"Last Layer:{self.lastLayer}")

    def get_failure_layer(self, zHeight:float or int):
        failureLayer = math.ceil(zHeight / self.layerHeight) 
        self.failureLayer = failureLayer
        print(f"Failure Layer: {self.failureLayer}")
        pass

    def modify_gcode(self):
        count = 0
        homeFlag = True
        for line in self.lines:
            if homeFlag:
                count += 1
                if line.startswith("G28"):
                    homeFlag = False
            else:
                count += 1
                if line.startswith("G"):
                    startIdx = count - 1
                    break
                    
        # print(self.lines[startIdx:startIdx+5])
        endIdx = self.lines.index(f";LAYER:{self.failureLayer + startLayerSafetyMargin}")
        print(self.lines[endIdx:endIdx+5])

        count = endIdx
        while True:
            count -= 1
            if "Z" in self.lines[count]:
                endIdx = count
                # print(count)
                break
        
        restartLine = self.lines[endIdx].split(" ")
        # print(restartLine)
        newLine = []
        for command in restartLine:
            if not command.startswith("X") and not command.startswith("Y"):
                newLine.append(command)
        # print(newLine)
        self.lines[endIdx] = " ".join(newLine)
        print(self.lines[endIdx])

        modifiedGCode = self.lines[:startIdx] + [self.lines[endIdx]] + ["M0 Please replace print bed then click to continue ; Stop for user input"] + self.lines[endIdx+1:]
        modifiedFile = open(r"C:\Users\yonx3\Documents\Crossbow\GCodes\Modified.gcode", "w")
        for line in modifiedGCode:
            modifiedFile.write(f"{line}\n")
        
        print("GCode Modified!")
        

def main():
    gcodeobj = gcodereader(filepath = r"C:\Users\yonx3\Documents\Crossbow\GCodes\CE3_3DBenchy.gcode")

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
    print("Starting")
    main()
    
    