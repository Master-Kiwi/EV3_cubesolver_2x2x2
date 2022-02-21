import os 
import numpy as np
import json
import datetime
from copy import copy, deepcopy
import random
from helpers import *

ROT_DIR_CW      = True
ROT_DIR_CCW     = False


SIDE_IDX_UP     = 0
SIDE_IDX_DOWN   = 1
SIDE_IDX_FRONT  = 2
SIDE_IDX_BACK   = 3
SIDE_IDX_LEFT   = 4
SIDE_IDX_RIGHT  = 5

#do not change those numbers - referenced in selftest
COL_IDX_WHITE   = 0
COL_IDX_YELLOW  = 1
COL_IDX_ORANGE  = 2
COL_IDX_RED     = 3
COL_IDX_BLUE    = 4
COL_IDX_GREEN   = 5
COL_IDX_BLACK   = 6
COL_IDX_ERROR   = -1
COL_IDX_END     = 7

#color format strings, check them using console_print_color_table() from helpers.py
#just for print2d, us a dict
col_fmt_str = { 
    COL_IDX_WHITE   : '\x1b[1;37;47m',  
    COL_IDX_YELLOW  : '\x1b[1;37;43m',  
    COL_IDX_ORANGE  : '\x1b[1;37;45m',  
    COL_IDX_RED     : '\x1b[1;37;41m',  
    COL_IDX_BLUE    : '\x1b[1;37;44m',  
    COL_IDX_GREEN   : '\x1b[1;37;42m',     
    COL_IDX_BLACK   : '\x1b[1;37;40m',  #for test use 1;37;46m  > "light blue"   40m > black
    COL_IDX_ERROR   : '\x1b[1;37;46m',
    COL_IDX_END     : '\x1b[0m' 
}

  
#key=color index
color_dict = {
    COL_IDX_WHITE   : "white",
    COL_IDX_YELLOW  : "yellow", 
    COL_IDX_ORANGE  : "orange",
    COL_IDX_RED     : "red",
    COL_IDX_GREEN   : "green",
    COL_IDX_BLUE    : "blue"
}
#key=side index
side_dict = {
    SIDE_IDX_UP     : "up",
    SIDE_IDX_DOWN   : "down",
    SIDE_IDX_FRONT  : "front",
    SIDE_IDX_BACK   : "back",
    SIDE_IDX_LEFT   : "left",
    SIDE_IDX_RIGHT  : "right"
}

ACT_IDX_U_CW  = 0
ACT_IDX_U_CCW = 3
ACT_IDX_R_CW  = 1
ACT_IDX_R_CCW = 4
ACT_IDX_F_CW  = 2
ACT_IDX_F_CCW = 5


#self.action_dict lists all possible actions, key=action_idx
action_dict_short = { 
    ACT_IDX_U_CW:   "U ",
    ACT_IDX_U_CCW:  "U'",
    ACT_IDX_R_CW:   "R ",
    ACT_IDX_R_CCW:  "R'",
    ACT_IDX_F_CW:   "F ",
    ACT_IDX_F_CCW:  "F'",
}

#self.action_dict lists all possible actions, key=action_idx
action_dict = { 
    ACT_IDX_U_CW:   "ROTATE UP    / CW",
    ACT_IDX_U_CCW:  "ROTATE UP    / CCW",
    ACT_IDX_R_CW:   "ROTATE RIGHT / CW",
    ACT_IDX_R_CCW:  "ROTATE RIGHT / CCW",
    ACT_IDX_F_CW:   "ROTATE FRONT / CW",
    ACT_IDX_F_CCW:  "ROTATE FRONT / CCW",
}

