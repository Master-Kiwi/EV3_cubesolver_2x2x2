import numpy as np
from copy import copy
from helpers import *
from color_decode import cube_image_to_hsv, hsv_to_color

#remaps the 4 faces of a cube_pic
def face_remap(face_data, side_str):
    #number of rotations in ccw direction
    rot_ccw = 0
    if(side_str == "up"):   rot_ccw = 0
    if(side_str == "down"): rot_ccw = 2     #180° CCW = 180° CW
    if(side_str == "left"):  rot_ccw = 3    #270° CCW = 90°  CW
    if(side_str == "right"): rot_ccw = 1    #90°  CCW = 270° CW
    if(side_str == "front"): rot_ccw = 0
    if(side_str == "back"):  rot_ccw = 2
    
    #rot90 CCW on flattened 2x2 array:
    #0/1    >   1/3
    #2/3    >   0/2
    for i in range(rot_ccw):
        face_mem = copy(face_data)
        face_data[0] = face_mem[1]
        face_data[1] = face_mem[3]
        face_data[2] = face_mem[0]
        face_data[3] = face_mem[2]
    return face_data


def flat_facemap_insert(flat_facemap, face_data, side_string):
    assert(len(flat_facemap) == 24)
    assert(len(face_data) == 4)

    N_DIM = 2

    #values defined in Rubikscube_2x2x2.py
    rcube_face_idx = {
        "up"     : 0,
        "down"   : 1,
        "front"  : 2,
        "back"   : 3,
        "left"   : 4,
        "right"  : 5,
        }
            
    #buildup flat facemap of size 24 (6*4) with respect to positioning of side-data
    #"up"   = 0 to 3
    #"down" = 4 to 7
    #...
    face_idx = rcube_face_idx[side_string]
    idx_pos_offset = face_idx * N_DIM*N_DIM
    for i in range(N_DIM*N_DIM):        
        flat_facemap[idx_pos_offset+i] = face_data[i]
    

#generate the rcube style facemap as 3-dimensional array from flat facemap
def flat_to_3d(flat_facemap_color):
    N_DIM = 2
    N_FACE = 6

    assert(len(flat_facemap_color) == N_FACE*N_DIM*N_DIM), 'wrong size of flat array for 2x2x2 cube'
    
    #values defined in Rubikscube_2x2x2.py
    rcube_col_idx = {
    "white"     : 0,
    "yellow"    : 1,
    "orange"    : 2,
    "red"       : 3,
    "blue"      : 4,
    "green"     : 5,
    }

    #rcube style facemap 
    complete_facemap = np.zeros([N_FACE,N_DIM,N_DIM], dtype=int)
    flat_idx = 0
    
    for side in range(N_FACE): #0 to 5
        for row in range(N_DIM): # 0 to 1
            for item in range(N_DIM): # 0 to 1
                face_color = flat_facemap_color[flat_idx]
                face_color_idx = rcube_col_idx[face_color]
                complete_facemap[side][row][item] = face_color_idx
                flat_idx = flat_idx + 1
    
    return(complete_facemap)


def facemap_to_ascii(flat_facemap):
    fm_ascii = ""
    #values defined in Rubikscube_2x2x2.py
    rcube_col_idx = {
    "white"     : 0,
    "yellow"    : 1,
    "orange"    : 2,
    "red"       : 3,
    "blue"      : 4,
    "green"     : 5,
    }

    for item, cnt in zip(flat_facemap, range(len(flat_facemap))):
        if((cnt % 4) == 0) & (cnt != 0): fm_ascii += "-"
        if(item == rcube_col_idx["white"]): fm_ascii += "W"
        if(item == rcube_col_idx["yellow"]): fm_ascii += "Y"
        if(item == rcube_col_idx["orange"]): fm_ascii += "O"
        if(item == rcube_col_idx["red"]): fm_ascii += "R"
        if(item == rcube_col_idx["blue"]): fm_ascii += "B"
        if(item == rcube_col_idx["green"]): fm_ascii += "G"       
        

    return (fm_ascii)


#very simple test
def main():
    console_clear()
    console_color_enable()
    print(__file__)
    
    #set the current working directory to a path containing test-files
    parent_dir = os.getcwd()
    pic_directory = "cube_scan_testruns" 
    path = os.path.join(parent_dir, pic_directory)
    os.chdir(path)


    #just for example load data for a cube
    start_time = time.time()
    hsv_facemap_original = []
    hsv_facemap_remapped = []
    
    #it's intended first collect ALL HSV Data and decode color at the complete hsv_facemap
    hsv_facemap = cube_image_to_hsv("2022-01-23_16-36-33_back.png")
    hsv_facemap_original += hsv_facemap
    hsv_facemap_remapped += face_remap(hsv_facemap, "back")

    hsv_facemap = cube_image_to_hsv("2022-01-23_16-36-33_down.png")
    hsv_facemap_original += hsv_facemap
    hsv_facemap_remapped += face_remap(hsv_facemap, "down")

    #compare results, down and back are rotated by 180°. 
    #attention: we are dealing with flattened array but the rotation is meant on how the faces appear on the picture
    #this can be found in doc in detail, quick example:
    #orig       remap 180°
    # [0][1]    [3][2]
    # [2][3]    [1][0]
    print("-----Original flat facemap from picture scan-----")
    color_facemap_orig = hsv_to_color(hsv_facemap_original)
    print("-----remapped facemap -----")
    color_facemap_remapped = hsv_to_color(hsv_facemap_remapped)

    print("Cube pics decoded in --- %s seconds ---" % (time.time() - start_time))

if __name__=="__main__":
    
    main()
