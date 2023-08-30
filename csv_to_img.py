import pandas as pd
import pygame
import ast

# CSV TO RECONSTRUCT
CSV_NAME = 'dragon_3.csv'

# Screen dimensions
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480

# machine dimensions
MACHINE_WIDTH = 16
MACHINE_HEIGHT = 12

# Function to draw the points on the screen
def draw_points(screen, x,y,r,g,b):
    for x,y,r,g,b in zip(x,y,r,g,b):
        pygame.draw.circle(screen, (r, g, b), (x, y), 2)  # Change the radius as needed

# Main function
def main():
    my_data = pd.read_csv(CSV_NAME, header=None)
    my_data = my_data[1:]
    fixed_data = []
    for row in my_data.iterrows():
        # convert x and y from machine to screen
        row = row[1]
        x = float(row[0]) * (SCREEN_WIDTH / MACHINE_WIDTH)
        y = float(row[1]) * (SCREEN_HEIGHT / MACHINE_HEIGHT)
        fixed_data.append((str(x), str(y), *row[2:]))
        # print("X:", row[0], " Y:", row[1], " R:", row[2], " G:", row[3], " B:", row[4])
    print(fixed_data)

    column_names = ['x', 'y', 'R', 'G', 'B']
    df = pd.DataFrame(fixed_data, columns=column_names)
    print(df)
    # breakpoint()
    # Extract coordinates and colors from the DataFrame
    x_coordinates = df.apply(lambda row: ast.literal_eval(row['x']), axis=1)
    y_coordinates = df.apply(lambda row: ast.literal_eval(row['y']), axis=1)
    r_colors = df.apply(lambda row: ast.literal_eval(row['R']), axis=1)
    g_colors = df.apply(lambda row: ast.literal_eval(row['G']), axis=1)
    b_colors = df.apply(lambda row: ast.literal_eval(row['B']), axis=1)

    # Initialize Pygame
    pygame.init()
    screen_size = (SCREEN_WIDTH, SCREEN_HEIGHT)  # Set your desired screen size
    screen = pygame.display.set_mode(screen_size)
    pygame.display.set_caption('Drawing from CSV')

    # Main loop
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Clear the screen
        screen.fill((0, 0, 0))  # Set the background color

        # Draw the points
        draw_points(screen, x_coordinates, y_coordinates, r_colors, g_colors, b_colors)

        # Update the display
        pygame.display.flip()

    # Quit Pygame
    pygame.quit()

if __name__ == "__main__":
    main()
