import os
import time
import numpy as np
from PIL import Image
from helpers import *

#coordinates used on usb webcam (windows)
'''rect_coord = [
    [(149,171),(184,247)],  #up-left rect
    [(257,153),(310,248)],  #up-right rect
    [(141,353),(186,431)],  #down-left rect 
    [(253,359),(297,446)]   #down-right rect
]'''

#coordinates used on rpi cam capture images
rect_coord = [
    [(160,165),(220,254)], 
    [(322,162),(372,248)],
    [(169,394),(227,457)],
    [(335,377),(374,453)]
]

'''
160,165
220,254
322,162
372,248
169,394
227,457
335,377
374,435
'''


def px_rect_avg_color(image_data, p1, p2):
    """
    extracts rectangular area of a image pixel-map with 3 channels each 8 Bit (example: rgb, hsv, yuv,...)
    :param      image_data:     Image input data (pixel-map), numpy array with 3 channels eg. RGB, YUV or HSV encoded.
                p1:             x,y coordinate tuple of rectangle
                p2:             x,y coordinate tuple of rectangle
    :return:    ch0_val, ch1_val, ch2_val:        most dominant channel values - using histogram
    """    
    #print("Rect Coordinates \tP1: " + str(p1) + "\tP2: " +str(p2))
    x1,y1 = p1
    x2,y2 = p2

    #x1/y1 is always smaller!
    if(x2 < x1): 
        mem = x1
        x1 = x2
        x2 = mem
    if(y2 < y1): 
        mem = y1
        y1 = y2
        y2 = mem

    #side-len is always positive > as a result of above swap
    a = x2-x1 
    b = y2-y1
    
    #print("Rect len \t a=" + str(a) + "\t b=" + str(b))
    ch0 = []
    ch1 = []
    ch2 = []
    #collect pixel data for rectangle, line-wise
    for y in range(y1, y1+b+1, 1):
        for x in range(x1, x1+a+1, 1):
            pix_data = image_data[x,y]
            ch0 += [pix_data[0]]
            ch1 += [pix_data[1]]
            ch2 += [pix_data[2]]

            #print("X: " + str(x) + "Y:" + str(y) + "pix: " + str(pix_data))
    
    #calc_hist_max needs numpy array
    ch0 = np.array(ch0)
    ch1 = np.array(ch1)
    ch2 = np.array(ch2)

    #Analyze Histogramm Data, use 32 bins (0-255 is channel value range)
    ch0_val = calc_hist_max(ch0, 32)
    ch1_val = calc_hist_max(ch1, 32)
    ch2_val = calc_hist_max(ch2, 32)

    return(ch0_val, ch1_val, ch2_val)


def calc_hist_max(indata, num_bins):
    """
    computes histogram distribution of indata with and returns the most dominant value 
    :param      indata:         input data, numpy array (dimension=1), in case of picture data the values are typical 0-255
                bins:           number of bins used in histogram 
    :return:    bin_val:        most dominant value of indata
    """
    #will give n hist values and n+1 bin edges
    hist, bin_edge = np.histogram(indata, bins=num_bins)
    #histogram maximum value and its index
    hist_max = np.max(hist)
    max_idx = np.where(hist == hist_max)[0][0]

    #corresponding bin edges for hist maximum 
    bin_edge_0 = bin_edge[max_idx]
    bin_edge_1 = bin_edge[max_idx+1]
    
    #take average of bin_edge values
    bin_val = np.mean([bin_edge_0, bin_edge_1])
    return bin_val