class tRubikCube:
    N_DIM: int      #dimension of cube (=side len)

    def __init__(self):
        #actual only 2 is supported
        self.N_DIM = 2 

        #start with empty action list
        #stores all actions that are performed on this object. (by index)
        self.actions_list = []

        #set initial state of cube = solved cube
        #opposite sides
        self.col = np.zeros([6,self.N_DIM,self.N_DIM], dtype=int)
        self.col[SIDE_IDX_UP]     = COL_IDX_WHITE
        self.col[SIDE_IDX_DOWN]   = COL_IDX_YELLOW
        self.col[SIDE_IDX_FRONT]  = COL_IDX_ORANGE
        self.col[SIDE_IDX_BACK]   = COL_IDX_RED  
        self.col[SIDE_IDX_LEFT]   = COL_IDX_BLUE
        self.col[SIDE_IDX_RIGHT]  = COL_IDX_GREEN
  
    #for colored console output, prints <num_blocks> spaces with col_idx as fg/bg/style
    #looks like large colored pixels
    #changed to read from dict
    def _print_blocks(self, col_idx, num_blocks):
        if(col_idx == COL_IDX_ERROR):
            print(col_fmt_str[col_idx] + (' '*num_blocks) + col_fmt_str[COL_IDX_END], sep='', end='')
        else:
            print(col_fmt_str[col_idx] + (' '*num_blocks) + col_fmt_str[COL_IDX_END], sep='', end='')
    #for colored console output, prints text spaces with col_idx as bg
    #pay attention that fg color is set correct in the col_idx strings
    def _print_col_text(self, col_idx, col_text):
        if(col_idx == COL_IDX_ERROR):
            print(col_fmt_str[col_idx] + col_text + col_fmt_str[COL_IDX_END], sep='', end='')
        else:
            print(col_fmt_str[col_idx] + col_text + col_fmt_str[COL_IDX_END], sep='', end='')

  
  
    def print_2d(self):
        ilen = 3  #a cube side col block has a len of 3
        print('', end='\n')
        self._print_blocks(COL_IDX_BLACK, ilen*((self.N_DIM*4+5)))    #fill first line

        for i in range (self.N_DIM):
            print('', end='\n')
            self._print_blocks(COL_IDX_BLACK, ilen*(self.N_DIM+2))
            for j in range (self.N_DIM):
                self._print_blocks(self.col[SIDE_IDX_BACK][i][j], ilen)
            self._print_blocks(COL_IDX_BLACK, ilen*((self.N_DIM*2+3)))

        print('', end='\n')
        self._print_blocks(COL_IDX_BLACK, ilen*((self.N_DIM*4+5)))    #fill seperator back/top

        for i in range (self.N_DIM):
            print('', end='\n')
            self._print_blocks(COL_IDX_BLACK, ilen)

            for j in range (self.N_DIM):
                self._print_blocks(self.col[SIDE_IDX_LEFT][i][j], ilen)
            
            self._print_blocks(COL_IDX_BLACK, ilen)
            for j in range (self.N_DIM):
                self._print_blocks(self.col[SIDE_IDX_UP][i][j], ilen)
            
            self._print_blocks(COL_IDX_BLACK, ilen)      
            for j in range (self.N_DIM):
                self._print_blocks(self.col[SIDE_IDX_RIGHT][i][j], ilen)
            
            self._print_blocks(COL_IDX_BLACK, ilen)
            for j in range (self.N_DIM):
                self._print_blocks(self.col[SIDE_IDX_DOWN][i][j], ilen)

            self._print_blocks(COL_IDX_BLACK, ilen)   #fill last row

        print('', end='\n')
        self._print_blocks(COL_IDX_BLACK, ilen*((self.N_DIM*4+5)))  #fill seperator top/front

        for i in range (self.N_DIM):
            print('', end='\n')
            self._print_blocks(COL_IDX_BLACK, ilen*(self.N_DIM+2))
            for j in range (self.N_DIM):
                self._print_blocks(self.col[SIDE_IDX_FRONT][i][j], ilen)        
            self._print_blocks(COL_IDX_BLACK, ilen*((self.N_DIM*2+3)))

        print('', end='\n')
        self._print_blocks(COL_IDX_BLACK, ilen*((self.N_DIM*4+5))) #fill last line
        print('', end='\n')    

    #get a copy from the action list
    #optional add parameter <notation> to get Text instead of numbers
    #default will give the numbers
    def get_action_list(self, notation="numbers"):
        if(notation=="numbers"):
            return self.actions_list.copy()
        elif (notation=="short"):
            action_list = []
            for action in self.actions_list:
                action_list.append(action_dict_short[action])
            return action_list
        elif (notation=="long"):
            action_list = []
            for action in self.actions_list:
                action_list.append(action_dict[action])
            return action_list

    def _rotate_side(self, side_idx, rotate_dir=ROT_DIR_CW):   
        #np.rot90(<array>, 1) rotates array by 90 degrees in CCW
        #to have -90degrees we just rotate 3-times, what means a CW rotation
        #rotate_dir = True is CW rotation
        if rotate_dir:
            self.col[side_idx] = np.rot90(self.col[side_idx] , 3)
        else:
            self.col[side_idx] = np.rot90(self.col[side_idx] , 1)

    def rotate_simple(self, side_idx, rotate_dir=ROT_DIR_CW):
        #rotate the main side, just a array rotatation
        self._rotate_side(side_idx, rotate_dir)
        #rotate the adjacent side
        if side_idx == SIDE_IDX_UP: 
            mem_side_back = self.col[SIDE_IDX_BACK][1].copy()
            #mem_side_back = [0] * 2
            #mem_side_back[0] = self.col[SIDE_IDX_BACK][1][0]
            #mem_side_back[1] = self.col[SIDE_IDX_BACK][1][1]
            if rotate_dir:    #0    #True = CW
                self.col[SIDE_IDX_BACK][1][0]   = self.col[SIDE_IDX_LEFT][1][1] 
                self.col[SIDE_IDX_BACK][1][1]   = self.col[SIDE_IDX_LEFT][0][1]
                self.col[SIDE_IDX_LEFT][0][1]   = self.col[SIDE_IDX_FRONT][0][0] 
                self.col[SIDE_IDX_LEFT][1][1]   = self.col[SIDE_IDX_FRONT][0][1] 
                self.col[SIDE_IDX_FRONT][0][0]  = self.col[SIDE_IDX_RIGHT][1][0]
                self.col[SIDE_IDX_FRONT][0][1]  = self.col[SIDE_IDX_RIGHT][0][0]
                self.col[SIDE_IDX_RIGHT][0][0]  = mem_side_back[0] 
                self.col[SIDE_IDX_RIGHT][1][0]  = mem_side_back[1]
            else:   #3  #False = CCW
                self.col[SIDE_IDX_BACK][1][0]   = self.col[SIDE_IDX_RIGHT][0][0] 
                self.col[SIDE_IDX_BACK][1][1]   = self.col[SIDE_IDX_RIGHT][1][0] 
                self.col[SIDE_IDX_RIGHT][0][0]  = self.col[SIDE_IDX_FRONT][0][1]
                self.col[SIDE_IDX_RIGHT][1][0]  = self.col[SIDE_IDX_FRONT][0][0]
                self.col[SIDE_IDX_FRONT][0][0]  = self.col[SIDE_IDX_LEFT][0][1]
                self.col[SIDE_IDX_FRONT][0][1]  = self.col[SIDE_IDX_LEFT][1][1]
                self.col[SIDE_IDX_LEFT][0][1]   = mem_side_back[1] 
                self.col[SIDE_IDX_LEFT][1][1]   = mem_side_back[0] 
        elif side_idx == SIDE_IDX_RIGHT:
            mem_side_back = [0] * 2
            mem_side_back[0] = self.col[SIDE_IDX_BACK][1][1]
            mem_side_back[1] = self.col[SIDE_IDX_BACK][0][1]
            if rotate_dir:    #3 CW
                self.col[SIDE_IDX_BACK][1][1]   = self.col[SIDE_IDX_UP][1][1] 
                self.col[SIDE_IDX_BACK][0][1]   = self.col[SIDE_IDX_UP][0][1]
                self.col[SIDE_IDX_UP][1][1]     = self.col[SIDE_IDX_FRONT][1][1] 
                self.col[SIDE_IDX_UP][0][1]     = self.col[SIDE_IDX_FRONT][0][1] 
                self.col[SIDE_IDX_FRONT][0][1]  = self.col[SIDE_IDX_DOWN][1][0]
                self.col[SIDE_IDX_FRONT][1][1]  = self.col[SIDE_IDX_DOWN][0][0]
                self.col[SIDE_IDX_DOWN][0][0]   = mem_side_back[0] 
                self.col[SIDE_IDX_DOWN][1][0]   = mem_side_back[1]
            else:    #9  CCW
                self.col[SIDE_IDX_BACK][1][1]   = self.col[SIDE_IDX_DOWN][0][0] 
                self.col[SIDE_IDX_BACK][0][1]   = self.col[SIDE_IDX_DOWN][1][0]
                self.col[SIDE_IDX_DOWN][0][0]   = self.col[SIDE_IDX_FRONT][1][1] 
                self.col[SIDE_IDX_DOWN][1][0]   = self.col[SIDE_IDX_FRONT][0][1] 
                self.col[SIDE_IDX_FRONT][1][1]  = self.col[SIDE_IDX_UP][1][1]
                self.col[SIDE_IDX_FRONT][0][1]  = self.col[SIDE_IDX_UP][0][1]
                self.col[SIDE_IDX_UP][1][1]     = mem_side_back[0]
                self.col[SIDE_IDX_UP][0][1]     = mem_side_back[1] 
        elif side_idx == SIDE_IDX_FRONT:
            mem_side_top = self.col[SIDE_IDX_UP][1].copy()
            #mem_side_top = [0] * 2
            #mem_side_top[0] = self.col[SIDE_IDX_UP][1][0]
            #mem_side_top[1] = self.col[SIDE_IDX_UP][1][1]
            if rotate_dir:    #action=2
                #self.col[SIDE_IDX_UP][1][0]     = self.col[SIDE_IDX_LEFT][1][0]
                #self.col[SIDE_IDX_UP][1][1]     = self.col[SIDE_IDX_LEFT][1][1]
                self.col[SIDE_IDX_UP][1]        = self.col[SIDE_IDX_LEFT][1]
                #self.col[SIDE_IDX_LEFT][1][0]   = self.col[SIDE_IDX_DOWN][1][0]
                #self.col[SIDE_IDX_LEFT][1][1]   = self.col[SIDE_IDX_DOWN][1][1]
                self.col[SIDE_IDX_LEFT][1]      = self.col[SIDE_IDX_DOWN][1]
                #self.col[SIDE_IDX_DOWN][1][0]    = self.col[SIDE_IDX_RIGHT][1][0]
                #self.col[SIDE_IDX_DOWN][1][1]    = self.col[SIDE_IDX_RIGHT][1][1]
                self.col[SIDE_IDX_DOWN][1]      = self.col[SIDE_IDX_RIGHT][1]
                #self.col[SIDE_IDX_RIGHT][1][0]  = mem_side_top[0]
                #self.col[SIDE_IDX_RIGHT][1][1]  = mem_side_top[1]
                self.col[SIDE_IDX_RIGHT][1]     = mem_side_top
            else:    #action=5
                #self.col[SIDE_IDX_UP][1][0]    = self.col[SIDE_IDX_RIGHT][1][0]
                #self.col[SIDE_IDX_UP][1][1]    = self.col[SIDE_IDX_RIGHT][1][1]
                self.col[SIDE_IDX_UP][1]       = self.col[SIDE_IDX_RIGHT][1]
                #self.col[SIDE_IDX_RIGHT][1][0]  = self.col[SIDE_IDX_DOWN][1][0]
                #self.col[SIDE_IDX_RIGHT][1][1]  = self.col[SIDE_IDX_DOWN][1][1]
                self.col[SIDE_IDX_RIGHT][1]     = self.col[SIDE_IDX_DOWN][1]      
                #self.col[SIDE_IDX_DOWN][1][0]    = self.col[SIDE_IDX_LEFT][1][0]
                #self.col[SIDE_IDX_DOWN][1][1]    = self.col[SIDE_IDX_LEFT][1][1]
                self.col[SIDE_IDX_DOWN][1]       = self.col[SIDE_IDX_LEFT][1]
                #self.col[SIDE_IDX_LEFT][2][0]   = mem_side_top[0]
                #self.col[SIDE_IDX_LEFT][2][1]   = mem_side_top[1]
                self.col[SIDE_IDX_LEFT][1]      = mem_side_top

    #helper for finding the inverse action (TOP/CW --> TOP/CCW)
    def inverse_action(self, action):
        if action < 3:
            return (action + 3)
        elif action >= 3 and action < self.num_actions():
            return (action - 3)

    #returns the inverse actions list
    def get_inverse_action_list(self):
        conj_actions_list = []
        for action in self.actions_list:
            conj_actions_list.append(self.inverse_action(action))
        return (conj_actions_list)

    #returns the total number of applicable actions
    def num_actions(self):
        return(6)

    #empties the action list
    def clear_action_list(self):
        self.actions_list.clear()     
  
    #print readable action list in short notation U / U'
    def print_action_list(self, max_line_len=100):
        szText = ""
        cnt = 0
        for action in self.get_action_list():
            szNew = "%s, " % action_dict_short[action]
            szText += szNew
            cnt += len(szNew)   #increment by len of added string
            #max line_len reached --> print this info, and start new line
            if(cnt >= max_line_len):
                print("%s" % szText[:-2], end="\n") #skip last 2 items
                cnt = 0
                szText = ""
        #print remaining 
        if(len(szText) > 0): 
            print("%s" % szText[:-2], end="\n") #skip last 2 items           


    #simple actions, less math, less if/else
    def actions_simple(self, action):
        if action==0:         self.rotate_simple(SIDE_IDX_UP,    ROT_DIR_CW)
        elif action==3:       self.rotate_simple(SIDE_IDX_UP,    ROT_DIR_CCW)
        elif action==1:       self.rotate_simple(SIDE_IDX_RIGHT, ROT_DIR_CW)
        elif action==4:       self.rotate_simple(SIDE_IDX_RIGHT, ROT_DIR_CCW)
        elif action==2:       self.rotate_simple(SIDE_IDX_FRONT, ROT_DIR_CW)
        elif action==5:       self.rotate_simple(SIDE_IDX_FRONT, ROT_DIR_CCW)
        else: return
        #append 
        self.actions_list.append(action)

    #save to .JSON file
    def save_to_file(self, filename):
        #open the file, if exists replaces all content
        with open(filename, 'w', encoding='utf-8') as outfile:
            mapped_values = deepcopy(self.col).tolist()
            for i in range(6):
                for j in range(self.N_DIM):
                    for k in range(self.N_DIM):
                        item = mapped_values[i][j][k]    
                        mapped_values[i][j][k] = color_dict[item] 
            #define data to write
            values_dict = {
                side_dict[SIDE_IDX_UP]       : mapped_values[SIDE_IDX_UP],
                side_dict[SIDE_IDX_FRONT]    : mapped_values[SIDE_IDX_FRONT],
                side_dict[SIDE_IDX_BACK]     : mapped_values[SIDE_IDX_BACK],
                side_dict[SIDE_IDX_RIGHT]    : mapped_values[SIDE_IDX_RIGHT],
                side_dict[SIDE_IDX_LEFT]     : mapped_values[SIDE_IDX_LEFT],
                side_dict[SIDE_IDX_DOWN]     : mapped_values[SIDE_IDX_DOWN],
                }

            actions_short = self.get_action_list(notation="short")
            outdata = {
                'col'                 : values_dict, #np array must be converted to list
                'actions_dict_short'  : action_dict_short,
                'color_dict'          : color_dict,
                'actions_list'        : self.actions_list,
                'actions_list_short'  : actions_short,
                }
            json.dump(outdata, outfile, separators=(',', ':'), sort_keys=False, indent=2)    

    def load_from_file(self, filename):
        #exists = os.path.isfile(filename)
        with open(filename, 'r', encoding='utf-8') as infile:
            indata = json.loads(infile.read())
            values              = indata['col']
            self.actions_list   = indata['actions_list']

            mapped_values = [None] * 6
            mapped_values[SIDE_IDX_UP]     = values[side_dict[SIDE_IDX_UP]]
            mapped_values[SIDE_IDX_FRONT]  = values[side_dict[SIDE_IDX_FRONT]]
            mapped_values[SIDE_IDX_BACK]   = values[side_dict[SIDE_IDX_BACK]]
            mapped_values[SIDE_IDX_RIGHT]  = values[side_dict[SIDE_IDX_RIGHT]]
            mapped_values[SIDE_IDX_LEFT]   = values[side_dict[SIDE_IDX_LEFT]]
            mapped_values[SIDE_IDX_DOWN]   = values[side_dict[SIDE_IDX_DOWN]]

            for i in range(6):
                for j in range(self.N_DIM):
                    for k in range(self.N_DIM):
                        item = mapped_values[i][j][k]   #item is a string eg. "white"                        
                        
                        found_key = None
                        #search for value in dict and return key, 
                        #key is the numberic äquivalent to the color, value is the string representation of color
                        for key,value in color_dict.items():
                            if value == item:
                                found_key = key
                                break
                        #colorstring not found  in color_dict --> replace with None
                        if(found_key == None):
                            print("Import error: Color '%s' on side: '%s'[%d][%d] not recognized" % (item, side_dict[i],j,k))
                            mapped_values[i][j][k] = -1 
                        else:
                            mapped_values[i][j][k] = found_key 
                        
            self.col[SIDE_IDX_UP]     = mapped_values[SIDE_IDX_UP]
            self.col[SIDE_IDX_FRONT]  = mapped_values[SIDE_IDX_FRONT]
            self.col[SIDE_IDX_BACK]   = mapped_values[SIDE_IDX_BACK]
            self.col[SIDE_IDX_RIGHT]  = mapped_values[SIDE_IDX_RIGHT]
            self.col[SIDE_IDX_LEFT]   = mapped_values[SIDE_IDX_LEFT]
            self.col[SIDE_IDX_DOWN]   = mapped_values[SIDE_IDX_DOWN]

    """
    corners are numbered starting from up/left position in clockwise direction
    continuing on down/left in clockwise direction
    get all corners or a single corner location given by <location> from 0 to 7
    optional sorting color values, <sort>=True
    """
    def get_corner(self, location=None, sort=False):
        corner_block  = [[0]*3 for _ in range(8)]  
        corner_block_idx = self.N_DIM - 1

        corner_block[0][0] = self.col[SIDE_IDX_UP][0][0]
        corner_block[0][1] = self.col[SIDE_IDX_BACK][corner_block_idx][0]
        corner_block[0][2] = self.col[SIDE_IDX_LEFT][0][corner_block_idx]

        corner_block[1][0] = self.col[SIDE_IDX_UP][0][corner_block_idx]
        corner_block[1][1] = self.col[SIDE_IDX_BACK][corner_block_idx][corner_block_idx]
        corner_block[1][2] = self.col[SIDE_IDX_RIGHT][0][0]

        corner_block[2][0] = self.col[SIDE_IDX_UP][corner_block_idx][corner_block_idx]
        corner_block[2][1] = self.col[SIDE_IDX_FRONT][0][corner_block_idx]
        corner_block[2][2] = self.col[SIDE_IDX_RIGHT][corner_block_idx][0]

        corner_block[3][0] = self.col[SIDE_IDX_UP][corner_block_idx][0]
        corner_block[3][1] = self.col[SIDE_IDX_FRONT][0][0]
        corner_block[3][2] = self.col[SIDE_IDX_LEFT][corner_block_idx][corner_block_idx]

        corner_block[4][0] = self.col[SIDE_IDX_DOWN][0][0]
        corner_block[4][1] = self.col[SIDE_IDX_BACK][0][corner_block_idx]
        corner_block[4][2] = self.col[SIDE_IDX_RIGHT][0][corner_block_idx]

        corner_block[5][0] = self.col[SIDE_IDX_DOWN][0][corner_block_idx]
        corner_block[5][1] = self.col[SIDE_IDX_BACK][0][0]
        corner_block[5][2] = self.col[SIDE_IDX_LEFT][0][0]

        corner_block[6][0] = self.col[SIDE_IDX_DOWN][corner_block_idx][corner_block_idx]
        corner_block[6][1] = self.col[SIDE_IDX_FRONT][corner_block_idx][0]
        corner_block[6][2] = self.col[SIDE_IDX_LEFT][corner_block_idx][0]

        corner_block[7][0] = self.col[SIDE_IDX_DOWN][corner_block_idx][0]
        corner_block[7][1] = self.col[SIDE_IDX_FRONT][corner_block_idx][corner_block_idx]
        corner_block[7][2] = self.col[SIDE_IDX_RIGHT][corner_block_idx][corner_block_idx]
        #requested sorted values
        if sort == True:
            for n in range(8):
                corner_block[n]      = np.sort(corner_block[n]).tolist()
        #requested a specific location
        if location: return corner_block[location]
        return corner_block

    #checks if cube is solved (each side has 4 identical colors, do not care about the side position )
    def done(self):
        results = []
        for side in self.col:
            col = side[0][0]            #color of first block
            comp = (side == col)        #numpy array compare returns N_DIM * N_DIM bools [True, false][True, false]
            result = np.all(comp)       #test if all elements are true - return single value, True means all colors identical on this side
            results.append(result)      
        final_result = np.all(results)  
        #print(results)
        print(final_result)
        return(final_result)

    
    def self_test(self):
        #print("Check consistency of data")
        #load color data for corner, no edge and no center blocks
        #edge has 3 visible sides

        #this is sorted validation data, that is derived from the original cube
        #it has to be identical with sorted data from any cube
        #this means that each corner has the correct combination of colours
        orig_cube           = tRubikCube()
        corner_block_valid  = orig_cube.get_corner(sort=True)
        
        #sorted data from actual cube
        corner_block        = self.get_corner(sort=True)
        #result buffer
        corner_result       = [False] * 8

        #inject error
        #corner_block_valid[2][0] = 2

        #multidimensional array search > the valid block (corner) is searched in ther actual cube (corners)
        #if the cube is turned the corners are at any positions
        for i in  range(8):
            valid_block = corner_block_valid[i]
            for j in  range(8):
                test_block = corner_block[j]
                
                #compare all 3 array elements of the corner block
                corner_compare = np.equal(valid_block, test_block)
                result = np.all(corner_compare)
                if(result == True) or (j == 7): #==7 just for last element debug print
                    corner_result[i] = True
                    print("corner #%02d:" %i + str(result))
                    break;

        #final result: all corner results must be true
        final_result = np.all(corner_result)
        print("final result: " + str(final_result))
        return(final_result)

