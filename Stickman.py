import pygame
import random
import time
import math
import sys
from balls import BallSimulation
from moviepy.editor import VideoFileClip

WIDTH = 800
HEIGHT = 500

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Labrynth")

world_offset = [0, 0]
world_size = [3200, 500]
# Interpolates between two points this is for the respawn animation
def interpolate(t, point1, point2):
    x = point1[0] + t * (point2[0] - point1[0])
    y = point1[1] + t * (point2[1] - point1[1])
    return (x, y)
class Particle:
    def __init__(self, position, size):
        self.x, self.y = position
        self.size = size
        self.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
        self.thickness = 1

    def display(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x - world_offset[0]), int(self.y - world_offset[1])), self.size, self.thickness)

    def move(self):
        self.size -= 0.1
        self.color = (self.color[0], self.color[1], self.color[2], self.size)

    def alive(self):
        return self.size > 0
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.frames_l = [pygame.image.load("./stickman/stick-L1.png"),
                         pygame.image.load("./stickman/stick-L2.png"),
                         pygame.image.load("./stickman/stick-L3.png"),
                         pygame.image.load("./stickman/stick-L4.png")]
        self.frames_r = [pygame.image.load("./stickman/stick-R1.png"),
                         pygame.image.load("./stickman/stick-R2.png"),
                         pygame.image.load("./stickman/stick-R3.png"),
                         pygame.image.load("./stickman/stick-R4.png")]
        self.image = self.frames_l[0]
        self.rect = self.image.get_rect(center=(WIDTH / 2, HEIGHT-100))
        self.size = self.image.get_size()
        self.position = [100, 445]
        self.velocity = [0, 0]
        self.gravity = 1
        self.jumping = False
        self.current_frame = 0
        self.last_time = time.time()
        self.respawn = False
        self.death_location = []
        self.death_time = 0
        self.friction = 0.85
        self.moving = False

        self.angle = 180
        self.scale = 1
        self.shrink_speed = 0.01
        self.rotation_speed = 6
        self.radius = 50
    def jump(self):
        if not self.jumping:
            self.jumping = True
            self.velocity[1] = -18

    def move(self, direction):
        self.moving = True
        if not self.jumping:
            if direction == 'Right':
                self.velocity[0] += 0.3
                self.velocity[0] = min(self.velocity[0], 7)
            if direction == 'Left':   
                self.velocity[0] += -0.3
                self.velocity[0] = max(self.velocity[0], -7)
        else:
            if direction == 'Right':
                self.velocity[0] += 0.15
                self.velocity[0] = min(self.velocity[0], 7)
            if direction == 'Left':   
                self.velocity[0] += -0.15
                self.velocity[0] = max(self.velocity[0], -7)

    def animate(self):
        now = time.time()
        if now - self.last_time > 0.05:
            self.last_time = now
            self.current_frame = (self.current_frame + int(self.velocity[0]/2)) % 4
        if self.jumping:
            if self.image in self.frames_l:
                self.image = self.frames_l[2]
            else:
                self.image = self.frames_r[2]
        elif self.velocity[0] < -0.5:
            self.image = self.frames_l[self.current_frame]
        elif self.velocity[0] > 0.5:
            self.image = self.frames_r[self.current_frame]
        else:
            self.current_frame = 1
            if self.image in self.frames_l:
                self.image = self.frames_l[1]
            else:
                self.image = self.frames_r[1]

    def update(self):
        if self.respawn:
            self.doRespawn()
            return
        self.animate()
        self.velocity[1] += self.gravity
        if self.velocity[1] > 10:
            self.velocity[1] = 10
        if not self.moving and not self.jumping:
            self.velocity[0] *= self.friction
            if abs(self.velocity[0]) < 0.1:
                self.velocity[0] = 0
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]

        if self.position[0] < self.size[0]/2:
            self.position[0] = self.size[0]/2
        
        if self.position[0] > world_size[0] - self.size[0]/2:
            self.position[0] = world_size[0] - self.size[0]/2
        
        if self.position[1] > world_size[1] - self.size[1]/2:
            self.respawn = True
            self.death_location = self.position.copy()
            self.death_time = 0
            self.position[1] = 10000000

        if 0 < world_offset[0]:
            self.rect.centerx = self.position[0] - world_offset[0]
        else:
            self.rect.centerx = self.position[0]
        if 0 < world_offset[1]:
            self.rect.centery = self.position[1] - world_offset[1]
        else:
            self.rect.centery = self.position[1]
    def doRespawn(self):
        new_point = interpolate(self.death_time, self.death_location, levels[current_level].player_start.copy())
        world_offset[0] = new_point[0] - WIDTH/2
        self.death_time += 0.01
        particles.append(Particle(new_point, random.randint(1, 5)))
        if self.death_time >= 1:
            world_offset[0] = 0
            self.respawn = False
            self.position = levels[current_level].player_start.copy()
    def portal_animation(self):
        global start_portal_animation
        if self.scale > 0:
            self.scale -= self.shrink_speed
            self.angle += self.rotation_speed
            self.radius -= self.rotation_speed/5
            if self.radius < 0:
                self.radius = 0
            self.position[0] = levels[current_level].end_point[0] + self.radius * math.cos(math.radians(self.angle))
            self.position[1] = levels[current_level].end_point[1] + self.radius * math.sin(math.radians(self.angle))
            self.rect.center = self.position[0] - world_offset[0], self.position[1] - world_offset[1]
            self.image = pygame.transform.rotozoom(self.frames_l[self.current_frame], self.angle, self.scale)
            self.rect = self.image.get_rect(center=self.rect.center)
            self.rect = self.image.get_rect(center=self.rect.center)
        else:
            self.position = levels[current_level].player_start.copy()
            self.scale = 1
            self.angle = 180
            self.radius = 50
            self.respawn = False
            self.jumping = False
            self.velocity = [0, 0]
            self.image = self.frames_l[0]
            self.rect = self.image.get_rect(center=(WIDTH / 2, HEIGHT-100))
            self.size = self.image.get_size()
            self.world_offset = [0, 0]
            start_portal_animation = False

        

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color):
        super().__init__()
        self.image = pygame.Surface((w, h))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.size = [w, h]
        self.position = [x, y]
    def collide(self, player:Player):
        if self.rect.colliderect(player.rect):
            overlapX = min(
                (player.position[0] + player.size[0]/2) - self.position[0], 
                (self.position[0] + self.size[0]) - (player.position[0] - player.size[0]/2))
            overlapY = min(
                (player.position[1] + player.size[1]/2) - self.position[1],
                self.position[1] + self.size[1] - (player.position[1] - player.size[1]/2))
            if overlapX < overlapY:
                if player.position[0] + player.size[0]/2 > self.position[0] + self.size[0]/2:
                    player.rect.left = self.rect.right
                    player.position[0] = player.rect.centerx + world_offset[0]
                    player.velocity[0] = 0
                else:
                    player.rect.right = self.rect.left
                    player.position[0] = player.rect.centerx + world_offset[0]
                    player.velocity[0] = 0
            else:
                if player.position[1] + player.size[1]/2 > self.position[1] + self.size[1]/2:
                    player.rect.top = self.rect.bottom
                    player.position[1] = player.rect.centery - world_offset[1]
                    player.velocity[1] = 0
                else:
                    player.rect.bottom = self.rect.top
                    player.position[1] = player.rect.centery - world_offset[1]
                    player.jumping = False
                    player.velocity[1] = 0
            
    def update(self):
        global world_offset
        self.rect.topleft = (self.position[0] - world_offset[0], self.position[1] - world_offset[1])
