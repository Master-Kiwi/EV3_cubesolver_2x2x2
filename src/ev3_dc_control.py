import os
import time
from thread_task import Sleep
import ev3_dc as ev3
from ev3_dc.constants import PORT_B

#EV3_mac_address = '00:16:53:7F:D7:C4'
EV3_mac_address = '00:16:53:46:E9:BB'

#CAGE LEFT/RIGHT
MOTOR_CAGE_GEAR_RATIO          = 36/12
MOTOR_CAGE_NORMAL_POSITION     = int(0  * MOTOR_CAGE_GEAR_RATIO)
MOTOR_CAGE_ROTATE_POSITION     = int(90 * MOTOR_CAGE_GEAR_RATIO)
MOTOR_CAGE_ROTATE_OVERTURN     = int(20 * MOTOR_CAGE_GEAR_RATIO)

#CRADLE 
MOTOR_CRADLE_GEAR_RATIO         = 36/12
MOTOR_CRADLE_NORMAL_POSITION    = int(0   * MOTOR_CRADLE_GEAR_RATIO)  # = 0
MOTOR_CRADLE_ROTATE_POSITION    = int(-90 * MOTOR_CRADLE_GEAR_RATIO)

#ELEVATOR UP/DOWN
MOTOR_ELEVATOR_UPPER_POSITION       = 1215       #slightly pushed against top of cage
MOTOR_ELEVATOR_TURN_LAYER_POSITION  = 840        #allows turning layers
MOTOR_ELEVATOR_TURN_CUBE_POSITION   = 400        #allows turning cube (slightly lift above the cradle)
MOTOR_ELEVATOR_LOWER_POSITION       = 0          #rest position

MOTOR_TIME_DELAY = 0.1


