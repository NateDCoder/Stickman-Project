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
        
        if self.position[0] > levels[current_level].world_size[0] - self.size[0]/2:
            self.position[0] = levels[current_level].world_size[0] - self.size[0]/2
        
        if self.position[1] > levels[current_level].world_size[1] - self.size[1]/2:
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

        if self.position[0] - world_offset[0] < -self.size[0] and current_level == 2:
            self.respawn = True 
            self.death_location = self.position.copy()
            self.death_time = 0
            self.position[1] = 10000000
    def doRespawn(self):
        new_point = interpolate(self.death_time, self.death_location, levels[current_level].player_start.copy())
        world_offset[0] = new_point[0] - WIDTH/2
        self.death_time += 0.01
        particles.append(Particle(new_point, random.randint(1, 5)))
        if self.death_time >= 1:
            world_offset[0] = 0
            self.respawn = False
            self.position = levels[current_level].player_start.copy()
            for platform in levels[current_level].platforms:
                if platform.type == "falling":
                    platform.collideable = True
                    platform.rects = [{"rect": pygame.Rect(platform.position[0] + i, platform.position[1] + j, 5, 5), "falling": False} for i in range(0, platform.size[0], 5) for j in range(0, platform.size[1], 5)]
    def portal_animation(self):
        global start_portal_animation, current_level, world_offset
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
        else:
            current_level += 1
            self.position = levels[current_level].player_start.copy()
            self.scale = 1
            self.angle = 180
            self.radius = 50
            self.respawn = False
            self.jumping = False
            self.velocity = [0, 0]
            self.image = self.frames_l[0]
            self.rect = self.image.get_rect(center=(levels[current_level].player_start[0], levels[current_level].player_start[1]))
            self.size = self.image.get_size()
            world_offset = [0, 0]
            start_portal_animation = False

class Bullet(pygame.sprite.Sprite):
    def __init__(self, position, velocity, size):
        super().__init__()
        self.image = pygame.Surface(size)
        self.image.fill((255, 157, 0))
        self.rect = self.image.get_rect(center=position)
        self.position = [position[0], position[1]]
        self.velocity = velocity
        self.dead = False
    def update(self):
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        self.rect.centerx = self.position[0] - world_offset[0]
        self.rect.centery = self.position[1] - world_offset[1]
        if self.position[0] < 0:
            self.dead = True
        if self.position[1] > levels[current_level].world_size[1]:
            self.dead = True
    def collide(self, player:Player):
        if self.rect.colliderect(player.rect):
            player.respawn = True
            player.death_location = player.position.copy()
            player.death_time = 0
            player.position[1] = 10000000
            player.rect.centery = 10000000
            return True
        return False

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, w, h, color, image=None, type="platform"):
        super().__init__()
        self.image = pygame.Surface((w, h))
        if image:
            self.image = pygame.transform.scale(pygame.image.load(image), (w, h))
        else:
            self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.size = [w, h]
        self.position = [x, y]
        self.type = type
        self.color = color
        self.collideable = True
        if self.type == "falling":
            self.rects = [{"rect": pygame.Rect(x + i, y + j, 5, 5), "falling": False} for i in range(0, w, 5) for j in range(0, h, 5)]
    def collide(self, player:Player):
        if type == "visual" or self.collideable == False:
            return
        if self.rect.colliderect(player.rect):
            if self.type == "spike":
                player.respawn = True
                player.death_location = player.position.copy()
                player.death_time = 0
                player.position[1] = 10000000
            if self.type == "falling" and self.collideable:
                for _ in range(5):
                    self.rects[random.randint(0, len(self.rects) - 1)]["falling"] = True
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
        if self.type == "falling":
            self.rect.topleft = (self.position[0] - world_offset[0], self.position[1] - world_offset[1])
            for r in self.rects:
                if r["falling"]:
                    r["rect"].y += 10
                if r["rect"].y > HEIGHT:
                    self.rects.remove(r)
            if len(self.rects) < 20:
                self.collideable = False
                for rect in self.rects:
                    rect["falling"] = True
            for r in self.rects:
                surface = pygame.Surface((5, 5))
                surface.fill(self.color)
                screen.blit(surface, pygame.Rect(r["rect"].x - world_offset[0], r["rect"].y, r["rect"].w, r["rect"].h))
        else:
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
        self.world_size = [3200, 500]
    def update(self):
        for platform in self.platforms:
            platform.update()
            if not platform.type == "falling":
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
        self.world_size = [3200, 500]
    def update(self):
        super().update()
        self.ball_pit.update_player_ball(player.position[0], player.position[1], player.velocity[0], player.velocity[1])
        self.ball_pit.run(world_offset)
        self.ball_pit_2.update_player_ball(player.position[0], player.position[1], player.velocity[0], player.velocity[1])
        self.ball_pit_2.run(world_offset)