class LevelData:
    def __init__(self, level, platforms = [], player_start = [], end_point = []):
        self.level = level
        self.platforms = pygame.sprite.Group()
        self.player_start = player_start
        self.end_point = end_point
        for platform in platforms:
            self.platforms.add(Platform(*platform))
        self.portal_angle = 0
        self.portal_speed = 0.05
        self.background_color = (173, 216, 230)
    def update(self):
        for platform in self.platforms:
            platform.update()
            screen.blit(platform.image, platform.rect)
        pygame.draw.circle(screen, (255, 0, 255), (self.end_point[0] - world_offset[0], self.end_point[1] - world_offset[1]), 52)
        # Draw the portal
        for i in range(5):
            angle_offset = 2 * math.pi / 5 * i + self.portal_angle
            for j in range(200):
                r = j / 200 * 50
                theta = j / 200 * 2 * math.pi + angle_offset
                x = int(r * math.cos(theta)) + 125
                y = int(r * math.sin(theta)) + 125
                pygame.draw.circle(screen, (128, 0, 128), ((self.end_point[0] - world_offset[0]) + x - 125, (self.end_point[1] - world_offset[1]) + y - 125), 3)
        pygame.draw.circle(screen, (0, 0, 0), (self.end_point[0] - world_offset[0], self.end_point[1] - world_offset[1]), 52, width=5)
        self.portal_angle += self.portal_speed
    def draw(self):
        for platform in self.platforms:
            screen.blit(platform.image, platform.rect)
    def collide(self, player):
        for platform in self.platforms:
            platform.collide(player)
    def reach_end(self, player):
        if player.rect.colliderect(pygame.Rect(self.end_point[0] - world_offset[0] - 50, self.end_point[1] - world_offset[1] - 50, 100, 100)):
            return True
        return False
