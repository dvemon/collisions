import pygame, sys, math
import pygame.locals as GAME_GLOBALS
import pygame.event as GAME_EVENTS

# initialise global variables
WIDTH = 1280
HEIGHT = 960

GRAVITY = 2

CIRCLE_COLOR = (255,255,255)
HELD_COLOR = (52,137,235)
ATTRACTION_COLOR = (52,137,235)

mouse_pos_prev = [0,0]
mouse_pos = None
mouse_down = False

draw_attractions = False

# define classes
class Circle:
    def __init__(self, position, velocity, mass, radius):
        self.position = list(position)
        self.velocity = velocity
        self.radius = radius
        self.mass = mass
        self.expanding = True

    def draw(self):
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        pygame.draw.circle(screen, CIRCLE_COLOR, (int(self.position[0]), int(self.position[1])), int(self.radius), 0)

    def handle_collision(self, other_circle):
        distance = math.hypot(other_circle.position[0] - self.position[0], other_circle.position[1] - self.position[1])
        if distance < self.radius + other_circle.radius:
            total_mass = self.mass + other_circle.mass

            new_x_velocity = (self.velocity[0] * (self.mass - other_circle.mass) + (2 * other_circle.mass * other_circle.velocity[0])) / total_mass
            new_y_velocity = (self.velocity[1] * (self.mass - other_circle.mass) + (2 * other_circle.mass * other_circle.velocity[1])) / total_mass
            new_x_position = self.position[0] + new_x_velocity
            new_y_position = self.position[1] + new_y_velocity

            other_circle.velocity[0] = (other_circle.velocity[0] * (other_circle.mass - self.mass) + (2 * self.mass * self.velocity[0])) / total_mass
            other_circle.velocity[1] = (other_circle.velocity[1] * (other_circle.mass - self.mass) + (2 * self.mass * self.velocity[1])) / total_mass
            other_circle.position[0] = other_circle.position[0] + other_circle.velocity[0]
            other_circle.position[1] = other_circle.position[1] + other_circle.velocity[1]

            self.position[0] = new_x_position
            self.position[1] = new_y_position
            self.velocity[0] = new_x_velocity
            self.velocity[1] = new_y_velocity
    
class CurrentCircle(Circle):
    def __init__(self, position, velocity, mass, radius):
        super().__init__(position, velocity, mass, radius)

    def draw(self):
        self.position[0] = mouse_pos[0]
        self.position[1] = mouse_pos[1]

        if self.expanding is True and self.radius < 30:
            self.radius += 0.2
            if self.radius >= 30:
                self.expanding = False
                self.radius = 9.9
        elif self.expanding is False and self.radius > 1:
            self.radius -= 0.2
            if self.radius <= 1:
                self.expanding = True
                self.radius = 1.1

        self.mass = self.radius
        pygame.draw.circle(screen, HELD_COLOR, (int(self.position[0]), int(self.position[1])), int(self.radius), 0)

class Collidables():
    def __init__(self):
        self.circles = []

    def add_circle(self, object):
        self.circles.append(object)

    def draw(self):
        for object in self.circles:
            object.position[0] += object.velocity[0]
            object.position[1] += object.velocity[1]
            pygame.draw.circle(screen, (255,255,255), (int(object.position[0]), int(object.position[1])), int(object.radius), 0)

    def handle_collisions(self):
        h = 0
        while h < len(self.circles):
            i = 0
            this_circle = self.circles[h]
            while i < len(self.circles):
                other_circle = self.circles[i]
                if this_circle != other_circle:
                    this_circle.handle_collision(other_circle)
                i += 1
            h += 1

    def calculate_movement(self):
        for this_circle in self.circles:
            for other_circle in self.circles:
                if this_circle is not other_circle:
                    direction = (other_circle.position[0] - this_circle.position[0], other_circle.position[1] - this_circle.position[1])
                    magnitude = math.hypot(other_circle.position[0] - this_circle.position[0], other_circle.position[1] - this_circle.position[1])
                    n_direction = (direction[0] / magnitude, direction[1] / magnitude)

                    if magnitude < 5:
                        magnitude = 5
                    elif magnitude > 15:
                        magnitude = 15

                    strength = ((GRAVITY * this_circle.mass * other_circle.mass) / (magnitude * magnitude)) / other_circle.mass
                    applied_force = (n_direction[0] * strength, n_direction[1] * strength)

                    other_circle.velocity[0] -= applied_force[0]
                    other_circle.velocity[1] -= applied_force[1]

                    if draw_attractions is True:
                        pygame.draw.line(screen, ATTRACTION_COLOR, (this_circle.position[0],this_circle.position[1]), (other_circle.position[0],other_circle.position[1]), 1)

def handle_mouse_down():
    global current_circle
    current_circle = CurrentCircle(position=[0,0], radius=3, mass=3, velocity=[0,0])

def quit_game():
	pygame.quit()
	sys.exit()

if __name__=="__main__":
    # init pygame
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption('Collisions')

    collidables = Collidables()
    current_circle = None

    # main loop
    while True:
        screen.fill((0,0,0))

        mouse_pos = pygame.mouse.get_pos()

        # handle user and system events 
        for event in GAME_EVENTS.get():
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    quit_game()

            if event.type == pygame.KEYUP:
                # reset game
                if event.key == pygame.K_r:
                    collidables.circles = []
                # draw lines
                if event.key == pygame.K_a:
                    draw_attractions = False if draw_attractions else True

            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_down = True
                handle_mouse_down()

            if event.type == pygame.MOUSEBUTTONUP:
                mouse_down = False

            if event.type == GAME_GLOBALS.QUIT:
                quit_game()

        # update the position and velocity of the circles in the collidables list
        collidables.calculate_movement()
        collidables.handle_collisions()
        
        # draw the circles in the collidables list
        collidables.draw()

        # draw the circle which the user is creating by holding down their mouse
        if current_circle:
            current_circle.draw()

            # add the circle to the list
            if mouse_down is False:
                current_circle.velocity[0] = (mouse_pos[0] - mouse_pos_prev[0]) / 4
                current_circle.velocity[1] = (mouse_pos[1] - mouse_pos_prev[1]) / 4
                collidables.add_circle(current_circle)
                current_circle = None

        # store the previous mouse co-ordinates to create a vector when we make a new circle
        mouse_pos_prev = mouse_pos

        pygame.display.update()
        clock.tick(60)