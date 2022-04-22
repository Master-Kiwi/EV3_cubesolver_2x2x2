import os
import sys
import time
#import numpy as np

from copy import copy, deepcopy
from RubiksCube_2x2x2 import tRubikCube
from helpers import *
from iterate_tools import tIterate

# A class to represent a graph object
class Graph:
    # Constructor
    def __init__(self, edges, n):
 
        # A list of lists to represent an adjacency list
        self.adjList = [[] for _ in range(n)]
 
        # add edges to the undirected graph
        for (src, dest) in edges:
            self.adjList[src].append(dest)
            self.adjList[dest].append(src)

"""def BFS(self, target_state=None, depth=1):
        if(target_state is None): 
            target_cube = tRubikCube()
            target_state = target_cube.get_facemap()

        all_actions = list(range(self.num_actions()))
        all_states = 1
        width = self.num_actions()
        for _ in range(depth):
            all_states = all_states * width
        
        
        graph = []
        
        parent_node = 0
        child_node = parent_node + 1
        
        num_childs = 0
        edges = []  
        for node in range(all_states):
            #edges for first depth
            edges.append((parent_node, child_node+num_childs))
            
            num_childs += 1
            if (num_childs == self.num_actions()):
                parent_node += 1
                child_node = parent_node + 1
                num_childs = 0
            
        return
"""

def main():
    #enable colored text on console outputs
    os.system('color') 
    #increase size of console
    os.system('mode con: cols=160 lines=60')  #12*4 +1

    orig_cube = tRubikCube()
    orig_cube.print_2d()
    num_actions = orig_cube.num_actions()
    max_depth = 2

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
