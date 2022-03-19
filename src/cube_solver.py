import os
import sys
import time
#import numpy as np
import subprocess
import shlex


from copy import copy, deepcopy
from RubiksCube_2x2x2 import tRubikCube
from ev3_dc_control import tCubeRobot
from helpers import *

from camera import Camera_Init, Camera_Close, Capture_to_File, working_dir_save, working_dir_restore
from color_decode import cube_image_to_hsv, hsv_to_color
from array_funcs import flat_to_3d, face_remap, flat_facemap_insert, facemap_to_ascii

EV3_mac_address = '00:16:53:46:E9:BB'

'''
trecord_stamps = [
    "2022-01-16_10-15-21",  #daylight
    "2022-01-16_10-16-16",
    "2022-01-16_10-17-09",  #daylight + smartphone lamp
    "2022-01-16_10-17-57",
    #"2022-01-16_10-20-14",  #daylight + led-ring
    #"2022-01-16_10-21-04",
    "2022-01-16_10-22-23",  #darkness, only TFT light shining
    "2022-01-16_10-23-18",
    "2022-01-16_10-24-13",  #darkness + smartphone_lamp
    "2022-01-16_10-25-07",
    "2022-01-16_10-26-02",  #darkness + ceiling light
    "2022-01-16_10-26-58",
    #"2022-01-16_10-27-58",  #darkness + led-ring
    #"2022-01-16_10-28-46",
    
    "2022-01-23_15-46-28",  #smartphone lamp
    "2022-01-23_15-48-40",  #smartphone lamp
    "2022-01-23_15-49-44",  #smartphone lamp, up="red", front=white
    "2022-01-23_15-51-06",  #smartphone lamp, scrambled cube, AWB on
    "2022-01-23_16-11-27",   #awb off, set manual gains 1,2
    "2022-01-23_16-36-33",   #awb off, set manual gains 1,2
        ]
'''

#decodes all 6 cube-pics, get their face colors.
#remaps the faces to defined standard in col_array_map.xls (machines rotation shows sides rotated)
#returns the facemap
def Decode_Cube_Pics(cube_scan_pics):
    
    N_FACE = 6
    N_DIM = 2
    FLAT_SIZE = N_FACE*N_DIM*N_DIM  #24
    flat_facemap = [None] * 24
    

    #iterate over all image files
    for key,value  in cube_scan_pics.items():
        print(key + ":" + value)
        filename = value
        side_string = key
        #get the hsv values for actual image - flat array of 4
        face_hsv = cube_image_to_hsv(filename)
        #remap the array based on it's side
        face_hsv = face_remap(face_hsv, side_string)
        
        #insert face data into flat facemap, array position depends on side-string
        flat_facemap_insert(flat_facemap,face_hsv,side_string )


    #Color Decoding at the end on all data
    flat_facemap_color = hsv_to_color(flat_facemap)

    #convert to 3D Facemap needed for tRubikCube
    rcube_facemap = flat_to_3d(flat_facemap_color)

    return rcube_facemap


    
#assume the 6 files exist in the pic-directory, behave like Cube-Scan()
def Cube_Scan_Emulate(pic_directory, timestr):
    print(">>   Cube_Scan_Emulate(%s, %s)" %(pic_directory,timestr ))
    directory = pic_directory
    parent_dir = os.getcwd()
    path = os.path.join(parent_dir, directory)

    #set the current working directory
    os.chdir(path)
    print(">> Picture Directory is: '%s' " %(os.getcwd()))
    
    filename_prefix = timestr 
    cube_scan_pics = {
    "front" : filename_prefix+"_front.png",
    "back"  : filename_prefix+"_back.png",
    "left"  : filename_prefix+"_left.png",
    "right" : filename_prefix+"_right.png",
    "up"    : filename_prefix+"_up.png",
    "down"  : filename_prefix+"_down.png",
    }
    return (cube_scan_pics, timestr)


