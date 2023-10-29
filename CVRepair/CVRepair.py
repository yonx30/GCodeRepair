import webcam as wb
from heightcv import cvImage, compare_hu_moments
import stleditor 
#import gcoderepair 
import time
import sys, asyncio
import numpy as np

sys.path.insert(0, r'C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks')
def init():
    global screenCam, stlImage, x_dim
    screenCam = wb.screenRecorder()

    path = r'C:\Users\yonx3\Documents\Crossbow\3DBenchySliced.stl'
    savePath = r'C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks\Webcam Images\model6.jpg'
    newMesh = stleditor.stlMesh(path)
    newMesh.plotMesh()
    newMesh.viewMesh()
    newMesh.saveFig(savePath, magnification=2)
    x_dim = newMesh.find_x_dim()
    print(x_dim)
    args = {"image":r"C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks\Webcam Images\model6.jpg"}
    stlImage = cvImage(args)




async def main():
    
    while True:
        image = screenCam.screenshot()
        # print(image)
        try:
            np.average(stlImage.lgHuMoments)
        except:
            pass
        screencapImage = cvImage(image=image)
        
        huDiff = compare_hu_moments(screencapImage, stlImage)
        if huDiff:
            imageMatch = 100 * (1 -  abs(huDiff / 20))
        else:
            imageMatch = 0
        screencapImage.write_text(300, 600, f"Match = {imageMatch}%")

        if imageMatch > 90:
            screencapImage.draw_bounding_box(width=x_dim)

        screencapImage.draw_image(250)
        time.sleep(0.05)

if __name__ == "__main__":
    init()
    asyncio.run(main())

