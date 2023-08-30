import cv2
import mediapipe as mp
import csv
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_hands = mp.solutions.hands

# Initialize video capture
cap = cv2.VideoCapture(0)

############### ETHAN'S IDEA ###############
# using the middle, index, and ring finger as RGB values
# calibrate the distance by having the user open and close their hand to measure max distance from palm to finger
# use the distance to determine the color intensity value for each finger
############################################

# Create black image to show curvy lines
height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
# 18 because 18 is a foot and a half in inches
pixels_per_in_y = height / 12
width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
# this may look a little squished because the width isn't a perfect square with the height, but it's close enough
pixels_per_in_x = width / 16
print("width", width)
print("height", height)
black_image = np.zeros((height, width, 3), dtype=np.uint8)

# initialize the last location of the right fingertip and set the list of locations to empty
last_location = None
list_of_locations = []


def determine_hand_position(index_up, middle_up, ring_up, pinky_up, thumb_up):
    ########## IMPORTANT INFO ##########
    ## THE COLORS ARE IN FORMAT BGR, NOT RGB
    ## SO (0, 0, 255) IS RED, NOT BLUE
    ####################################
    if not index_up and not middle_up and not ring_up and not pinky_up and not thumb_up:
        print("fist")
        return (0, 0, 0)
    elif index_up and not middle_up and not ring_up and not pinky_up and not thumb_up:
        print("one")
        return (0, 0, 255)
    elif index_up and middle_up and not ring_up and not pinky_up and not thumb_up:
        print("two")
        return (0, 165, 255)
    elif index_up and middle_up and not ring_up and not pinky_up and thumb_up:
        print("three")
        return (0, 255, 255)
    elif index_up and middle_up and ring_up and pinky_up and not thumb_up:
        print("four")
        return (0, 255, 0)
    elif index_up and middle_up and ring_up and pinky_up and thumb_up:
        print("five")
        return (255, 0, 0)
    elif not index_up and middle_up and ring_up and pinky_up and not thumb_up:
        print("six")
        return (130, 0, 75)
    elif index_up and not middle_up and ring_up and pinky_up and not thumb_up:
        print("seven")
        return (211, 0, 148)
    elif index_up and middle_up and not ring_up and pinky_up and not thumb_up:
        print("eight")
        return (255, 0, 255)
    elif index_up and middle_up and ring_up and not pinky_up and not thumb_up:
        print("nine")
        return (255, 255, 0)
    elif not index_up and not middle_up and not ring_up and not pinky_up and thumb_up:
        print("ten")
        return (255, 255, 255)
    else:
        return (0, 0, 0)


#
# ==============================================================================================================
# MAIN PROGRAM
# ==============================================================================================================
#

