import os
import sys

from PIL import Image
from helpers import *

#using cv2
if (sys.platform == "win32"):
    import cv2 

#using libcamera with shell execute
if (sys.platform == "linux"):
    import subprocess
    import shlex

__working_dir = ""
def working_dir_save():
    global __working_dir
    __working_dir = os.getcwd()

def working_dir_restore():
    os.chdir(__working_dir)


def picture_dir_init(pic_directory):
    if (sys.platform == "win32"): 
        # Parent Directory is actual working directory
        parent_dir = os.getcwd()
    
    if (sys.platform == "linux"):
        # Parent Directory is /tmp (ramdisk)
        parent_dir = "/tmp"

    # new path
    path = os.path.join(parent_dir, pic_directory)
    # Create the directory
    if(os.path.exists(path) == False):
        os.mkdir(path, mode=0o666)
        print(">> Picture Directory '%s' created in %s" %(pic_directory,parent_dir))
    
    #set the current working directory
    os.chdir(path)
    print(">> Picture Directory is: '%s' " %(os.getcwd()))  


#start camera stream
def Camera_Init(pic_directory):
    #preserve the working directory
    working_dir_save()
    
    #create the picture directory and set actual working directory
    picture_dir_init(pic_directory)

    if (sys.platform == "win32"):   
        print(">> Running on Win32 OS")
        print(">> Using OpenCV")
        print(">> OpenCV version: " + str(cv2.__version__))
        camera = cv2.VideoCapture(0)        
        return (camera)

    if (sys.platform == "linux"):
        print(">> Running on Linux OS")
        if(os.uname()[1] == "raspberrypi"):
            print(">> Running on raspberry")
            print(">> using libcamera, no python binding")
        return

#stop camera stream    
def Camera_Close(camera):
    #reset the working directory 
    working_dir_restore()

    if (sys.platform == "win32"):
        camera.release()
        cv2.destroyAllWindows()
    if (sys.platform == "linux"):
        return


#picture from camera to file
def Capture_to_File(camera, img_filename):
    print("Capture_to_File(\"%s\")" %img_filename)
    
    if (sys.platform == "win32"):
        retval, image = camera.read()
        result = cv2.imwrite(img_filename, image)
        #rotate to adapt for camera orientation 
        Rotate_Image(img_filename, 90)
        Show_Image(img_filename)
        return

    if (sys.platform == "linux"):
        if(os.uname()[1] == "raspberrypi"):
            #using libcamera-still, no python binding at moment - execute shell command
            
            #build the arguments string
            
            #using noir tuning file "--tuning-file /usr/share/libcamera/ipa/raspberrypi/imx219_noir.json"
            tuning_file= "--tuning-file /usr/share/libcamera/ipa/raspberrypi/imx219_noir.json "
            
            #using long exposure max 10 sec  "--shutter 10000000 --gain 1 --awbgains 1,1 --immediate"
            #exposure = "--shutter 10000000 --gain 1 --awbgains 1,1 --immediate "
            #exposure = "--immediate " 
            
            #no preview, manual white balance gains
            exposure = "--immediate --awbgains 1,2 " #awbgain R-chan,B-chan

            #png data
            pic_format = "-e png "

            #output to file
            #img_filename = "cube_scan_results//2022-01-09_11-30-39_back.png"
            #img_filename = "test.png"
            output_file = "-o " + img_filename

            #width heigh, keep aspect ratio=4:3
            #actual changing the width height acts as digital zoom, so it crops the image, should be resolved in future version
            img_dimension ="--width=640 --height=480 "

            #ROI (digital zoom)
            #roi is cropping the image around the given coordinates and afterwards resizes the image to the given resolution.
            #roi = "--roi 0.25,0.25,0.5,0.5 "  
            roi = ""
  
            shell_cmd = "libcamera-still " + tuning_file + exposure + img_dimension + roi + pic_format + output_file
            #print("Shell Cmd to execute: %s " %shell_cmd)
            
            #using os.system("cmd") will redirect the stdout from the cmd-call to the stdout of python (the console)
            #as liubcamera generates a huge amount of messages it's filling up the console output
            #os.system(shell_cmd)
            
            #use subprocess.run() and redirect the output stream 
            cmd_and_args = shlex.split(shell_cmd)
            #print("Split Command Str: " + str(cmd_and_args))

            #CLI - dump stdout and stderr to variables
            process = subprocess.run(cmd_and_args,
                         stdout=subprocess.PIPE, 
                         stderr=subprocess.PIPE,
                         universal_newlines=True)
            assert(process.returncode == 0), 'libcamera-still exception'
            #process = subprocess.run(cmd_and_args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
            #print(process)

            #rotate to adapt for camera orientation
            Rotate_Image(img_filename, 270)


def Rotate_Image(filename, angle):
    print("Rotate_Image(\"%s\", %d)" % (filename, angle))
    #read the image
    im = Image.open(filename)
    #rotate image, expand resolution
    out = im.rotate(angle, expand=True)
    out.save(filename)

def Show_Image(filename):
    if (sys.platform == "win32"):   
        #read the image
        im = Image.open(filename)
        #show image
        im.show(title=filename)
        #input()
        im.close()
    #rpi is headless without display
    if (sys.platform == "linux"):   
        return

#very simple test
def main():
    console_clear()
    console_color_enable()
    print(__file__)

    camera = Camera_Init("camerapy_testdir")
    Capture_to_File(camera, "test.png")
    Camera_Close(camera)
    
    return

if __name__=="__main__":
    main()
