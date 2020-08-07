#!/usr/bin/env python3

import pygame
import time
import serial

#### Key map
# A = button_0
# B = button_1
# X = button_2
# Y = button_3
# LB = button_4
# RB = button_5
# View button = button_6
# Menu button = button_7
# Left stick = button_9
# Right stick = button_10
# D-pad = Hat 0 : (Right-Left, Up-Down)

# Left stick(Right-Left) = Axis_0
# Left stick(Down-Up) = Axis_1
# LT = Axis_2 (-1 - 1)
# Right stick(Right-Left) = Axis_3
# Right stick(Down-Up) = Axis_4
# RT = Axis_5 (-1 - 1)
#####
pygame.init()

# Loop until the user clicks the close button.
done = False

# Initialize the joysticks
pygame.joystick.init()

# -------- Main Program Loop -----------
while done == False:
    # EVENT PROCESSING STEP
    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop

        # Possible joystick actions: JOYAXISMOTION JOYBALLMOTION JOYBUTTONDOWN JOYBUTTONUP JOYHATMOTION
        # if event.type == pygame.JOYBUTTONDOWN:
        #     print("Joystick button pressed.")
        # if event.type == pygame.JOYBUTTONUP:
        #     print("Joystick button released.")

    # Get count of joysticks
    joystick_count = pygame.joystick.get_count()

    # For each joystick:
    for i in range(joystick_count):
        joystick = pygame.joystick.Joystick(i)
        joystick.init()

        # Get the name from the OS for the controller/joystick
        name = joystick.get_name()

        # Usually axis run in pairs, up/down for one, and left/right for
        # the other.
        axes = joystick.get_numaxes()

        PWM = ''
        for i in [0, 2, 5]:
            axis = joystick.get_axis(i)
            if i == 0:  # Left stick(Right-Left) -> steering 2bit
                axis = abs(int((axis + 1) / 2 * 98)) + 1
                axis = max(25, axis)
                axis = min(75, axis)
                PWM += str(axis // 10)
                PWM += str(axis % 10)
            elif i == 2:  # LT -> brake 2bit
                axis = abs(int((axis + 1) / 2 * 99))
                PWM += str(axis // 10)
                PWM += str(axis % 10)
            elif i == 5:  # RT -> gas pedal 2bit
                axis = abs(int((axis + 1) / 2 * 99))
                PWM += str(axis // 10)
                PWM += str(axis % 10)

        buttons = joystick.get_numbuttons()

        for i in [1]:
            button = joystick.get_button(i)

            if i == 1:  # B -> hand brake 1bit
                PWM += str(int(button))

        # Hat switch. All or nothing for direction, not like joysticks.
        # Value comes back in an array.
        hats = joystick.get_numhats()

        # for i in range(hats):
        #     hat = joystick.get_hat(i)

        PWM = (PWM + '\r\n').encode('utf-8')  # 2(steering)+2(brake)+2(gas pedal)+1(hand brake)+2bit

        print('steering00, brake00, gas pedal00, hand brake0\n  is: {}'.format(PWM))
        ser = serial.Serial("/dev/ttyUSB0", 115200)
        ser.write(PWM)
        time.sleep(0.05)
        ser.close()

# Close the window and quit.
# If you forget this line, the program will 'hang'
# on exit if running from IDLE.
pygame.quit()

