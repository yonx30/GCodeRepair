import webcam as wb
from heightcv import cvImage, compare_hu_moments
import stleditor 
#import gcoderepair 
import time
import sys, asyncio
import numpy as np
import trimesh
# import os

sys.path.insert(0, r'C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks')

referenceModelPath = r'C:\Users\yonx3\Documents\Crossbow\3DBenchy.stl'
# referenceModelPath = r"C:\Users\yonx3\Documents\Crossbow\Random\catstretch_voronoi updated.stl"

savePath = r'C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks\Webcam Images\referenceSlice.jpg'
meshPath = r'C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks\Webcam Images\newMesh.stl'

mode = "B"

def init():
    global screenCam, stlImage, x_dim, newMesh

    fileDirectory = input("Please enter file directory: ") + "/"
    fileName = input("Please enter file name: ")
    if not fileName and fileDirectory == "/":
        filepath = referenceModelPath
    else:
      filepath = fileDirectory + fileName
    print(filepath)
        
    screenCam = wb.screenRecorder()
    newMesh = stleditor.stlMesh(filepath)
    # newMesh.plotMesh()
    newMesh.saveSnapshot(savePath, mode)
    x_dim = newMesh.find_x_dim()
    print(f"X dimension = {x_dim}")
    args = {"image":savePath}
    stlImage = cvImage(args)


async def get_new_mesh(mesh, savePath):
    global x_dim
    mesh.saveSnapshot(savePath, mode)
    x_dim = mesh.find_x_dim()
    # print(f"X dimension = {x_dim}")
    args = {"image":savePath}
    return cvImage(args)

async def get_new_image(mesh, newPartHeight:int or float, meshPath:str):
    splitRes = mesh.section(newPartHeight)
    trimesh.exchange.export.export_mesh(splitRes, meshPath, 'stl')
    splitMesh = stleditor.stlMesh(meshPath)
    # newMesh.plotMesh()
    newImage = await get_new_mesh(splitMesh, savePath)
    return newImage


async def main():
    global newMesh, stlImage, x_dim, oldPartHeight, newPartHeight
    oldPartHeight, newPartHeight = 0, 0
    decrementFlag = False
    highestMatch = {"HuDiff":5, "Height":0}
    bestPartHeights = np.array([],dtype=float)

    while True:
        image = screenCam.screenshot()
        # print(image)
        try:
            np.average(stlImage.lgHuMoments)
        except:
            pass
        screencapImage = cvImage(image=image)
        # print(screencapImage.lgHuMoments, stlImage.lgHuMoments)
        
        huDiff = compare_hu_moments(screencapImage, stlImage)
        if huDiff:
            imageMatch = 100 * (1 -  abs(huDiff / 10))
        else:
            imageMatch = 0
        screencapImage.write_text(300, 400, f"Match = {imageMatch}%")
        

        if mode == 'B':
            if imageMatch > 90:
                newPartHeight = screencapImage.draw_bounding_box(width=x_dim,visibility=True)
            else:
                newPartHeight = screencapImage.draw_bounding_box(width=x_dim,visibility=False)
        
            # print(newPartHeight)
            if newPartHeight:
                heightDiff = oldPartHeight - newPartHeight  
                # print(heightDiff) 
                if decrementFlag: 
                    if heightDiff > 0:
                        decrementFlag = True

                    if (abs(heightDiff) > 0.1 and heightDiff < 1 and imageMatch > 98) or (abs(heightDiff) > 0.1 and heightDiff < 0 and imageMatch > 96):
                                                
                            # Get new sliced STL based on height
                            print(f"Slicing at height: {newPartHeight}")
                            stlImage = await get_new_image(newMesh, newPartHeight, meshPath)
                            res = compare_hu_moments(screencapImage, stlImage)
                            if res == None or huDiff > res:
                                newMesh = stleditor.stlMesh(meshPath)

                else:
                    if heightDiff < 0:
                        decrementFlag = True
                    print(abs(heightDiff), imageMatch)
                    if abs(heightDiff) > 0.3 and imageMatch > 86:
                        # Get new sliced STL based on height
                        print(f"Slicing at height: {newPartHeight}")
                        if abs(heightDiff) > 5:
                            splitRes = newMesh.section(oldPartHeight - 5)
                        else:
                            splitRes = newMesh.section(newPartHeight)
                        trimesh.exchange.export.export_mesh(splitRes, meshPath, 'stl')
                        newMesh = stleditor.stlMesh(meshPath)
                        # newMesh.plotMesh()
                        stlImage = await get_new_mesh(newMesh, savePath)
                
                if huDiff and huDiff < highestMatch["HuDiff"]:
                    highestMatch["HuDiff"] = huDiff
                    highestMatch["Height"] = newPartHeight
                    np.append(bestPartHeights, newPartHeight)

                    print("New best part height: %s"%(highestMatch["Height"]))

        elif mode == 'T': 
            partZ = newMesh.find_z_dim()
            
            topImage = await get_new_image(newMesh, partZ + 15, meshPath)
            bottomImage = await get_new_image(newMesh, partZ - 15, meshPath)
            res1 = compare_hu_moments(screencapImage, topImage)
            res2 = compare_hu_moments(screencapImage, bottomImage)
            if res1 == None or res2 == None:
                continue
            imageMatch1 = 100 * (1 -  abs(res1 / 10))
            imageMatch2 = 100 * (1 -  abs(res2 / 10))
            print(f"Part height: {partZ}, topHu = {res1}, bottomHu = {res2}")
            if imageMatch < 99 and imageMatch2 < 99:
                if (abs(res1) - abs(res2)) < 0.001:
                    newZ = partZ
                elif abs(res1) > abs(res2) or (abs(res1) - abs(res2)) < 0.1:
                    newZ = partZ - 15
                else:
                    newZ = partZ + 10
                print(newZ)
                splitRes = newMesh.section(newZ)
                trimesh.exchange.export.export_mesh(splitRes, meshPath, 'stl')
                newMesh = stleditor.stlMesh(meshPath)
            else:
                screencapImage.write_text(300, 500, f"Good Match!")
            screencapImage.write_text(300, 400, f"Match = {max(imageMatch1, imageMatch2)}%")
            


        screencapImage.draw_image(250)
        await asyncio.sleep(0.01)

if __name__ == "__main__":
    init()
    asyncio.run(main())

