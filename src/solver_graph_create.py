import os
import sys
import time
#import numpy as np

from copy import copy, deepcopy
from RubiksCube_2x2x2 import tRubikCube
from helpers import *
from iterate_tools import tIterate

def main():
    #enable colored text on console outputs
    os.system('color') 
    #increase size of console
    os.system('mode con: cols=160 lines=60')  #12*4 +1

    orig_cube = tRubikCube()
    num_actions = orig_cube.num_actions()
    max_depth = 1

    test_iterator = tIterate(max_depth, num_actions, 0)
    iter_steps    = test_iterator.get_total_num()
    iter_func     = test_iterator.generator()
    print("\nIteration Depth:   %d" %max_depth, end= "")
    print("  Num_Actions:       %d" %num_actions, end="")
    print("  Num_Iterations:    %d" %iter_steps)
    
    iterations = []
    test_iterator = tIterate(max_depth, num_actions, 0)
    for iter in range(iter_steps):
        iteration_step = next(iter_func)
        iterations.append(copy(iteration_step))
    print(str(iterations))
    del(test_iterator)

    return

if __name__=="__main__":
    main()