#key=side index
#side_dict = {
#    SIDE_IDX_UP     : "up",
#    SIDE_IDX_DOWN   : "down",
#    SIDE_IDX_FRONT  : "front",
#    SIDE_IDX_BACK   : "back",
#   SIDE_IDX_LEFT   : "left",
#    SIDE_IDX_RIGHT  : "right"
#}    
    #
    
    def set_side(self, side_idx, col_data):
        self.col[side_idx] = col_data.copy()
        return
    
    def get_facemap(self, flatten = False):
        if flatten == False:
            return deepcopy(self.col)
        else:
            return deepcopy(self.col.flatten(order = "C"))

    def set_facemap(self, rcube_facemap):
        self.col = deepcopy(rcube_facemap)

def main():
    console_clear()
    console_color_enable()
    print("Testing Rubikscube 2x2x2")
    
    #increase size of console
    #os.system('mode con: cols=120 lines=60')  #12*4 +1
    #cube_algo_check()
    

    orig_cube = tRubikCube()
    orig_cube.done()
    corners = orig_cube.get_corner(sort = True)
    print(corners)
    #orig_cube.self_test()

#    orig_cube.save_to_file("test.json")
#    test_cube = tRubikCube()
#    test_cube.load_from_file("test.json")
#    orig_cube.print_2d()
#    orig_cube.done()


    test_cube = tRubikCube()
    #rotate the test cube
    test_cube.col[0] = 5
    test_cube.col[1] = 4
    test_cube.col[2] = 2
    test_cube.col[3] = 3
    test_cube.col[4] = 0
    test_cube.col[5] = 1
    corners = test_cube.get_corner(sort = True)
    print(corners)
    test_cube.self_test()
    test_cube.print_2d()


    exit()


    #testing UP side action
    orig_cube = tRubikCube()
    orig_cube.print_2d()
    orig_cube.done()

    orig_cube.actions_simple(ACT_IDX_U_CW)
    orig_cube.print_2d()
    orig_cube.done()

    orig_cube.actions_simple(ACT_IDX_U_CCW)
    orig_cube.actions_simple(ACT_IDX_U_CCW)
    orig_cube.print_2d()
    orig_cube.done()


    #testing RIGHT side action
    orig_cube = tRubikCube()
    orig_cube.print_2d()
    orig_cube.done()

    orig_cube.actions_simple(ACT_IDX_R_CW)
    orig_cube.print_2d()
    orig_cube.done()

    orig_cube.actions_simple(ACT_IDX_R_CCW)
    orig_cube.actions_simple(ACT_IDX_R_CCW)
    orig_cube.print_2d()
    orig_cube.done()

    #testing Front side action
    orig_cube = tRubikCube()
    orig_cube.print_2d()
    orig_cube.done()

    orig_cube.actions_simple(ACT_IDX_F_CW)
    orig_cube.print_2d()
    orig_cube.done()

    orig_cube.actions_simple(ACT_IDX_F_CCW)
    orig_cube.actions_simple(ACT_IDX_F_CCW)
    orig_cube.print_2d()
    orig_cube.done()


    blink_line("Cube Testing Done", 3, 0.3)
    print("Press Any Key to continue")
    input()

    #print 2D view of the cube on console    
    #it was changed due to weird color output to fill the whole cube-boundary box with black boxes
    #additional information added, edges and colors, mapping according to cube_col_array_index_map.xlsx

if __name__=="__main__":
  main()
