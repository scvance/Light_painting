import RPi.GPIO as GPIO
import pandas as pd
import time

# df = pd.read_csv("./fingerpaint_data.csv", sep=',', encoding='latin-1')
df = pd.read_csv("./baseball09.csv", sep=',', encoding='latin-1')



# Define the GPIO pins
V_SPIN = 17
V_DPIN = 27
H_SPIN = 22
H_DPIN = 23
#H_RELAY = 24
V_RELAY = 16
LED_PINS = (19, 13, 18) # Blue, Green, Red

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(V_DPIN, GPIO.OUT)
GPIO.setup(V_SPIN, GPIO.OUT)
GPIO.setup(V_RELAY, GPIO.OUT)
GPIO.setup(H_DPIN, GPIO.OUT)
GPIO.setup(H_SPIN, GPIO.OUT)
GPIO.setup(LED_PINS, GPIO.OUT)

# Setting up PWM, 100Hz frequency
pwmRed = GPIO.PWM(LED_PINS[0], 100)
pwmGreen = GPIO.PWM(LED_PINS[1], 100)
pwmBlue = GPIO.PWM(LED_PINS[2], 100)

# Starting PWM with 0% duty cycle
pwmRed.start(0)
pwmGreen.start(0)
pwmBlue.start(0)

# Define Global Variables
# start in the bottom left corner
CURR_XY = [0, 11.5]


# Define Functions
def set_led_colors(red, green, blue):
    pwmRed.ChangeDutyCycle(red * 100)
    pwmGreen.ChangeDutyCycle(green * 100)
    pwmBlue.ChangeDutyCycle(blue * 100)


def move_carriage(x, y):
    global CURR_XY
    new_x = x - CURR_XY[0]
    new_y = y - CURR_XY[1]
    if new_x < 0:
        dirH = GPIO.LOW
    else:
        dirH = GPIO.HIGH
    if new_y > 0:
        dirV = GPIO.HIGH
    else:
        dirV = GPIO.LOW
    # actually define num_steps_x and num_steps_y
    # according to some quick maths, the wheel diameter is 1 inch which means
    # the circumferance of the wheel is exactly pi inches.
    # given that one revolution is 200 steps, if we want to figure out the amount of steps
    # we need to travel in order to get to some number of inches, we have to do
    # 1/3.14 in order to get the percentage of a revolution 1 inch is. We determine that
    # it is 31.847% of a revolution. then we take 200 * .31847 to get 63.69 steps per inch
    # WARNING: IT IS POSSIBLE 200 STEPS DOES NOT == 1 REVOLUTION
    # due to gear ratio, there are 94 inches between the top and bottom of the machine.
    # this means that we are going to multiply our position by 7.84 so that we can get an
    # accurate position
    num_steps_x = abs(int(new_x * 63.69))
    num_steps_y = abs(int(new_y * 63.69 * 3.4))
    if (num_steps_y < 2 and num_steps_x < 2):
        return 1
    taken_steps_x = 0
    taken_steps_y = 0
    # set them directions
    GPIO.output([H_DPIN, V_DPIN], (dirH, dirV))

    while num_steps_y > taken_steps_y or num_steps_x > taken_steps_x:
        GPIO.output(V_RELAY, GPIO.HIGH)
        if num_steps_x > taken_steps_x and num_steps_y > taken_steps_y:
            # step the motor
            GPIO.output([H_SPIN, V_SPIN], (GPIO.HIGH, GPIO.HIGH))
            time.sleep(0.0008)
            GPIO.output([H_SPIN, V_SPIN], (GPIO.LOW, GPIO.LOW))
            time.sleep(0.0008)
            taken_steps_x += 1
            taken_steps_y += 1
        elif num_steps_y > taken_steps_y:
            GPIO.output(V_SPIN, GPIO.HIGH)
            time.sleep(0.0008)
            GPIO.output(V_SPIN, GPIO.LOW)
            time.sleep(0.0008)
            taken_steps_y += 1
        else:
            GPIO.output(H_SPIN, GPIO.HIGH)
            time.sleep(0.0008)
            GPIO.output(H_SPIN, GPIO.LOW)
            time.sleep(0.0008)
            taken_steps_x += 1
    GPIO.output(V_RELAY, GPIO.LOW)
    CURR_XY = [x, y]

for row in df.iterrows():
    try:
        move_carriage(row[1]['X'], row[1]['Y'])
        set_led_colors(row[1]['R'] / 255, row[1]['G'] / 255, row[1]['B'] / 255)
    except KeyboardInterrupt:
        # if the picture takes too long to draw, we will pause by keyboard interrupting
        # we need to set the colors to black so that we don't overexpose one point.
        set_led_colors(0,0,0)
        time.sleep(10)
    # time.sleep(50/1000) # if we don't have this delay then the next iteration of the loop
    # will immediately execute andthe majority of the time, you will never even see the light
    # because of this, we are delaying for one half of a second in order to see the light.

set_led_colors(0,0,0)
move_carriage(1, 11.8)
# Cleanup
pwmRed.stop()
pwmGreen.stop()
pwmBlue.stop()
GPIO.output(H_DPIN, GPIO.LOW)
GPIO.output(H_SPIN, GPIO.LOW)
GPIO.output(V_DPIN, GPIO.LOW)
GPIO.output(V_SPIN, GPIO.LOW)
GPIO.cleanup()

print("cleaned up")



