import pygame
import pymunk
import random
class BallSimulation:
    def __init__(self, x, y, width=800, height=600, ball_radius=5, start_height=400, screen=None):
        self.width = width
        self.height = height
        self.ball_radius = ball_radius
        self.start_height = start_height
        self.x = x
        self.y = y
        self.balls = []
        self.space = None
        self.screen = screen
        self.colors_list = [(255, 0, 0), (255, 255, 0), (255, 127, 0), (0, 255, 0), (200, 0, 200)]
        self.colors = []

    def add_ball(self, x, y):
        mass = 1
        moment = pymunk.moment_for_circle(mass, 0, self.ball_radius)
        body = pymunk.Body(mass, moment)
        body.position = x, y
        shape = pymunk.Circle(body, self.ball_radius)
        shape.elasticity = 0.97
        self.space.add(body, shape)
        self.balls.append(shape)

    def add_walls(self):
        static_lines = [
            pymunk.Segment(self.space.static_body, (self.x, self.y), (self.x, self.y+self.height), 1),
            pymunk.Segment(self.space.static_body, (self.x, self.y+self.height), (self.x+self.width, self.y+self.height), 1),
            pymunk.Segment(self.space.static_body, (self.x+self.width, self.y+self.height), (self.x+self.width, self.y), 1),
            pymunk.Segment(self.space.static_body, (self.x+self.width, self.y), (self.x, self.y), 1)
        ]
        for line in static_lines:
            line.elasticity = 1.0
            self.space.add(line)

    def draw_ball(self, ball, color, world_offset):
        pos_x, pos_y = int(ball.body.position.x), int(ball.body.position.y)
        pygame.draw.circle(self.screen, color, (pos_x - world_offset[0], pos_y - world_offset[1]), self.ball_radius)

    def initialize(self):
        self.space = pymunk.Space()
        self.space.gravity = (0, 100)

        self.add_walls()
        for x in range(self.ball_radius, self.width, self.ball_radius * 2):
            for y in range(self.start_height, self.height, self.ball_radius * 2):
                self.add_ball(x + self.x, y+self.y)
                self.colors.append(random.choice(self.colors_list))
        mass = 10
        moment = pymunk.moment_for_circle(mass, 0, 20)
        body = pymunk.Body(mass, moment)
        body.position = x, y
        new_ball = pymunk.Circle(body, 20)
        new_ball.elasticity = 0.99
        self.space.add(body, new_ball)
        self.balls.append(new_ball)

    def update_player_ball(self, x, y, vel_x, vel_y):
        self.balls[-1].body.position = x, y
        self.balls[-1].body.velocity = vel_x*10, 100
    def run(self, world_offset):
        for i in range(len(self.balls)-1):
            self.draw_ball(self.balls[i], self.colors[i], world_offset)

        self.space.step(1/60.0)

            