def cube_image_to_hsv(filename):
    """
    get hsv values for a cube_scan image files, 4 faces on the 2x2 cube will return an list of size 4
    :param      filename:    picture filename to analyze
    :return:    face_hsv:    list of HSV-values(tuples) [hue, sat, val] - len = 4 on 2x2
    """
    #colors = [""] * 4
    face_hsv = []
    
    #img_rgb = Image.open(filename)
    img_hsv = Image.open(filename).convert('HSV')
    #img_yuv = Image.open(filename).convert('YCbCr')

    
    width, height = img_hsv.size
    assert(width == 480), "width=%d pixel, wrong image size" %width
    assert(height == 640), "height=%d pixel, wrong image size" %height

    #print("Filename: %s Picture Dimension: %d x %d " %(filename, width, height))
    
    #4 rectangles are defined for each face
    #up-left / up-right / down-left / down-right
        
    #load pixel data for alle color encodings
    #px_rgb = img_rgb.load()
    #px_yuv = img_yuv.load()
    px_hsv = img_hsv.load()
    
    #scan all 4 face rectangles on each color representation
    for p1,p2 in rect_coord:
        #rgb_avg = px_rect_avg_color(px_rgb, p1, p2)
        #yuv_avg = px_rect_avg_color(px_yuv, p1, p2)
        hsv_avg = px_rect_avg_color(px_hsv, p1, p2)
        
        #map to standard range
        #r,g,b = rgb_avg = 0,0,0
        #r = r / 255         #0 to 1
        #b = b / 255         #0 to 1
        #g = g / 255         #0 to 1
        
        #map to standard range
        #y,u,v = yuv_avg = 0,0,0
        #y = y/255           #0 to 1
        #u = (u-127)/255     #+-0.5
        #v = (v-127)/255     #+-0.5

        #map to standard range 
        hue,sat,val = hsv_avg     
        hue = hue / 255 * 360       #0 to 360°
        sat = sat / 255 * 100       #0 to 100%
        val = val / 255 * 100       #0 to 100%
        hsv_avg = hue,sat,val 

        face_hsv.append(hsv_avg)
        #debug output
        #print(str(p1) +"/" +str(p2) + "\tRGB: %.2f %.2f %.2f" % (r,g,b) + "\tYUV: %.2f %.2f %.2f" % (y,u,v) + "\tHSV: %d %d %d" % (hue,sat,val))
        #print("[%03d,%03d] / [%03d, %03d]" % (p1[0], p1[1], p2[0], p2[1]) + "\tHSV: %03d %03d %03d" % (hue,sat,val))

    img_hsv.close()
    return (face_hsv)



def hsv_to_color(hsv_facemap):
    """
    convert hsv-values to rcube color string
    :param      hsv_facemap:    list of HSV values(tuples) [hue, sat, val]
    :return:    color_facemap:  list of color strings
    """
    color_facemap = []

    #index only used for debug print
    for hsv,index in zip(hsv_facemap, range(len(hsv_facemap))):
        hue, sat, val = hsv
        face_color = ""

        if(sat <= 25): #low saturation means white 
            face_color = "white"
        else:
            if(hue < 9) | (hue > 330): 
                face_color = "red"
            elif(hue >= 9) & (hue < 45): 
                face_color = "orange"
            elif(hue >= 45) & (hue < 90): 
                face_color = "yellow"
            elif(hue >= 90) & (hue < 180): 
                face_color = "green"
            elif(hue >= 180) & (hue < 270): 
                face_color = "blue"
            else:
                face_color = "magenta"

        color_facemap.append(face_color)
        #debug print, insert a newline each 4 elemets (1 cube face)
        if(index != 0) and (index % 4 == 0): print("")
        print("\t[%02d]" % index + "\tHSV: %03d %03d %03d" % (hue,sat,val) + "\tcolor = %s" % face_color)
    return (color_facemap)

#very simple test
def main():
    console_clear()
    console_color_enable()
    print(__file__)
    print(__doc__)

    #set the current working directory to a path containing test-files
    parent_dir = os.getcwd()
    pic_directory = "cube_scan_testruns" 
    path = os.path.join(parent_dir, pic_directory)
    os.chdir(path)


    #just for example load all data for a cube
    start_time = time.time()
    hsv_facemap = []
    #it's intended first collect ALL HSV Data and decode color at the complete hsv_facemap
    hsv_facemap += cube_image_to_hsv("2022-01-23_16-36-33_back.png")
    hsv_facemap += cube_image_to_hsv("2022-01-23_16-36-33_down.png")
    hsv_facemap += cube_image_to_hsv("2022-01-23_16-36-33_up.png")
    hsv_facemap += cube_image_to_hsv("2022-01-23_16-36-33_front.png")
    hsv_facemap += cube_image_to_hsv("2022-01-23_16-36-33_left.png")
    hsv_facemap += cube_image_to_hsv("2022-01-23_16-36-33_right.png")
    
    #actual hsv_to_color() is deciding on simple conditional
    #better accuracy if all data are compared to each other and groups of 4 are built (future improvment)
    color_facemap = hsv_to_color(hsv_facemap)

    print("Cube pics decoded in --- %s seconds ---" % (time.time() - start_time))

    return

if __name__=="__main__":
    main()