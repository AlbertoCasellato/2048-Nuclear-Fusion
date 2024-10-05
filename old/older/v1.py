import pygame
from pygame import Vector2

SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = Vector2(1280, 720)
ROWS, COLS = 3, 3

class Atom:
    instances = []

    def __init__(self, atomic_number, pos=(0,0), atomic_mass="stable"):
        Atom.instances.append(self)

        self.z = atomic_number
        self.m = 2*atomic_number if atomic_mass is "stable" else atomic_mass
        self.pos = Vector2(pos)
        self.speed = 3

        self.size = 60
        self.text1 = font1.render(str(self.z), 1, "black")
        self.text2 = font2.render(str(self.m), 1, "black")

        # image
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA, 32).convert_alpha()
        pygame.draw.circle(self.image, "red", (self.size/2,self.size/2), self.size/2)
        pygame.draw.circle(self.image, "black", (self.size/2,self.size/2), self.size/2, 2)
        self.image.blit(self.text1, (self.size/3,self.size/3))
        self.image.blit(self.text2, (self.size/5,self.size/5))

        self.destination = None
    
    def move(self, new_pos):
        self.destination = Vector2(new_pos)
    
    def collision(self, other):
        # apply rules
        ...

        # TODO: remove
        new_z, new_m = self.z + other.z, self.m + other.m
        Atom(new_z, pos=other.pos, atomic_mass=new_m)
        Atom.instances.remove(self)
        Atom.instances.remove(other)
    
    def update(self):
        if self.destination is not None:
            movement = self.speed*(self.destination - self.pos).normalize()
            self.pos += movement
            if (self.destination - self.pos).magnitude() < self.speed:
                self.pos = self.destination
                self.destination = None

                # collision
                for atom in Atom.instances:
                    if atom is self: continue
                    distance = (atom.pos-self.pos).magnitude()
                    if distance < self.size:
                        self.collision(atom)
                        break
    
    def draw(self, surf):
        surf.blit(self.image, (self.pos.x-self.size/2, self.pos.y-self.size/2))


pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()
font1 = pygame.font.Font(None, 40)
font2 = pygame.font.Font(None, 20)
running = True

grid = [0 for _ in range(ROWS*COLS)]
a = Atom(1, pos=SCREEN_SIZE/2)
b = Atom(2, pos=SCREEN_SIZE/2- Vector2(100,0))


while running:
    dt = clock.tick(60)/1000
    t = pygame.time.get_ticks()
    mouse_pos = pygame.mouse.get_pos()

    screen.fill("gray20")

    # [EVENTS]
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE):
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            a.move(mouse_pos)

    # [UPDATE]
    keys = pygame.key.get_pressed()
    print(Atom.instances)
    

    # [DRAW]
    for atom in Atom.instances:
        atom.update()
        atom.draw(screen)

    pygame.display.flip()
    

pygame.quit()