class tCubeRobot:
    
    def __init__(self, ev3_mac_address, verbosity=0):
        self.verbosity = verbosity
        self.cube_robot = ev3.EV3(protocol=ev3.USB, host = EV3_mac_address)
        self.cube_robot.sleep=10
        sensors = self.cube_robot.sensors_as_dict
        #print("protocol USB's default sync_mode is " + str(self.cube_robot.sync_mode))
        #print(sensors)
        assert(sensors[ev3.PORT_A_SENSOR] == ev3.EV3_LARGE_MOTOR), 'no motor at port A'
        assert(sensors[ev3.PORT_B_SENSOR] == ev3.EV3_LARGE_MOTOR), 'no motor at port B'
        assert(sensors[ev3.PORT_C_SENSOR] == ev3.EV3_LARGE_MOTOR), 'no motor at port C'
        self.print("All Motors connected")
        self.print(" Motor at Port A (large) = CAGE")
        self.print(" Motor at Port B (large) = CRADLE")
        self.print(" Motor at Port C (large) = ELEVATOR")

        #get motor control handles
        self.MOTOR_CAGE         = ev3.Motor(ev3_obj=self.cube_robot, port=ev3.PORT_A)
        #print(MOTOR_CAGE.motor_type)
        self.MOTOR_CRADLE       = ev3.Motor(ev3_obj=self.cube_robot, port=ev3.PORT_B)
        #print(self.MOTOR_CRADLE.motor_type)
        self.MOTOR_ELEVATOR     = ev3.Motor(ev3_obj=self.cube_robot, port=ev3.PORT_C)
        #print(self.MOTOR_ELEVATOR.motor_type)

        #unlock brake 
        self.unlock_brake()
        
        #default motor movement settings
        #CAGE ROTATION LEFT/RIGHT
        self.MOTOR_CAGE.speed = 100
        self.MOTOR_CAGE.ramp_up = 0
        self.MOTOR_CAGE.ramp_down = 0
        self.MOTOR_CAGE.ramp_up_time = 0
        self.MOTOR_CAGE.ramp_down_time = 0

        #CRADLE ROTATION 
        self.MOTOR_CRADLE.speed = 100
        self.MOTOR_CRADLE.ramp_up = 0
        self.MOTOR_CRADLE.ramp_down = 0
        self.MOTOR_CRADLE.ramp_up_time = 0
        self.MOTOR_CRADLE.ramp_down_time = 0

        #ELEVATOR UP/DOWN
        self.MOTOR_ELEVATOR.speed = 100
        self.MOTOR_ELEVATOR.ramp_up = 0
        self.MOTOR_ELEVATOR.ramp_down = 0
        self.MOTOR_ELEVATOR.ramp_up_time = 0
        self.MOTOR_ELEVATOR.ramp_down_time = 0
    
    #overloaded print function
    # output dependent on verbosity level
    def print(self, msg):
        if(self.verbosity != 0): print(msg)

    def GetBattery(self): 
        bat = self.cube_robot.battery

        #per cell: 1.0V > 0% / 1.3V > 100%  (for nimh rechargeable battery)
        #per cell: 1.0V > 0% / 1.5V > 100%  (for alkali non rechargeable battery)
        #6 cells in series used. 6.0V > 0% 
        bat_min = 1.0 * 6  #=6.0V
        #bat_max = 1.3 * 6  #=7.8V  
        bat_max = 1.5 * 6  #=9.0V  
        bat_voltage=bat.voltage #actual measurement
        
        #calculate percent from voltage
        bat_percent = ((bat_voltage - bat_min) / (bat_max-bat_min)) * 100
        if(bat_percent < 0):    bat_percent=0
        if(bat_percent > 100):  bat_percent=100

        self.print(" Battery Voltage:   %.3f V" % bat_voltage)
        self.print(" Discharge current: %.3f A" % bat.current)        
        self.print(" Battery SOC:       %.1f " % bat_percent + str("%"))

        #return(bat.voltage, bat.current, bat_percent)
        return(bat_percent)

    #
    def cradle_move_to(self, position="rotated"):
        self.print("cradle_rotate_to(position=%s): Start" % position)
        if(position == "rotated"):   motor_pos = MOTOR_CRADLE_ROTATE_POSITION
        else:                        motor_pos = MOTOR_CRADLE_NORMAL_POSITION
        #rotate the cradle to desired position
        movement_plan = (
            self.MOTOR_CRADLE.move_to(motor_pos, brake=True) +
            Sleep(MOTOR_TIME_DELAY) +
            self.MOTOR_CRADLE.stop_as_task(brake=True)
        )
        movement_plan.start(thread=False)    
        total_moved = abs(MOTOR_CRADLE_ROTATE_POSITION)
        self.print("cradle_rotate_to(): Job Done, total moved = %d°" %total_moved)
        return(total_moved)

    #turn the whole rubikscube around the X-axis (left-to-right / horizontal axis)
    #CW = front to up
    #CCW = front to down
    def X_turn(self, direction, num_rot):
        total_moved = 0
        if(num_rot > 2): return
        if(num_rot < 1): return
        
        self.print("X_turn(): Start")

        if(direction == "CW"):       #front to up
            for i in range(num_rot):
                #up to front
                movement_plan = (
                    self.MOTOR_CRADLE.move_to(MOTOR_CRADLE_ROTATE_POSITION, brake=True) +           #cradle rotate
                    Sleep(MOTOR_TIME_DELAY) +
                    self.MOTOR_ELEVATOR.move_to(MOTOR_ELEVATOR_TURN_CUBE_POSITION, brake=True) +    #elev up
                    Sleep(MOTOR_TIME_DELAY) +
                    self.MOTOR_CRADLE.move_to(MOTOR_CRADLE_NORMAL_POSITION, brake=True) +           #cradle normal
                    Sleep(MOTOR_TIME_DELAY) +
                    self.MOTOR_ELEVATOR.move_to(MOTOR_ELEVATOR_LOWER_POSITION, brake=True) +        #elev down
                    Sleep(MOTOR_TIME_DELAY) +
                    self.MOTOR_ELEVATOR.stop_as_task(brake=True) +                                  #unlock brake
                    self.MOTOR_CRADLE.stop_as_task(brake=True)
                )
                movement_plan.start(thread=False) 
        
        if(direction == "CCW"):       #front to down
            for i in range(num_rot):
                movement_plan = (
                    self.MOTOR_ELEVATOR.move_to(MOTOR_ELEVATOR_TURN_CUBE_POSITION, brake=True) +    #elev up
                    Sleep(MOTOR_TIME_DELAY) +
                    self.MOTOR_CRADLE.move_to(MOTOR_CRADLE_ROTATE_POSITION, brake=True) +           #cradle rotate
                    Sleep(MOTOR_TIME_DELAY) +
                    self.MOTOR_ELEVATOR.move_to(MOTOR_ELEVATOR_LOWER_POSITION, brake=True) +        #elev down
                    Sleep(MOTOR_TIME_DELAY) +
                    self.MOTOR_CRADLE.move_to(MOTOR_CRADLE_NORMAL_POSITION, brake=True) +           #cradle normal
                    Sleep(MOTOR_TIME_DELAY) +
                    self.MOTOR_ELEVATOR.stop_as_task(brake=True) +                              #unlock brake
                    self.MOTOR_CRADLE.stop_as_task(brake=True)
                )
                movement_plan.start(thread=False)        

        total_moved = (2*MOTOR_ELEVATOR_TURN_CUBE_POSITION + 2*abs(MOTOR_CRADLE_ROTATE_POSITION))*num_rot
        self.print("X_turn(): Job Done, total moved = %d°" %total_moved)
        return(total_moved)

    #turn the whole rubikscube around the Y-axis (down-to-up / vertical axis)
    #CW =  front to left
    #CCW = front to right
    def Y_turn(self, direction, num_rot):       
        if(num_rot > 2): return
        if(num_rot < 1): return
        self.print("Y_turn(): Start")
        
        rotate_pos      = (MOTOR_CAGE_ROTATE_POSITION * num_rot)
        if(direction == "CCW"):
            rotate_pos = -rotate_pos
            #self.print("Rotate the cube %d times - counter clockwise" %num_rot)    
        
        movement_plan = (
            self.MOTOR_ELEVATOR.move_to(MOTOR_ELEVATOR_UPPER_POSITION, brake=True) +    #elev up
            Sleep(MOTOR_TIME_DELAY) +
            self.MOTOR_CAGE.move_by(rotate_pos, brake=True) +                           #cage rotate (multiple times)
            Sleep(MOTOR_TIME_DELAY) +
            self.MOTOR_ELEVATOR.move_to(MOTOR_ELEVATOR_LOWER_POSITION, brake=True) +    #elev down
            Sleep(MOTOR_TIME_DELAY) +
            self.MOTOR_ELEVATOR.stop_as_task(brake=True) +                             #unlock brake
            self.MOTOR_CAGE.stop_as_task(brake=True)                                   #unlock brake
        )
        movement_plan.start(thread=False)    
        total_moved = 2*MOTOR_ELEVATOR_UPPER_POSITION + abs(rotate_pos)
        self.print("Y_turn(): Job Done, total moved = %d°" %total_moved)
        return(total_moved)
    

    #turn the whole rubikscube around the Z-Axis (front-to-back axis)
    #CW =  up to right
    #CCW = up to left
    def Z_turn(self, direction, num_rot):   
        total_moved = 0
        if(num_rot > 2): return
        if(num_rot < 1): return
        
        #this will change the axis, Z -> Y
        total_moved += self.cradle_move_to("rotated")         #cradle - rotate (front to up)

        #turn around Y axis (cube is t urning arund Z-axis)
        total_moved += self.Y_turn(direction, num_rot)

        #this will change the axis, Y -> Z
        total_moved += self.cradle_move_to("normal")          #cradle - rotate (up to front)
        self.print("Z_turn(): Job Done, total moved = %d°" %total_moved)
        return(total_moved)

    
    '''----------------------------------------CUBE MODFICICATION FUNCTIONS----------------------------------------------
    ALWAYS PRESERVE THE CUBES ORIENTATION
        machines mechanics allows layer turning only on up or front layer
        to turn the left layer and preserve the cubes orientation (example):
            H-Turn the cube (left to front)
            turn front layer
            H-Turn the cube (front to left)

    '''   
    
    #primary cuby modification function
    #least amount of machine moves
    def rot_up_layer(self, direction, num_rot):
        total_moved = 0
        if(num_rot > 2): return
        if(num_rot < 1): return
        self.print("rot_up_layer(dir=%s, num=%d): Start" %(direction, num_rot))

        overturn_ratio  = MOTOR_CAGE_ROTATE_OVERTURN
        rotate_pos      = (MOTOR_CAGE_ROTATE_POSITION * num_rot) 

        if(direction == "CCW"):
            overturn_ratio = -overturn_ratio  
            rotate_pos = -rotate_pos
        #self.print("  target position=%d°  overturn ratio=%d°" %(rotate_pos/MOTOR_CAGE_GEAR_RATIO, overturn_ratio/MOTOR_CAGE_GEAR_RATIO))        

        movement_plan = (
            self.MOTOR_ELEVATOR.move_to(MOTOR_ELEVATOR_TURN_LAYER_POSITION, brake=True) +         #elev up
            Sleep(MOTOR_TIME_DELAY) +
            
            #rotate with Overturn and then back to normal position (mechanical tolerance)
            self.MOTOR_CAGE.move_by(rotate_pos + overturn_ratio, brake=True) +              #cage rotate by (rot + overtutn)
            Sleep(MOTOR_TIME_DELAY) +   
            self.MOTOR_CAGE.move_by(-overturn_ratio, brake=True) +                          #cage rotate by (-overturn)
            Sleep(MOTOR_TIME_DELAY) +
            #this might cause the absolute position of the cage-axis to run away in one direction

            self.MOTOR_ELEVATOR.move_to(MOTOR_ELEVATOR_UPPER_POSITION, brake=True) +        #elev push to top
            Sleep(MOTOR_TIME_DELAY) +
            self.MOTOR_ELEVATOR.move_to(MOTOR_ELEVATOR_LOWER_POSITION, brake=True) +        #elev down
            Sleep(MOTOR_TIME_DELAY) +
            
            #self.MOTOR_CAGE.move_by(-rotate_pos, brake=True) +                               #cage orig position
            #Sleep(MOTOR_TIME_DELAY) +

            self.MOTOR_ELEVATOR.stop_as_task(brake=True) +
            self.MOTOR_CAGE.stop_as_task(brake=True)
        )
        movement_plan.start(thread=False)    
        total_moved = 2*MOTOR_ELEVATOR_UPPER_POSITION + abs(rotate_pos) + 2*abs(overturn_ratio)

        self.print("rot_up_layer(): Job Done, total moved = %d°" %total_moved)
        return(total_moved)
    
    #2nd order MODIFICATION ACTION: rotate front layer
    #preserve cubes state
    def rot_down_layer(self, direction, num_rot):
        self.print("rot_down_layer(dir=%s, num=%d): Start" %(direction, num_rot))
        total_moved = 0
        total_moved += self.X_turn("CW", 2)                            #down to up
        total_moved += self.rot_up_layer(direction, num_rot)          #rotate up layer
        total_moved += self.X_turn("CCW", 2)                           #up to down
        self.print("rot_down_layer(): Job Done, total moved = %d°" %total_moved)
        return(total_moved)


    #2nd order MODIFICATION ACTION: rotate front layer
    #preserve cubes state
    #could be a bit more effective
    def rot_front_layer(self, direction, num_rot):
        self.print("rot_front_layer(dir=%s, num=%d): Start" %(direction, num_rot))
        total_moved = 0
        #total_moved += self.X_turn("CW", 1)                            #front to up
        total_moved += self.cradle_move_to("rotated")                  #cradle - rotate (front to up)
        total_moved += self.rot_up_layer(direction, num_rot)          #rotate up layer
        total_moved += self.cradle_move_to("normal")                   #cradle - rotate (up to front)
        #total_moved += self.X_turn("CCW", 1)                           #up to front
        self.print("rot_front_layer(): Job Done, total moved = %d°" %total_moved)
        return(total_moved)

    #2nd order MODIFICATION ACTION: rotate back layer
    #preserve cubes state
    def rot_back_layer(self, direction, num_rot):
        self.print("rot_back_layer(dir=%s, num=%d): Start" %(direction, num_rot))
        total_moved = 0
        total_moved += self.X_turn("CCW", 1)                           #back to up
        total_moved += self.rot_up_layer(direction, num_rot)          #rotate the up layer
        total_moved += self.X_turn("CW", 1)                            #up to back
        self.print("rot_back_layer(): Job Done, total moved = %d°" %total_moved)
        return(total_moved)
        

    #2nd order MODIFICATION ACTION: rotate left layer
    #preserve cubes state
    def rot_left_layer(self, direction, num_rot):
        self.print("rot_left_layer(dir=%s, num=%d): Start" %(direction, num_rot))
        total_moved = 0
        total_moved += self.Y_turn("CCW", 1)                           #left to front
        total_moved += self.rot_front_layer(direction, num_rot)        #rotate the front layer
        total_moved += self.Y_turn("CW", 1)                            #front to left
        self.print("rot_left_layer(): Job Done, total moved = %d°" %total_moved)
        return(total_moved)

    #2nd order MODIFICATION ACTION: rotate right side of the cube
    #preserve cubes state
    def rot_right_layer(self, direction, num_rot):
        self.print("rot_right_layer(dir=%s, num=%d): Start" %(direction, num_rot))
        total_moved = 0
        total_moved += self.Y_turn("CW", 1)                            #right to front
        total_moved += self.rot_front_layer(direction, num_rot)        #rotate the front layer
        total_moved += self.Y_turn("CCW", 1)                           #front to right
        self.print("rot_right_layer(): Job Done, total moved = %d°" %total_moved)
        return(total_moved)


    
  

    #unlock brake 
    def unlock_brake(self):
        self.MOTOR_CAGE.stop(brake=False)
        self.MOTOR_CRADLE.stop(brake=False)
        self.MOTOR_ELEVATOR.stop(brake=False)  


