import numpy as np
import cv2
from droneImageSift import initRefs, findImage

frame = None
track_window = None
hist = None
rect = None

def getNextFrame(vidObj):
    """Takes in the VideoCapture object and reads the next frame, returning one that is half the size 
    (Comment out that line if you want fullsize)."""
    ret, frame = vidObj.read()
    #print type(vidObj), type(frame)
    if frame is not None:
        frame = cv2.resize(frame, (0, 0), fx = 0.5, fy = 0.5)
    return frame

cam = cv2.VideoCapture(0)
ret, frame = cam.read()
#print type(frame)
cv2.namedWindow('camshift')

# start processing frames
while True:
    frame1 = getNextFrame(cam)

    #from camShiftDemo
    hsv = cv2.cvtColor(frame1, cv2.COLOR_BGR2HSV)    # convert to HSV
    mask = cv2.inRange(hsv, np.array((0., 60., 32.)), np.array((180., 255., 255.)))   # eliminate low and high saturation and value values

    vis1 = frame1.copy()

    if track_window is None:
        itemsSought = ['hatch', 'exit']
        properties = initRefs(itemsSought)
        rect = findImage(vis1, properties, itemsSought, 0)
        if rect is not None: #if findImage didn't return anything, just pass and try again
            x, y, w, h = rect
            #print("rect is", rect)
            cv2.rectangle(vis1,(x,y),(x+w,y+h),(0,255,0),2)
            
            track_window = (x, y, w, h)

            hsv_roi = hsv[y:h+y, x:w+x]             # access the currently selected region and make a histogram of its hue 
            mask_roi = mask[y:h+y, x:w+x]
            hist = cv2.calcHist( [hsv_roi], [0], mask_roi, [16], [0, 180] )
            cv2.normalize(hist, hist, 0, 255, cv2.NORM_MINMAX)
            hist = hist.reshape(-1)
        
    else: #from camShiftDemo
        prob = cv2.calcBackProject([hsv], [0], hist, [0, 180], 1)
        #prob &= mask
        term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 50, 1 )
        track_box, track_window = cv2.CamShift(prob, track_window, term_crit)
        try:
            cv2.ellipse(vis1, track_box, (0, 0, 255), 2)
        except:
            print track_box
        
    cv2.imshow('camshift', vis1)

    ch = 0xFF & cv2.waitKey(5)
    if ch == 27:
        break

        
cv2.destroyAllWindows()


