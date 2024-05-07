import pygame
import sys
import random

# Initialize Pygame
pygame.init()

# Set up some constants
WIDTH, HEIGHT = 800, 600
FPS = 60

# Set up the display
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Set up the clock
clock = pygame.time.Clock()

# Set up the rectangle
rect = pygame.Rect(WIDTH // 2, HEIGHT // 2, 200, 100)

# Create a list of smaller rectangles within the main rectangle
rects = [{"rect": pygame.Rect(rect.x + i*10, rect.y + j*10, 10, 10), "falling": False} for i in range(rect.width//10) for j in range(rect.height//10)]

def draw_rects():
    global rects
    if rects:
        # Randomly select a rectangle and set its "falling" value to True
        for _ in range(5):
            rects[random.randint(0, len(rects) - 1)]["falling"] = True

        # Update the y-coordinate of all rectangles that are falling
        for r in rects:
            if r["falling"]:
                r["rect"].y += 10  # Adjust this value to change the speed of falling

                # If the rectangle has fallen off the screen, remove it from the list
                if r["rect"].y > HEIGHT:
                    rects.remove(r)

    if len(rects) < 50:
        for rect in rects:
            rect["falling"] = True

    for r in rects:
        pygame.draw.rect(screen, (57, 57, 57), r["rect"])

def main():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        screen.fill((0, 0, 0))
        draw_rects()

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()