class Level2(LevelData):
    def __init__(self, level, platforms = [], player_start = [], end_point = []):
        super().__init__(level, platforms, player_start, end_point)
        self.platforms.add(Platform(800, 425, 60, 40, (75, 75, 75), "./stickman/stalactite.png", type="spike"))
        self.platforms.add(Platform(500, 425, 60, 40, (75, 75, 75), "./stickman/stalactite.png", type="spike"))
        for x in range(16):
            self.platforms.add(Platform(2325+x*60, 425, 60, 40, (75, 75, 75), "./stickman/stalactite.png", type="spike"))
        # Stagitites above the player    
        self.platforms.add(Platform(430, 0, 20, 30, (100, 100, 100), type="visual"))
        self.platforms.add(Platform(450, 0, 10, 20, (100, 100, 100), type="visual"))

        self.platforms.add(Platform(1000, 0, 10, 20, (100, 100, 100), type="visual"))
        self.platforms.add(Platform(1010, 0, 15, 50, (100, 100, 100), type="visual"))
        self.platforms.add(Platform(1025, 0, 20, 30, (100, 100, 100), type="visual"))

        self.platforms.add(Platform(1770, 0, 20, 25, (100, 100, 100), type="visual"))
        self.platforms.add(Platform(1790, 0, 10, 20, (100, 100, 100), type="visual"))

        self.platforms.add(Platform(2300, 0, 10, 20, (100, 100, 100), type="visual"))
        self.platforms.add(Platform(2310, 0, 20, 100, (100, 100, 100), type="visual"))
        self.platforms.add(Platform(2330, 0, 10, 80, (100, 100, 100), type="visual"))
        self.platforms.add(Platform(2340, 0, 25, 70, (100, 100, 100), type="visual"))

        self.platforms.add(Platform(3020, 0, 10, 70, (100, 100, 100), type="visual"))
        self.platforms.add(Platform(3030, 0, 8, 100, (100, 100, 100), type="visual"))
        self.platforms.add(Platform(3038, 0, 10, 90, (100, 100, 100), type="visual"))
        self.platforms.add(Platform(3048, 0, 10, 50, (100, 100, 100), type="visual"))

        self.platforms.add(Platform(3500, 0, 5, 50, (100, 100, 100), type="visual"))
        self.platforms.add(Platform(3505, 0, 15, 60, (100, 100, 100), type="visual"))
        self.platforms.add(Platform(3520, 0, 10, 70, (100, 100, 100), type="visual"))
        self.platforms.add(Platform(3530, 0, 5, 60, (100, 100, 100), type="visual"))
        self.platforms.add(Platform(3535, 0, 20, 50, (100, 100, 100), type="visual"))
        # Lava rects    
        self.platforms.add(Platform(990, 460, 730, 40, (255, 0, 0), type="spike"))
        self.platforms.add(Platform(1090, 460, 200, 10, (255, 127, 39), type="visual"))
        self.platforms.add(Platform(1040, 468, 100, 15, (255, 127, 39), type="visual"))
        self.platforms.add(Platform(1100, 463, 40, 7, (255, 255, 0), type="visual"))
        self.platforms.add(Platform(1400, 465, 150, 20, (255, 127, 39), type="visual"))
        self.platforms.add(Platform(1500, 480, 120, 15, (255, 127, 39), type="visual"))
        self.platforms.add(Platform(1480, 467, 40, 15, (255, 255, 0), type="visual"))
        self.platforms.add(Platform(1500, 482, 35, 10, (255, 255, 0), type="visual"))
        self.background_color = (127, 127, 127)
        self.world_size = [4000, 500]

class Level3(LevelData):
    def __init__(self, level, platforms = [], player_start = [], end_point = []):
        super().__init__(level, platforms, player_start, end_point)
        self.background_color = (255, 174, 201)
        self.world_size = [3700, 500]
    
class Level4(LevelData):
    def __init__(self, level, platforms = [], player_start = [], end_point = []):
        super().__init__(level, platforms, player_start, end_point)
        self.background_color = (255, 255, 255)
        self.world_size = [3700, 500]
        for x in range(11):
            self.platforms.add(Platform(630+x*60, 425, 60, 40, (75, 75, 75), "./stickman/stalactite.png", type="spike"))
        for x in range(26):
            self.platforms.add(Platform(1440+x*60, 425, 60, 40, (75, 75, 75), "./stickman/stalactite.png", type="spike"))
