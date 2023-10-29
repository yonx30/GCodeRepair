import cv2 
# import os 
import numpy as np
# import time
from scipy.spatial import distance as dist
from imutils import perspective
from imutils import contours
import imutils
from math import log10 as lg

dir = r"C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks\Webcam Images/"
name = "model2.jpg"

# dir = r"C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks\Webcam Images/"
# name = "model.jpg"


def midpoint(ptA, ptB):
	return ((ptA[0] + ptB[0]) * 0.5, (ptA[1] + ptB[1]) * 0.5)

# construct the argument parse and parse the arguments
# ap = argparse.ArgumentParser()
# ap.add_argument("-i", "--image", required=True,
# 	help="path to the input image")
# ap.add_argument("-w", "--width", type=float, required=True,
# 	help="width of the left-most object in the image (in inches)")
# args = vars(ap.parse_args())

# args = {"image":r"C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks\Webcam Images\OpenCVCans.jpg", "width":10}
# args = {"image":r"C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks\Webcam Images\6SIR Logo.jpg", "width":10}
# args = {"image":dir+name, "width":10}

# cap = cv2.VideoCapture(0) 
# while(cap.isOpened()): 
#     ret, image = cap.read() 
#     if ret == False: 
#         break

class cvImage:
    def __init__(self, args:dict=None, image=None) -> None:
        if type(image) == np.ndarray:
            self.image = image
        elif args:
            self.image = cv2.imread(args["image"])
        self.lgHuMoments = None
        self.cvImage = None
        self.contours = None
        self.find_countours()
        self.draw_contours()

    def find_countours(self):
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY) 
        gray = cv2.GaussianBlur(gray, (11, 11), 0) # Blurring removes noise, (7,7) is standard deviation in x/y directions for blur   

        # perform edge detection, then perform a dilation + erosion to
        # close gaps in between object edges
        kernel = np.ones((2,2),np.uint8)
        edged = cv2.Canny(gray, 93, 100, apertureSize=3)
        edged = cv2.dilate(edged, kernel, iterations=2) # Dilate expands the width of (contour) lines and features
        edged = cv2.erode(edged, kernel, iterations=2) # Erode is the opposite of dilate

        # find contours in the edge map
        self.contours = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # Draws contours - 1st arg is image, 2nd is contour retrieval mode and 3rd is contour approx method
        self.contours = imutils.grab_contours(self.contours)
        (self.contours, _) = contours.sort_contours(self.contours)
        self.cvImage = self.image.copy()

    def draw_contours(self):
        # loop over the contours individually
        for contour in self.contours:
            # Compute the contour area, reject those below a certain size
            if cv2.contourArea(contour) < 2500:
                continue

            # Fits straight line contours to the given contour approximately, with the straight line lengths being epsilon and the Bool (True)
            # referring to whether the approxPolyDP should be closed
            epsilon = 0.001*cv2.arcLength(contour,True)
            contourApprox = cv2.approxPolyDP(contour,epsilon,True)

            # Construct a numpy array with the contour coordinates
            contourApprox = np.array(contourApprox, dtype="int")

            # args = (image, contours to be passed, contours to draw [-1 means all], RGB colour of contours, thickness)
            cv2.drawContours(self.cvImage, [contourApprox], -1, (255, 0, 0), 2) 
            # huMoments = cv2.HuMoments(cv2.moments(image))
            huMoments = cv2.HuMoments(cv2.moments(contourApprox))
            try:
                self.lgHuMoments = np.array([-lg(abs(huMoment[0])) for huMoment in huMoments], dtype=float)
            except:
                pass
            
            else:
                # Gets the centroid, then write the lgHuMoment values at the centroid
                moment = cv2.moments(contour)
                cX = int(moment["m10"] / moment["m00"])
                cY = int(moment["m01"] / moment["m00"])
                cv2.putText(self.cvImage, "{:.1f}".format(np.average(self.lgHuMoments)),
                (int(cX), int(cY)), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (0, 0, 0), 2)
    
    def draw_bounding_box(self, width:int or float):
        pixelsPerMetric = None
        for contour in self.contours:
            # Compute the contour area, reject those below a certain size
            if cv2.contourArea(contour) < 2500:
                continue        
            # compute the rotated bounding box of the contour
            box = cv2.minAreaRect(contour)
            box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)
            box = np.array(box, dtype="int")

            # order the points in the contour such that they appear
            # in top-left, top-right, bottom-right, and bottom-left
            # order, then draw the outline of the rotated bounding
            # box
            box = perspective.order_points(box)
            cv2.drawContours(self.cvImage, [box.astype("int")], -1, (0, 255, 0), 3)

            
            # loop over the original points and draw them
            for (x, y) in box:
                cv2.circle(self.cvImage, (int(x), int(y)), 5, (0, 0, 255), -1)
            
            # unpack the ordered bounding box, then compute the midpoint
            # between the top-left and top-right coordinates, followed by
            # the midpoint between bottom-left and bottom-right coordinates
            (tl, tr, br, bl) = box
            (tltrX, tltrY) = midpoint(tl, tr) #top width
            (blbrX, blbrY) = midpoint(bl, br) #bottom width
            # compute the midpoint between the top-left and bottom-left points,
            # followed by the midpoint between the top-righ and bottom-right
            (tlblX, tlblY) = midpoint(tl, bl) #left height
            (trbrX, trbrY) = midpoint(tr, br) #right height
            # draw the midpoints on the image
            cv2.circle(self.cvImage, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
            cv2.circle(self.cvImage, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
            cv2.circle(self.cvImage, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
            cv2.circle(self.cvImage, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)
            # draw lines between the midpoints
            cv2.line(self.cvImage, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),
                (255, 0, 255), 2)
            cv2.line(self.cvImage, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),
                (255, 0, 255), 2)
            
            # compute the Euclidean distance between the midpoints
            dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY)) #height
            dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY)) #width
            # if the pixels per metric has not been initialized, then
            # compute it as the ratio of pixels to supplied metric
            # (in this case, inches)
            if pixelsPerMetric is None:
                pixelsPerMetric = dB / width

            # compute the size of the object
            dimA = dA / pixelsPerMetric
            dimB = dB / pixelsPerMetric
            # draw the object sizes on the image
            cv2.putText(self.cvImage, "X = {:.1f}mm".format(dimB),
                (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (0, 0, 0), 3)
            cv2.putText(self.cvImage, "Z = {:.1f}mm".format(dimA),
                (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
                0.65, (0, 0, 0), 3)


    def draw_image(self, wait:int or float=0):
        cv2.imshow("Image", self.cvImage)
        cv2.waitKey(wait)

    def write_text(self, xcoord:float or int, ycoord:float or int, text:str):
        cv2.putText(self.cvImage, text,
		(int(xcoord), int(ycoord)), cv2.FONT_HERSHEY_SIMPLEX,
		0.65, (0, 0, 0), 3)

def compare_hu_moments(cvImage1:cvImage, cvImage2:cvImage):
    try:
        cvImage1.lgHuMoments.any() and cvImage2.lgHuMoments.any()
        stdDeviationLst = []
        for i in range(len(cvImage1.lgHuMoments)):
            stdDeviationLst.append( (cvImage1.lgHuMoments[i] - cvImage2.lgHuMoments[i]) * 2 )
        
        std_deviation = sum(stdDeviationLst) / len(stdDeviationLst)
    
    except:
        return None
    return std_deviation

if __name__ == "__main__":

    args = {"image":r"C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks\Webcam Images\model6.jpg"}
    image6 = cvImage(args)
    image6.draw_image()

    args = {"image":r"C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks\Webcam Images\model.jpg"}
    image1 = cvImage(args)
    image1.draw_image()

    args = {"image":r"C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks\Webcam Images\model2.jpg"}
    image2 = cvImage(args)
    image2.draw_image()

    args = {"image":r"C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks\Webcam Images\model3.jpg"}
    image3 = cvImage(args)
    image3.draw_image()

    args = {"image":r"C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks\Webcam Images\model4.jpg"}
    image4 = cvImage(args)
    image4.draw_image()

    args = {"image":r"C:\Users\yonx3\Documents\NUS Y2S1\NOC\Misc\Calhacks\Webcam Images\model5.jpg"}
    image5 = cvImage(args)
    image5.draw_image()

    print(f"Hu Moment Deviation 1: {compare_hu_moments(image1, image2)}")
    print(f"Hu Moment Deviation 2: {compare_hu_moments(image1, image3)}")
    print(f"Hu Moment Deviation 3: {compare_hu_moments(image1, image4)}")
    print(f"Hu Moment Deviation 4: {compare_hu_moments(image1, image5)}")
    print(f"Hu Moment Deviation 5: {compare_hu_moments(image4, image5)}")




# # load the image, convert it to grayscale, and blur it slightly
# image = cv2.imread(args["image"]) # Can technically indicate greyscale as 2nd arg straight away, but best to parse colour images as BGR first then convert subsequently
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
# gray = cv2.GaussianBlur(gray, (9, 9), 0) # Blurring removes noise, (7,7) is standard deviation in x/y directions for blur


# # perform edge detection, then perform a dilation + erosion to
# # close gaps in between object edges
# edged = cv2.Canny(gray, 93, 100, apertureSize=3)
# edged = cv2.dilate(edged, None, iterations=1) # Dilate expands the width of (contour) lines and features
# edged = cv2.erode(edged, None, iterations=1) # Erode is the opposite of dilate


# # find contours in the edge map
# cnts = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE) # Draws contours - 1st arg is image, 2nd is contour retrieval mode and 3rd is contour approx method

# cnts = imutils.grab_contours(cnts)
# # sort the contours from left-to-right and initialize the
# # 'pixels per metric' calibration variable
# # if not contours.sort_contours(cnts):
# #     continue
# (cnts, _) = contours.sort_contours(cnts)
# pixelsPerMetric = None

# # print(cnts)
# # cv2.imshow("Image", edged)
# # cv2.waitKey(0)

# orig = image.copy()

# # loop over the contours individually
# for contour in cnts:
#     # Compute the rotated bounding box of the contour
#     if cv2.contourArea(contour) < 1500:
#         continue

#     # compute the rotated bounding box of the contour
    
#     # Fits straight line contours to the given contour approximately, with the straight line lengths being epsilon and the Bool (True)
#     # referring to whether the approxPolyDP should be closed
#     epsilon = 0.001*cv2.arcLength(contour,True)
#     contourApprox = cv2.approxPolyDP(contour,epsilon,True)

#     # Construct a numpy array with the contour coordinates
#     contourApprox = np.array(contourApprox, dtype="int")

#     # args = (image, contours to be passed, contours to draw [-1 means all], RGB colour of contours, thickness)
#     cv2.drawContours(orig, [contourApprox], -1, (0, 255, 0), 2) 
#     # huMoments = cv2.HuMoments(cv2.moments(image))
#     huMoments = cv2.HuMoments(cv2.moments(contourApprox))
#     print(huMoments)
#     lgHuMoments = np.array([-lg(abs(huMoment[0])) for huMoment in huMoments], dtype=float)
#     print("\n", lgHuMoments)

    # show the output image
# cv2.imshow("Image", orig)
# cv2.waitKey(0)
    # if cv2.waitKey(25) & 0xFF == ord('q'):
    #     break

"""# loop over the contours individually
for c in cnts:
    # Compute the rotated bounding box of the contour
    if cv2.contourArea(c) < 1500:
        continue

    # compute the rotated bounding box of the contour
    
    # Draws a rectangle that fits the countour entirely, can be rotated (unlike cv2.boundingRect) 
    box = cv2.minAreaRect(c)

    # Gets the four corners of the box drawn, starting from lowest point then rotating clockwise
    box = cv2.cv.BoxPoints(box) if imutils.is_cv2() else cv2.boxPoints(box)

    # Construct a numpy array with the box corner coordinates
    box = np.array(box, dtype="int")

    # order the points in the contour such that they appear in top-left, top-right, bottom-right, 
    # and bottom-left order, then draw the outline of the rotated bounding box
    box = perspective.order_points(box)

    # args = (image, contours to be passed, contours to draw [-1 means all], RGB colour of contours, thickness)
    cv2.drawContours(orig, [box.astype("int")], -1, (0, 255, 0), 2) 

    # loop over the original points and draw them
    for (x, y) in box:
        cv2.circle(orig, (int(x), int(y)), 5, (0, 0, 255), -1)

    # unpack the ordered bounding box, then compute the midpoint between the top-left and top-right coordinates, 
    # followed by the midpoint between bottom-left and bottom-right coordinates
    (tl, tr, br, bl) = box
    (tltrX, tltrY) = midpoint(tl, tr)
    (blbrX, blbrY) = midpoint(bl, br)
    # compute the midpoint between the top-left and top-right points,
    # followed by the midpoint between the top-righ and bottom-right
    (tlblX, tlblY) = midpoint(tl, bl)
    (trbrX, trbrY) = midpoint(tr, br)
    # draw the midpoints on the image
    cv2.circle(orig, (int(tltrX), int(tltrY)), 5, (255, 0, 0), -1)
    cv2.circle(orig, (int(blbrX), int(blbrY)), 5, (255, 0, 0), -1)
    cv2.circle(orig, (int(tlblX), int(tlblY)), 5, (255, 0, 0), -1)
    cv2.circle(orig, (int(trbrX), int(trbrY)), 5, (255, 0, 0), -1)
    # draw lines between the midpoints
    cv2.line(orig, (int(tltrX), int(tltrY)), (int(blbrX), int(blbrY)),(255, 0, 255), 2)
    cv2.line(orig, (int(tlblX), int(tlblY)), (int(trbrX), int(trbrY)),(255, 0, 255), 2)

    # compute the Euclidean distance between the midpoints
    dA = dist.euclidean((tltrX, tltrY), (blbrX, blbrY))
    dB = dist.euclidean((tlblX, tlblY), (trbrX, trbrY))
    # if the pixels per metric has not been initialized, then
    # compute it as the ratio of pixels to supplied metric
    # (in this case, inches)
    if pixelsPerMetric is None:
        pixelsPerMetric = dB / args["width"]
        
    # compute the size of the object
    dimA = dA / pixelsPerMetric
    dimB = dB / pixelsPerMetric
    # draw the object sizes on the image
    cv2.putText(orig, "{:.1f}in".format(dimA),
        (int(tltrX - 15), int(tltrY - 10)), cv2.FONT_HERSHEY_SIMPLEX,
        0.65, (255, 255, 255), 2)
    cv2.putText(orig, "{:.1f}in".format(dimB),
        (int(trbrX + 10), int(trbrY)), cv2.FONT_HERSHEY_SIMPLEX,
        0.65, (255, 255, 255), 2)"""
