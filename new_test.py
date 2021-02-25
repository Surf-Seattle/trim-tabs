import RPi.GPIO as GPIO
import time
import sys

#Define GPIO pins to activate
Channel_List = (13,19,20,21,26,16)
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(Channel_List, GPIO.OUT)

#Assign extend and retract to GPIO pins
Port_ext = Channel_List[0]
Port_ret = Channel_List[1]
Stbd_ext = Channel_List[2]
Stbd_ret = Channel_List[3]
Center_ext = Channel_List[4]
Center_ret = Channel_List[5]

#total time to extend actuator
Extend_Time = 3.52
#time to ensure full retract
Home_Time = 4
#Define and initialize postion variable
port_position = 0
center_position = 0 
stbd_position = 0

print("Port_ext ", Port_ext)
print("Port_ret ", Port_ret)
print("Stbd_ext ", Stbd_ext)
print("Stbd_ret ", Stbd_ret)
print("Center_ext ", Center_ext)
print("Center_ret ", Center_ret)

def actuator(Channel, Duration):
    GPIO.output(Channel, True)
    print("Channel ", Channel, "on")
    time.sleep(Duration)
    GPIO.output(Channel, False)
    print("Channel ", Channel, "off")
    return;

def home():
    GPIO.output(Port_ret, True)
    time.sleep(Home_Time)
    GPIO.output(Port_ret, False)
    port_position = 0
#     GPIO.output(Center_ret, True)
#     time.sleep(Home_Time)
#     GPIO.output(Center_ret, False)
#     center_position = 0
    GPIO.output(Stbd_ret, True)
    time.sleep(Home_Time)
    GPIO.output(Stbd_ret, False)
    stbd_position = 0
    print("actuators home")
    return;



#Home the actuators
home()

# time.sleep(3)
# #move Port actuator
# actuator(Port_ext, Time)
# time.sleep(3)
# actuator(Port_ext, T2)
# time.sleep(3)
# actuator(Port_ret, Time)
# #add delay between actuators
# time.sleep(1)

#move Starboard actuator
# actuator(Stbd_ext, Time)
# time.sleep(3)
# actuator(Stbd_ext, T2)
# time.sleep(3)
# actuator(Stbd_ret, Time)
#     except KeyboardInterrupt as e:
#         time.sleep(3)
block = True
#main program
while block:
        try:
# input postion to move port actuator to    
            new_port_position = input("enter Port position, example 35:\n")
                         
            new_port_position = int(new_port_position)
            print(f'You entered {new_port_position}')
            #make sure input is in a valid range between 0  to 100
            if new_port_position > 100:
                new_port_position = 100
            if new_port_position < 0:
                new_port_position = 0

#determine direction actuator needs to move, 

            if new_port_position > port_position:
                    # determine the change in actuator position
                    delta = new_port_position - port_position
                    #determine time required to reach new position
                    relay_time = (delta/100*Extend_Time)
                    print(f'relay time {relay_time}')
                    #Turn on the correct relay
                    actuator(Port_ext, relay_time)
                    # store position 
                    port_position = new_port_position
                    print(f'Port position {port_position}')
# Determine Direction actuator needs to move                   
            if new_port_position < port_position:

                    delta = port_position - new_port_position
                    relay_time = (delta/100*Extend_Time)
                    print(f'relay time {relay_time}')

                    actuator(Port_ret, relay_time)
                    port_position = new_port_position
                    print(f'Port position {port_position}')
                    
# input postion to move Starboard actuator to
                    
            new_stbd_position = input("enter Starboard position, example 35:\n")
            
            new_stbd_position = int(new_stbd_position)
            print(f'You entered {new_stbd_position}')
            #make sure input is in a valid range between 0  to 100
            if new_stbd_position > 100:
                new_stbd_position = 100
            if new_stbd_position < 0:
                new_stbd_position = 0

#determine direction actuator needs to move, 

            if new_stbd_position > stbd_position:
                    # determine the change in actuator position
                    delta = new_stbd_position - stbd_position
                    #determine time required to reach new position
                    relay_time = (delta/100*Extend_Time)
                    print(f'relay time {relay_time}')
                    #Turn on the correct relay
                    actuator(Stbd_ext, relay_time)
                    # store position 
                    stbd_position = new_stbd_position
                    print(f'Starboard position {stbd_position}')
# Determine Direction actuator needs to move                   
            if new_stbd_position < stbd_position:

                    delta = stbd_position - new_stbd_position
                    relay_time = (delta/100*Extend_Time)
                    print(f'relay time {relay_time}')

                    actuator(Stbd_ret, relay_time)
                    stbd_position = new_stbd_position
                    print(f'Starbard position {stbd_position}')
# The above if statements need to be repeated for starboard actuators 
        except KeyboardInterrupt as e:
            print("Quit the Loop")
            GPIO.cleanup()
            sys.exit()
            

      