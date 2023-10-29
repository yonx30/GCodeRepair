import webcam as wb
from heightcv import cvImage, compare_hu_moments
import stleditor 
#import gcoderepair 
import time
import sys, asyncio
import numpy as np
import trimesh
import os

sys.path.insert(0, r'C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks')
path = r'C:\Users\yonx3\Documents\Crossbow\3DBenchy.stl'
# path = r"C:\Users\yonx3\Documents\Crossbow\Random\T51_low_poly.stl"
savePath = r'C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks\Webcam Images\referenceSlice.jpg'
meshPath = r'C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks\Webcam Images\newMesh.stl'

def init():
    global screenCam, stlImage, x_dim, newMesh
    screenCam = wb.screenRecorder()
    newMesh = stleditor.stlMesh(path)
    # newMesh.plotMesh()
    newMesh.saveSnapshot(savePath)
    x_dim = newMesh.find_x_dim()
    print(f"X dimension = {x_dim}")
    args = {"image":savePath}
    stlImage = cvImage(args)


async def get_new_mesh(mesh, savePath):
    global x_dim
    os.remove(savePath)
    mesh.saveSnapshot(savePath)
    x_dim = mesh.find_x_dim()
    # print(f"X dimension = {x_dim}")
    args = {"image":savePath}
    return cvImage(args)



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
        
        if imageMatch > 92:
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
                        splitRes = newMesh.section(newPartHeight)
                        trimesh.exchange.export.export_mesh(splitRes, meshPath, 'stl')
                        splitMesh = stleditor.stlMesh(meshPath)
                        # newMesh.plotMesh()
                        stlImage = await get_new_mesh(splitMesh, savePath)
                        res = compare_hu_moments(screencapImage, stlImage)
                        if res == None or huDiff > res:
                            newMesh = stleditor.stlMesh(meshPath)

            else:
                if heightDiff < 0:
                    decrementFlag = True
                if abs(heightDiff) > 0.3 and imageMatch > 92:
                    # Get new sliced STL based on height
                    # print(f"Slicing at height: {newPartHeight}")
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
                
        screencapImage.draw_image(250)
        time.sleep(0.01)

if __name__ == "__main__":
    init()
    asyncio.run(main())