'''MOVEMENT SCORES 2x2x2(sum of all motor movements in motor-axis degree)

cube layer turning actions  (WITH PRESERVATION OF CUBE STATE)
                                    num=1       num=2       cube code
rot_up_layer(CW/CCW, num):          2820°       3090°       U/U' U2
rot_down_layer(CW/CCW, num):        8180°       8450°       D/D' D2
rot_front_layer(CW/CCW, num):       3360°       3630°       F/F' F2
rot_back_layer(CW/CCW, num):        5500°       5770°       B/B' B2     
rot_left_layer(CW/CCW, num):        8760°       9030°       L/L' L2
rot_right_layer(CW/CCW, num):       8760°       9030°       R/R' R2
best to use half.turn metric with U/F/L or U/F/R

cube-turning around actions 
                                    num=1       num=2
X_turn(CW/CCW, num):                1340°       2680°           
Y_turn(CW/CCW, num):                2700°       2970°
Z_turn(CW/CCW, num):                3240°       3510°


'''
def main():
    
    robot = tCubeRobot(EV3_mac_address, verbosity=1)
    #print(cube_robot.system)
    
    for i in range(2):
        robot.GetBattery()
        time.sleep(0.2)
    

    '''#robot.rot_up_layer("CW", 1)
    robot.rot_up_layer("CCW", 2)
    print(" ")

    #robot.rot_down_layer("CCW", 1)
    robot.rot_down_layer("CW", 2)
    print(" ")

    #robot.rot_front_layer("CW", 1)
    robot.rot_front_layer("CCW", 2)
    print(" ")

    #robot.rot_back_layer("CCW", 1)
    robot.rot_back_layer("CW", 2)
    print(" ")

    #robot.rot_left_layer("CW", 1)
    robot.rot_left_layer("CCW", 2)
    print(" ")
   
    #robot.rot_right_layer("CCW", 1)
    robot.rot_right_layer("CW", 2)
    print(" ")'''


    robot.X_turn("CW", 1)   #down to front
    #robot.X_turn("CCW", 1)   #up to front
    print(" ")

    robot.Y_turn("CW", 1)   #right to front
    #robot.Y_turn("CCW", 1)   #left to front
    print(" ")

    robot.Z_turn("CW", 1)   #left to up        
    #robot.Z_turn("CCW", 1)   #right to up        
    print(" ")


    robot.X_turn("CW", 2)   #down to front
    #robot.X_turn("CCW", 1)   #up to front
    print(" ")

    robot.Y_turn("CW", 2)   #right to front
    #robot.Y_turn("CCW", 1)   #left to front
    print(" ")

    robot.Z_turn("CW", 2)   #left to up        
    #robot.Z_turn("CCW", 1)   #right to up        
    print(" ")

    
    #print("show R ")
    #robot.Y_turn("CW", 1)   #show B
    #print("show B ")
    #robot.Y_turn("CW", 1)   #show L
    #print("show L ")
    #robot.Y_turn("CW", 1)   #show F
    #print("show F ")
    #robot.X_turn()          #show D
    #print("show D ")
    #robot.Y_turn("CW", 2)   #show U
    #print("show U ")
    time.sleep(0.5)
    robot.unlock_brake()





if __name__=="__main__":
  main()