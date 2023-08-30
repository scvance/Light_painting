import pygame
import csv
import multiprocessing
import tkinter as tk
from tkinter import colorchooser

# Screen dimensions
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

def main():
    pygame.init()

    # Set the width and height of the screen (width, height).
    size = (SCREEN_WIDTH, SCREEN_HEIGHT)
    screen = pygame.display.set_mode(size)

    pygame.display.set_caption("Drawing App")

    # Store points
    data = []

    # Loop until the user clicks the close button.
    done = False

    # Used to manage how fast the screen updates.
    clock = pygame.time.Clock()

    # Track if the mouse button is being held down
    drawing = False

    # Initialize color
    color = WHITE

    pipe_recv, pipe_send = None, None
    proc = None

    # -------- Main Program Loop -----------
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            # Mouse button down event
            if event.type == pygame.MOUSEBUTTONDOWN:
                drawing = True
                if color != BLACK:  # Not the first black dot
                    pos = pygame.mouse.get_pos()
                    pygame.draw.circle(screen, color, pos, 2)
                    data.append(((pos[0]/640) * 16, (pos[1]/480) * 12, *color))

            # Mouse button up event
            if event.type == pygame.MOUSEBUTTONUP:
                drawing = False
                pos = pygame.mouse.get_pos()
                data.append(((pos[0]/640) * 16, (pos[1]/480) * 12, 0,0,0))

            # Mouse motion event
            if event.type == pygame.MOUSEMOTION:
                if drawing:
                    pos = pygame.mouse.get_pos()
                    pygame.draw.circle(screen, color, pos, 2)
                    data.append(((pos[0]/640) * 16, (pos[1]/480) * 12, *color))

            # Key press event
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_c:  # If 'c' key is pressed
                    pipe_recv, pipe_send = multiprocessing.Pipe(False)
                    proc = multiprocessing.Process(target=choose_color, args=(pipe_send,))
                    proc.start()  # Open color chooser

        # If color chooser process ended and a color was picked
        if proc and not proc.is_alive() and pipe_recv.poll():
            color = pipe_recv.recv()


        # --- update the screen with what we've drawn.
        pygame.display.flip()

        # --- Limit to 60 frames per secondm
        clock.tick(60)

    # When we break out of the loop, write data to a CSV file
    with open('drawing.csv', 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["X", "Y", "R", "G", "B"])
        for row in data:
            writer.writerow(row)

    # Close the window and quit.
    pygame.quit()

def choose_color(pipe):
    # Get color from tkinter colorchooser
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    color_code = colorchooser.askcolor(title ="Choose color")
    root.destroy()

    # If a color was selected, send it through the pipe
    if color_code[1] is not None:
        pipe.send(color_code[0])

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