class Level5(LevelData):
    def __init__(self, level, platforms = [], player_start = [], end_point = []):
        super().__init__(level, platforms, player_start, end_point)
        self.background_color = (3, 11, 207)
        self.world_size = [2500, 500]
        self.bullets = pygame.sprite.Group()
        self.counter = 0
        self.last_spawn_time = time.time()
        self.finished = False
    def update(self):
        global player
        super().update()
        if not player.respawn:
            start_len = len(self.bullets)
            for i in range(len(self.bullets)):
                bullet = self.bullets.sprites()[start_len - i - 1]
                bullet.update()
                if bullet.dead:
                    self.bullets.remove(bullet)
                screen.blit(bullet.image, bullet.rect)    
        if time.time() - self.last_spawn_time >= 1 and self.counter < 20:
            self.counter += 1
            self.bullets.add(Bullet((3000, random.randrange(300, 450)), (-5, 0), (20, 5)))
            for _ in range(10):
                self.bullets.add(Bullet((random.randrange(0, 2500), -300), (0, 5), (5, 20)))
            # spawn a bullet that will go do player
            angle_to_player_1 = math.atan2(player.position[1], player.position[0] - 1000)
            angle_to_player_2 = math.atan2(player.position[1], player.position[0] - 2200)
            self.bullets.add(Bullet((1000, 0), (5*math.cos(angle_to_player_1), 5*math.sin(angle_to_player_1)), (10, 10)))
            self.bullets.add(Bullet((2200, 0), (5*math.cos(angle_to_player_2), 5*math.sin(angle_to_player_2)), (10, 10)))
            self.last_spawn_time = time.time()
        if self.counter == 20:
            self.finished = True
        if self.finished:
            self.platforms.sprites()[-1].collideable = False
            self.platforms.sprites()[-1].image.fill(self.background_color)
    def collide(self, player):
        super().collide(player)
        for bullet in self.bullets:
            if bullet.collide(player):
                self.counter = 0
                self.bullets = pygame.sprite.Group()
                self.last_spawn_time = time.time()
                self.finished = False
        