def Cube_Scan(pic_directory):
    #get timestamp for actual scan - to have unique filenames
    now = time.localtime()
    timestr = str(time.strftime("%Y-%m-%d_%H-%M-%S", now))
    
    #create dict for save-files, key=side, value=filename
    if (sys.platform == "win32"):
        #filename_prefix = pic_directory + "//" + timestr     
        filename_prefix = timestr     
    if (sys.platform == "linux"):
        #filename_prefix = pic_directory + "\\" + timestr     
        filename_prefix = timestr     
        
    cube_scan_pics = {
    "front" : filename_prefix+"_front.png",
    "back"  : filename_prefix+"_back.png",
    "left"  : filename_prefix+"_left.png",
    "right" : filename_prefix+"_right.png",
    "up"    : filename_prefix+"_up.png",
    "down"  : filename_prefix+"_down.png",
    }

    machine = tCubeRobot(EV3_mac_address)
    bat_percent = machine.GetBattery()

    #start camera stream and set the working directory to pic_dir
    camera = Camera_Init(pic_directory)
    
    #orig position is "Front" do not immediate take picture, as cube maybe misaligned
    #cube will be centered during the scan sequence.
    machine.Y_turn("CW", 1)
    Capture_to_File(camera, cube_scan_pics["right"]) 
    machine.Y_turn("CW", 1)
    Capture_to_File(camera, cube_scan_pics["back"])
    machine.Y_turn("CW", 1)
    Capture_to_File(camera, cube_scan_pics["left"])
    machine.Y_turn("CW", 1)
    Capture_to_File(camera, cube_scan_pics["front"])
    
    machine.X_turn("CW", 1)
    Capture_to_File(camera, cube_scan_pics["down"])
    machine.X_turn("CW", 2)
    Capture_to_File(camera, cube_scan_pics["up"])
    #back to orig position = front
    machine.X_turn("CW", 1)
    
    #stop streaming (cv2) > save power, reset working directory
    Camera_Close(camera)
    #unlock all brakes after movement, save power, allow turning of motors
    machine.unlock_brake()

    return (cube_scan_pics, timestr)

def main():
    console_clear()
    console_color_enable()
    working_dir_save()
    print(__file__)

    
    #collect 6 pictures, 
    # return image filenames and path
    # return the unique timestr used
    print("\n-----Programm Start--------")
    if (sys.platform == "win32"):   
        cube_scan_pics, timestr = Cube_Scan_Emulate(pic_directory="cube_scan_testruns", timestr="2022-01-23_16-36-33")
        #cube_scan_pics, timestr = Cube_Scan(pic_directory="cube_scan_testruns")
    if (sys.platform == "linux"):   
        cube_scan_pics, timestr = Cube_Scan(pic_directory="cube_scan_testruns")
    
    #Display Filenames
    print("\n-----Cube pictures --------")
    for key,value in cube_scan_pics.items():
        print("\t>> " + str(key) + " : " + str(value))

    
    #decode the pics and get the standard 3D facemap [6][2][2] need for tRubikCube
    #np.array() is returned 
    rcube_facemap = Decode_Cube_Pics(cube_scan_pics)        

    scanned_cube = tRubikCube()
    #np.array is used in tRubikCube > will be converted from list, deepcopy necessary?
    scanned_cube.set_facemap(rcube_facemap)
    
    #stop on selftest error > color decoding wrong
    result = scanned_cube.self_test()
    scanned_cube.print_2d()

    #save to json descriptor file - exchange IO for the solver_algo
    scanned_rcube_json_file = timestr + '_scanned.json'
    scanned_cube.save_to_file(scanned_rcube_json_file)



    """
    #ascii conversion to style "WWWW-YYYY-OOOO-RRRR-BBBB-GGGG", better use flat facemap
    #side order U-D-F-B-R-L as read from get_facemap()
    flat_facemap = scanned_cube.get_facemap(flatten=True)
    #cube_data_string = "WWWW-YYYY-OOOO-RRRR-BBBB-GGGG"
    cube_data_string = facemap_to_ascii(flat_facemap)
    print("Solver Argument: \"%s\" " %cube_data_string)

    working_dir_restore()

    print("Call Solver Algo....")
    time.sleep(0.5)
    #example on windows use "cmd.exe" to call executable or use builtin functions (like dir, cd,..)
    cmd_string = "cmd /c dir"
    #cmd_string = "powershell -command dir"
    #subprocess module needs sliced arguments
    #cmd_string = "C://work//ML_workspace//projects//EV3_cubesolver_2x2x2//C_solver//out//cube_solver_1.exe"
    cmd_string = "C_solver//out//cube_solver_1.exe " + cube_data_string
    cmd_and_args_split = shlex.split(cmd_string)
    #print("Split Command Str: " + str(cmd_and_args))
    
    #CLI - dump stdout and stderr to variables
    process = subprocess.run(cmd_and_args_split, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE,
                    universal_newlines=True)
    #assert(process.returncode == 0), 'solver algo error'
    print("Rx %d characters on stdout" % len(process.stdout))
    print(process.stdout)
    
    print("Execute Solver Algo on Machine")
    time.sleep(0.5)
    """
    
    print("-----Programm Exit---------")

    exit()

if __name__=="__main__":
    main()
