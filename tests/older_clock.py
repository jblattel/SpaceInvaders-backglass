#!/bin/python
#Simple clock program to run the basic mechanics
import pygame
import os
import signal
import sys
import time
import datetime
import random
import threading

from Adafruit_LED_Backpack import SevenSegment
from MCP230xx import Adafruit_MCP230XX

#label the channels (MCP2)
channel_0 = 0xFFFE
channel_1 = 0xFFFD
channel_2 = 0xFFFB
channel_3 = 0xFFF7
channel_4 = 0xFFEF
channel_5 = 0xFFDF
channel_6 = 0xFFBF
channel_7 = 0xFF7F
channel_8 = 0xFEFF
channel_9 = 0xFDFF
channel_10 = 0xFBFF
channel_11 = 0xF7FF
channel_12 = 0xEFFF
channel_13 = 0xDFFF
channel_14 = 0xBFFF
channel_15 = 0x7FFF

#label the channels (MCP2)
chan_0 = 0xFFFE #Eyes
chan_1 = 0xFFFD #Game Over
chan_2 = 0xFFFB #High Score
chan_3 = 0xFFF7 #Shoot Again
chan_4 = 0xFFEF #Ball In Play
chan_5 = 0xFFDF #Main Title
chan_6 = 0xFFBF #Tilt
chan_7 = 0xFF7F #Match
chan_8 = 0xFEFF #NOT CONNECTED
chan_9 = 0xFDFF #Right Shoulder
chan_10 = 0xFBFF #Left Hip
chan_11 = 0xF7FF #Head
chan_12 = 0xEFFF #Left Hand
chan_13 = 0xDFFF #Right Hand
chan_14 = 0xBFFF #Right Hip
chan_15 = 0x7FFF #Left Shoulder


#initialize sounds for use in clock
pygame.mixer.init()
tick = pygame.mixer.Sound("sounds/clock-tick1.wav")
bewareil = pygame.mixer.Sound("sounds/bewareil.wav")

# Create control objects for the LED's
mcp = Adafruit_MCP230XX(address = 0x26, num_gpios = 16) # MCP23017
mcp2 = Adafruit_MCP230XX(address = 0x25, num_gpios = 16) # MCP23017

# Set everything to OFF
mcp.write16(0xFFFF)
mcp2.write16(0xFFFF)

# Turn all the I/O to OUTPUT ONLY
z = 0
while (z <= 15):
  mcp.config(z,mcp.OUTPUT)
  mcp2.config(z,mcp2.OUTPUT)
  z += 1
# Setup all the Light Channels for the backbox as a List:
#channel = [0xFFFE,0xFFFD,0xFFFB,0xFFF7,0xFFEF,0xFFDF,0xFFBF,0xFF7F,0xFEFF,0xFDFF,0xFBFF,0xF7FF,0xEFFF,0xDFFF,0xBFFF,0x7FFF]

#turn on the Alien and Main Title
mcp2.write16(channel_5 & channel_9 & channel_10 & channel_11 & channel_12 & channel_13 & channel_14 & channel_15)


# Create a display with a specific I2C address and/or bus.
display_upper_left = SevenSegment.SevenSegment(address=0x73, busnum=1)
display_upper_right = SevenSegment.SevenSegment(address=0x72, busnum=1)
display_lower_right = SevenSegment.SevenSegment(address=0x70, busnum=1)
display_lower_left = SevenSegment.SevenSegment(address=0x71, busnum=1)

# Initialize the screens
display_upper_left.begin()
display_upper_right.begin()
display_lower_right.begin()
display_lower_left.begin()

# Catch ctrl+D to stop program quasi gracefully
def signal_handler(signal, frame):
  print('Time to clear the Grid')
  display_lower_right.clear()
  display_lower_left.clear()
  display_upper_right.clear()
  display_upper_left.clear()
  mcp.write16(0xFFFF)
  mcp2.write16(0xFFFF)

  display_upper_right.write_display()
  display_upper_left.write_display()
  display_lower_left.write_display()
  display_lower_right.write_display()
  t1.stop()
  sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.pause

