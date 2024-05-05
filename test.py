import pygame
import pymunk
import random

class BallSimulation:
    def __init__(self, x, y, width=800, height=600, ball_radius=10, start_height=400):
        self.width = width
        self.height = height
        self.ball_radius = ball_radius
        self.start_height = start_height
        self.x = x
        self.y = y
        self.balls = []
        self.space = None
        self.screen = None

    def add_ball(self, x, y):
        mass = 1
        moment = pymunk.moment_for_circle(mass, 0, self.ball_radius)
        body = pymunk.Body(mass, moment)
        body.position = x, y
        shape = pymunk.Circle(body, self.ball_radius)
        shape.elasticity = 0.95
        self.space.add(body, shape)
        self.balls.append(shape)

    def add_walls(self):
        static_lines = [
            pymunk.Segment(self.space.static_body, (self.x, self.y), (self.x, self.height), 1),
            pymunk.Segment(self.space.static_body, (self.x, self.height), (self.width, self.height), 1),
            pymunk.Segment(self.space.static_body, (self.width, self.height), (self.width, 0), 1),
            pymunk.Segment(self.space.static_body, (self.width, self.y), (self.x, self.y), 1)
        ]
        for line in static_lines:
            line.elasticity = 1.0
            self.space.add(line)

    def draw_ball(self, ball):
        pos_x, pos_y = int(ball.body.position.x), int(ball.body.position.y)
        pygame.draw.circle(self.screen, (255, 255, 255), (pos_x, pos_y), self.ball_radius)

    def run(self):
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        clock = pygame.time.Clock()

        self.space = pymunk.Space()
        self.space.gravity = (0, 100)

        self.add_walls()
        for x in range(self.ball_radius, self.width, self.ball_radius * 2):
            for y in range(self.start_height, self.height, self.ball_radius * 2):
                self.add_ball(x, y)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            self.screen.fill((0, 0, 0))

            for ball in self.balls:
                self.draw_ball(ball)

            self.space.step(1/60.0)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()

if __name__ == "__main__":
    sim = BallSimulation(0, 0)
    sim.run()