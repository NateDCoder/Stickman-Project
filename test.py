import pygame
import math

# Pygame setup
pygame.init()
screen = pygame.display.set_mode((250, 250))
running = True

angle = 0
speed = 0.05
num_arms = 5
radius = 100

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    pygame.draw.circle(screen, (255, 0, 255), (125, 125), 105)
    # Draw the spiral
    for i in range(num_arms):
        angle_offset = 2 * math.pi / num_arms * i + angle
        for j in range(200):
            r = j / 200 * radius
            theta = j / 200 * 2 * math.pi + angle_offset
            x = int(r * math.cos(theta)) + 125
            y = int(r * math.sin(theta)) + 125
            pygame.draw.circle(screen, (128, 0, 128), (x, y), 5)
    pygame.draw.circle(screen, (0, 0, 0), (125, 125), 105, width=10)
    # Update the display
    pygame.display.flip()

    # Increase the angle
    angle += speed
    pygame.time.delay(16)

# Quit Pygame
pygame.quit()