def light_chase(chasex):
    count = 0
    while (count <= chasex):
        mcp.write16(channel_14 & channel_10 & channel_8 & channel_12)
        time.sleep(.1);
        mcp.write16(channel_13 & channel_9 & channel_11 & channel_15)
        time.sleep(.1);
        mcp.write16(channel_1 & channel_3 & channel_7 & channel_2)
        time.sleep(.1);
        mcp.write16(channel_4 & channel_0 & channel_6 & channel_5)
        time.sleep(.1);
        count += 1
        mcp.write16(ALLOFF)


def setLess(string):
    #print(string)
    hour = time.strftime("%H",time.localtime())
    minute = time.strftime("%M",time.localtime())
    #second = time.strftime("%S",time.localtime())
    day = time.strftime("%d",time.localtime())
    month = time.strftime("%m",time.localtime())
    year = time.strftime("%Y",time.localtime())

    #write the month and day 
    display_lower_left.print_number_str(month,justify_right=False)
    display_lower_left.print_number_str(day,justify_right=True)
    display_lower_left.write_display()
     
    #write the year
    display_lower_right.print_number_str(year,justify_right=True)
    display_lower_right.write_display()

    #write the minute hour and seconds
    display_upper_left.print_number_str(minute,justify_right=True)
    display_upper_left.print_number_str(hour,justify_right=False)
    #display_upper_right.write_display()
    display_upper_left.write_display()
    

def setTime():
  currentsec = 0
  lastsec = 0
  sec = 3600
  while True: 
    #hour = time.strftime("%H",time.localtime())
    #minute = time.strftime("%M",time.localtime())
    second = time.strftime("%S",time.localtime())
    #day = time.strftime("%d",time.localtime())
    #month = time.strftime("%m",time.localtime())
    #year = time.strftime("%Y",time.localtime())
    #print(day,"/",month,"/",year)
    #print(hour,":",minute,":",second)

    #write the month and day 
    #display_lower_left.print_number_str(month,justify_right=False)
    #display_lower_left.print_number_str(day,justify_right=True)
    #display_lower_left.write_display()
     
    #write the year
    #display_lower_right.print_number_str(year,justify_right=True)
    #display_lower_right.write_display()

    #write the minute hour and seconds
    #display_upper_left.print_number_str(minute,justify_right=True)
    #display_upper_left.print_number_str(hour,justify_right=False)
    display_upper_right.print_number_str(sec,justify_right=False)
    display_upper_right.write_display()
    #display_upper_left.write_display()
    
    #blink the eyes and the colon
    if ((int(second) % 2) == 1):
        colon = True
        display_upper_left.set_colon(colon)
        #tick.play()
        mcp2.output(0,0)
    else:
        colon = False
        display_upper_left.set_colon(colon)
        #tick.play()
        mcp2.output(0,1)



    #check to see if a second has passed
    currentsec = second
    #print(currentsec, " < is current second")
    if (int(currentsec) == 00):
        #print("we hit zero seconds setting lastsec to ZERO")
        lastsec = 0
        #do soemthing when we hit 0 
    elif (currentsec == lastsec):
        pass
        #print("we are in the current second")
        #still in the current second
    elif ((int(currentsec) - int(lastsec)) >= 1):
            #one second has past
            #print(lastsec, " < This is the last second")
            lastsec = currentsec
            #print(lastsec, " < This is the last second after setting it")

            if (sec == 0):
                #do the animation
                sec = 3600
                print("do a little dance")
            else:
                sec = sec - 1
                setLess("setting it")
                #print(sec)

               


t1 = threading.Thread(target=setTime)
#t2 = threading.Thread(target=setLess)




if __name__ == '__main__':
    t1.setDaemon(True)
    t1.start()
    while True:
        pass
    