class Level1(LevelData):
    def __init__(self, level, platforms = [], player_start = [], end_point = []):
        super().__init__(level, platforms, player_start, end_point)
        self.background_color = (173, 216, 230)
        self.ball_pit = BallSimulation(770, 0, width=280, start_height=420, height=HEIGHT-40, screen=screen)
        self.ball_pit_2 = BallSimulation(1090, 0, width=1290, start_height=420, height=HEIGHT-40, screen=screen)
        self.ball_pit.initialize()
        self.ball_pit_2.initialize()
    def update(self):
        super().update()
        self.ball_pit.update_player_ball(player.position[0], player.position[1], player.velocity[0], player.velocity[1])
        self.ball_pit.run(world_offset)
        self.ball_pit_2.update_player_ball(player.position[0], player.position[1], player.velocity[0], player.velocity[1])
        self.ball_pit_2.run(world_offset)
    
levels = [
    Level1(
              1,
              [
                (0, world_size[1]-40, world_size[0], 40, (0, 255, 0)), 
                (500, 415, 80, 20, (255, 255, 255)), 
                (720, 350, 50, 110, (255, 255, 255)), 
                (770, 380, 75, 25, (255, 255, 255)),
                (990, 320, 60, 20, (255, 255, 255)),
                (1050, 320, 40, 140, (255, 255, 255)),
                (1300, 280, 100, 30, (255, 255, 255)),
                (1650, 270, 100, 30, (255, 255, 255)),
                (2000, 250, 100, 30, (255, 255, 255)),
                (2380, 220, 30, 240, (255, 255, 255)),
              ],
              [100, 445],
              [3000, 400]
            )
]
current_level = 0
player = Player()
particles = []
jumpDebounce = True
def handle_input():
    global jumpDebounce
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.move('Left')
    if keys[pygame.K_RIGHT]:
        player.move('Right')
    if keys[pygame.K_UP] and jumpDebounce:
        player.jump()
        jumpDebounce = False
    if not keys[pygame.K_UP]:
        jumpDebounce = True
    if not any(keys):
        player.moving = False

def update_world_offset(old_x_position):
    world_offset[0] += player.position[0] - old_x_position
    world_offset[1] += player.velocity[1]

    if world_offset[0] < 0 or player.position[0] < WIDTH/2:
        world_offset[0] = 0
    if world_offset[1] < 0 or player.position[1] < HEIGHT/2:
        world_offset[1] = 0
    
    if world_offset[0] > world_size[0] - WIDTH or player.position[0] > world_size[0] - WIDTH/2:
        world_offset[0] = world_size[0] - WIDTH

    if world_offset[1] > world_size[1] - HEIGHT or player.position[1] > world_size[1] - HEIGHT/2:
        world_offset[1] = world_size[1] - HEIGHT
       
start_screen = VideoFileClip('./stickman/Start Screen.mp4')
def play_start_screen():
    while True:
        for t in start_screen.iter_frames():
            # Get the dimensions of the frame
            frame_dims = (t.shape[1], t.shape[0])
            
            frame_image = pygame.image.fromstring(t.tostring(), frame_dims, 'RGB')
            screen.blit(frame_image, (0, 0))
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        return
            time.sleep(1/30)

def draw_text(screen, text, x, y, size=50, color=(255, 255, 255)):
    font = pygame.font.Font(None, size)  # Use the default font
    text_surface = font.render(text, True, color)  # Create a surface with the text
    screen.blit(text_surface, (x, y))  # Draw the text surface on the screen

def tutorial_text():
    if player.position[0] < 300:
        draw_text(screen, "Arrow Keys to move", 50, 300)
    elif player.position[0] < 500:
        draw_text(screen, "Press UP arrow to jump", 300, 250)
    elif 1090 < player.position[0] < 1350:
        draw_text(screen, "Hold LEFT to maintain momentum", 100, 200) 
    elif 1950 < player.position[0] < 2380:
        draw_text(screen, "Jump in the air to travel further", 100, 100)
    elif player.position[0] > 2800:
        draw_text(screen, "Congrats!! You finished the tutorial", 150, 100)

def draw_death_particles():
    for particle in particles[:]:
        particle.move()
        particle.display(screen)
        if not particle.alive():
            particles.remove(particle)
start_portal_animation = False
def main():
    global angle, speed, start_portal_animation
    play_start_screen()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        handle_input()

        # Update the player
        if not start_portal_animation:
            old_x_position = player.position[0]
            player.update()
            levels[current_level].collide(player)
            update_world_offset(old_x_position)

        screen.fill(levels[0].background_color)
        screen.blit(player.image, player.rect)
        levels[current_level].update()
        draw_death_particles()
        if current_level == 0:
            tutorial_text()
        if levels[current_level].reach_end(player):
            print("finished level")
            start_portal_animation = True 
            # current_level += 1
            # player.position = levels[current_level].player_start.copy()
            # player.velocity = [0, 0]
            # world_offset = [0, 0]
        if start_portal_animation:
            player.portal_animation()
            screen.blit(player.image, player.rect)
        pygame.display.flip()

        pygame.time.Clock().tick(60)
if __name__ == "__main__":
    main()