with mp_hands.Hands(static_image_mode=False,
                    max_num_hands=2,
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5) as hands:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            break

        # Flip the image horizontally for a later selfie-view display
        image = cv2.flip(image, 1)

        # Convert the image from BGR color (which OpenCV uses) to RGB color
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        results = hands.process(image)

        if results.multi_hand_landmarks:
            # make sure there are two hands in the frame
            if len(results.multi_handedness) != 1:
                # determine which hand is which
                handedness = results.multi_handedness[0].classification[0].label
                if handedness == "Left":
                    left_hand_landmarks = results.multi_hand_landmarks[0]
                    right_hand_landmarks = results.multi_hand_landmarks[1]
                else:
                    left_hand_landmarks = results.multi_hand_landmarks[1]
                    right_hand_landmarks = results.multi_hand_landmarks[0]

                # Get all hand landmarks
                left_hand_landmarks_all = list(
                    np.array([[landmark.x, landmark.y] for landmark in left_hand_landmarks.landmark]))
                right_hand_landmarks_all = list(
                    np.array([[landmark.x, landmark.y] for landmark in right_hand_landmarks.landmark]))

                # get the x and y coordinates of the entire left hand fingertips
                left_index_finger_tip = left_hand_landmarks_all[8]
                left_middle_finger_tip = left_hand_landmarks_all[12]
                left_ring_finger_tip = left_hand_landmarks_all[16]
                left_pinky_finger_tip = left_hand_landmarks_all[20]
                left_thumb_tip = left_hand_landmarks_all[4]
                left_base_of_palm = left_hand_landmarks_all[0]

                # we only need the right index fingertip
                right_index_finger_tip = right_hand_landmarks_all[8]

                # Convert normalized point coordinates to pixel coordinates
                left_index_pixel_location = (
                    int(left_index_finger_tip[0] * image.shape[1]), int(left_index_finger_tip[1] * image.shape[0]))
                left_middle_pixel_location = (
                    int(left_middle_finger_tip[0] * image.shape[1]), int(left_middle_finger_tip[1] * image.shape[0]))
                left_ring_pixel_location = (
                    int(left_ring_finger_tip[0] * image.shape[1]), int(left_ring_finger_tip[1] * image.shape[0]))
                left_pinky_pixel_location = (
                    int(left_pinky_finger_tip[0] * image.shape[1]), int(left_pinky_finger_tip[1] * image.shape[0]))
                left_thumb_pixel_location = (
                    int(left_thumb_tip[0] * image.shape[1]), int(left_thumb_tip[1] * image.shape[0]))
                left_palm_pixel_location = (
                    int(left_base_of_palm[0] * image.shape[1]), int(left_base_of_palm[1] * image.shape[0]))

                right_index_pixel_location = (
                    int(right_index_finger_tip[0] * image.shape[1]), int(right_index_finger_tip[1] * image.shape[0]))

                # determine which fingers are being held up
                if left_index_pixel_location[1] < left_palm_pixel_location[1] - 360:
                    index_finger_up = True
                else:
                    index_finger_up = False
                if left_middle_pixel_location[1] < left_palm_pixel_location[1] - 380:
                    middle_finger_up = True
                else:
                    middle_finger_up = False
                if left_ring_pixel_location[1] < left_palm_pixel_location[1] - 380:
                    ring_finger_up = True
                else:
                    ring_finger_up = False
                if left_pinky_pixel_location[1] < left_palm_pixel_location[1] - 340:
                    pinky_finger_up = True
                else:
                    pinky_finger_up = False
                if left_thumb_pixel_location[0] > left_palm_pixel_location[0] + 320:
                    thumb_finger_up = True
                else:
                    thumb_finger_up = False

                ############ DELETE THE FOLLOWING LINES WHEN YOU ARE DONE ################

                # font = cv2.FONT_HERSHEY_SIMPLEX
                # font_scale = 1.0
                # font_thickness = 2
                # # Calculate the size of the text
                # text_size, _ = cv2.getTextSize("____ finger up", font, font_scale, font_thickness)
                #
                # # Calculate the position of the text
                # text_width, text_height = text_size
                # text_x = (width - text_width) // 2
                # text_y = (height + text_height) // 2
                # og_text_y = text_y
                #
                # # Draw the text on the image
                # for j in range(5):
                #     text_y = og_text_y
                #     text = ""
                #     text_visible = False
                #     if j == 0:
                #         if index_finger_up:
                #             text = "index finger up"
                #             text_visible = True
                #     elif j == 1:
                #         if middle_finger_up:
                #             text = "middle finger up"
                #             text_visible = True
                #         text_y += 30
                #     elif j == 2:
                #         if ring_finger_up:
                #             text = "ring finger up"
                #             text_visible = True
                #         text_y += 60
                #     elif j == 3:
                #         if pinky_finger_up:
                #             text = "pinky finger up"
                #             text_visible = True
                #         text_y += 90
                #     elif j == 4:
                #         if thumb_finger_up:
                #             text = "thumb finger up"
                #             text_visible = True
                #         text_y += 120
                #     cv2.putText(black_image, text, (text_x, text_y), font, font_scale, (0, 255, 0),
                #                 font_thickness, cv2.LINE_AA)
                #     if not text_visible:
                #         # If the text is not visible, fill the text region with black
                #         cv2.rectangle(black_image, (text_x, text_y - text_height),
                #                       (text_x + text_width, text_y + 3),
                #                       (0, 0, 0), -1)
                    ############################################################################

                    # Draw points on the black image where the hand landmarks are
                    # color is BGR
                    color = determine_hand_position(index_finger_up, middle_finger_up, ring_finger_up, pinky_finger_up,
                                                    thumb_finger_up)
                    if color != (0, 0, 0):
                        cv2.circle(black_image, right_index_pixel_location, 3, color, -1)
                        x_in_inches = right_index_pixel_location[0] / pixels_per_in_x
                        y_in_inches = right_index_pixel_location[1] / pixels_per_in_y
                        list_of_locations.append(((x_in_inches, y_in_inches), color))
                        if last_location != None:
                            cv2.line(black_image, last_location, right_index_pixel_location, color, 3)
                        last_location = right_index_pixel_location
                    else:
                        # we still want to save the points where their finger was so that we can easily follow it
                        # by having the color to black, the light *should* just turn off anyways
                        x_in_inches = right_index_pixel_location[0] / pixels_per_in_x
                        y_in_inches = right_index_pixel_location[1] / pixels_per_in_y
                        list_of_locations.append(((x_in_inches, y_in_inches), color))
                        last_location = None

        # Show black image with curvy lines instead of original image
        cv2.imshow('MediaPipe Hands', black_image)

        if cv2.waitKey(2) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()

print(list_of_locations, "\n\n")

filename = "fingerpaint_data_test.csv"

# Open the CSV file in write mode
with open(filename, 'w', newline='') as file:
    writer = csv.writer(file)

    # Write the header row
    writer.writerow(["NEEDED DATA", "X", "Y", "B", "G", "R"])
    unique_list = [x for i, x in enumerate(list_of_locations) if x not in list_of_locations[:i]]
    print(unique_list)
    # Write each data row
    for point, color in unique_list:
        x, y = point
        b, g, r = color
        writer.writerow(["", x, y, b, g, r])

print(f"CSV file '{filename}' has been created.")