levels = [
    Level1(
              1,
              [
                (0, 500-40, 3200, 40, (0, 255, 0)), 
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
            ),
    Level2(
              2,
              [
                (0, 500-40, 990, 40, (100, 100, 100)),
                (1720, 500-40, 2280, 40, (100, 100, 100)),
                (400, 500-80, 60, 40, (75, 75, 75)),
                (600, 340, 140, 30, (75, 75, 75)),
                (890, 255, 100, 30, (75, 75, 75)),
                (920, 285, 70, 25, (75, 75, 75)),
                (950, 310, 40, 35, (75, 75, 75)),
                (965, 345, 25, 80, (75, 75, 75)),
                (900, 425, 90, 20, (75, 75, 75)),
                (890, 445, 100, 15, (75, 75, 75)),
                (1200, 220, 50, 20, (75, 75, 75)),
                (1400, 250, 75, 15, (75, 75, 75)),
                (1720, 345, 110, 115, (75, 75, 75)),
                (1730, 280, 75, 65, (75, 75, 75)),
                (1730, 260, 30, 30, (75, 75, 75)),
                (1830, 390, 30, 70, (75, 75, 75)),

                (2300, 390, 25, 70, (75, 75, 75)),
                (2450, 320, 80, 30, (75, 75, 75)),
                (2650, 320, 100, 30, (75, 75, 75)),
                (3000, 250, 80, 20, (75, 75, 75)),
                (3300, 220, 50, 240, (75, 75, 75)),
              ],
              [100, 445],
              [3800, 400]
                
    ),
    Level3(
              3,
              [
                (0, 500-40, 3700, 40, (163, 73, 164)),
                (400, 350, 400, 110, (163, 73, 164)),
                (470, 290, 280, 60, (163, 73, 164)),
                (750, 330, 40, 20, (163, 73, 164)),
                (500, 230, 110, 60, (163, 73, 164)),
                (610, 270, 140, 20, (163, 73, 164)),
                (950, 230, 55, 230, (163, 73, 164)),
                (1005, 350, 50, 110, (163, 73, 164)),
                (1250, 230, 55, 230, (163, 73, 164)),
                (1305, 350, 50, 110, (163, 73, 164)),
                (1550, 230, 55, 230, (163, 73, 164)),
                (1605, 350, 50, 110, (163, 73, 164)),
                (1900, 200, 145, 25, (163, 73, 164)),
                (2150, 260, 145, 200, (163, 73, 164)),
                (2295, 360, 15, 100, (163, 73, 164)),
                (2260, 220, 35, 40, (163, 73, 164)),
                (2200, 25, 45, 70, (163, 73, 164)),
                (2220, 0, 250, 50, (163, 73, 164)),

                (2380, 50, 70, 20, (163, 73, 164)),
                (2380, 70, 70, 20, (163, 73, 164)),
                (2400, 70, 50, 100, (163, 73, 164)),
                (2420, 160, 55, 185, (163, 73, 164)),
                (2535, 445, 25, 15, (163, 73, 164)),

                (2470, 0, 430, 25, (163, 73, 164)),
                (2760, 5, 190, 30, (163, 73, 164)),
                (2810, 30, 45, 30, (163, 73, 164)),
                (2855, 30, 115, 210, (163, 73, 164)),

                (2970, 90, 35, 50, (163, 73, 164)),
                (2970, 140, 65, 100, (163, 73, 164)),
                (2915, 240, 75, 85, (163, 73, 164)),

                (2560, 360, 180, 100, (163, 73, 164)),
                (2730, 345, 50, 115, (163, 73, 164)),
                (2580, 255, 155, 105, (163, 73, 164)),
                (2590, 205, 130, 50, (163, 73, 164)),
                (2600, 155, 100, 80, (163, 73, 164)),
                (2600, 135, 40, 20, (163, 73, 164)),
              ],
              [100, 445],
              [3500, 400]
    ),

    Level4(
              4,
              [
                (0, 500-40, 3700, 40, (153, 217, 234)),
                (500, 350, 125, 150, (0, 162, 232)),
                (780, 220, 110, 25, (127, 127, 127), None, "falling"),
                (1080, 200, 50, 25, (127, 127, 127), None, "falling"),
                (1295, 50, 125, 450, (0, 162, 232)),
                (1200, -50, 300, 50, (255, 255, 255)),
                (1920, 320, 40, 25, (127, 127, 127), None, "falling"),
                (2180, 320, 40, 25, (127, 127, 127), None, "falling"),
                (2420, 290, 40, 25, (127, 127, 127), None, "falling"),
                (2740, 240, 40, 25, (0, 162, 232)),
                (3000, 180, 700, 320, (0, 162, 232)),
              ],
              [100, 445],
              [3500, 120]
    ),
    Level5(
              5,
              [
                (0, 500-40, 1000, 40, (35, 160, 72)),
                (1000, 500-40, 1200, 20, (185, 122, 87)),
                (1005, 500-35, 1190, 10, (128, 64, 0)),
                (2200, 500-40, 300, 40, (157, 157, 157)),
                (2200, 0, 300, 300, (157, 157, 157)),
                (2400, 300, 100, 160, (128, 64, 0)),
              ],
              [100, 445],
              [3500, 120]
    )
    
]
current_level = 4
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
        jumpDebounce =  True
    if not any(keys): 
        player.moving = False

def update_world_offset(old_x_position):
    if current_level == 2:
        world_offset[0] += 5.5
        if world_offset[0] < 0 or player.position[0] < WIDTH/2:
            world_offset[0] = 0
        if world_offset[0] > levels[current_level].world_size[0] - WIDTH or player.position[0] > levels[current_level].world_size[0] - WIDTH/2:
            world_offset[0] = levels[current_level].world_size[0] - WIDTH
    else:
        world_offset[0] += player.position[0] - old_x_position
        world_offset[1] += player.velocity[1]

        if world_offset[0] < 0 or player.position[0] < WIDTH/2:
            world_offset[0] = 0
        if world_offset[1] < 0 or player.position[1] < HEIGHT/2:
            world_offset[1] = 0
        
        if world_offset[0] > levels[current_level].world_size[0] - WIDTH or player.position[0] > levels[current_level].world_size[0] - WIDTH/2:
            world_offset[0] = levels[current_level].world_size[0] - WIDTH

        if world_offset[1] > levels[current_level].world_size[1] - HEIGHT or player.position[1] > levels[current_level].world_size[1] - HEIGHT/2:
            world_offset[1] = levels[current_level].world_size[1] - HEIGHT
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
        draw_text(screen, "Hold LEFT on platforms maintain momentum", 100, 200) 
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
    global start_portal_animation
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

        screen.fill(levels[current_level].background_color)
        screen.blit(player.image, player.rect)
        levels[current_level].update()
        draw_death_particles()
        if current_level == 0:
            tutorial_text()
        if levels[current_level].reach_end(player):
            start_portal_animation = True
        if start_portal_animation:
            player.portal_animation()
            screen.blit(player.image, player.rect)
        pygame.display.flip()

        pygame.time.Clock().tick(60)
if __name__ == "__main__":
    main()