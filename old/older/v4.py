import pygame
from pygame import Vector2
import numpy as np
from random import choice

SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = Vector2(1280, 720)
ELEMENTS = {
    1: "H",
    2: "He",
    3: "Li",
    4: "Be",
    5: "B",
    6: "C",
    7: "N",
    8: "O"
}

class Atom:
    instances = []

    def __init__(self, atomic_number, pos=(0,0), atomic_mass="stable", visible=True):
        Atom.instances.append(self)

        self.z = atomic_number
        self.m = 2*atomic_number if atomic_mass is "stable" else atomic_mass
        self.pos = Vector2(pos)
        self.visible = visible

        self.speed = 3
        self.size = 60

        element_name = ELEMENTS[self.z]
        font_main_text = font1 if len(element_name)==1 else font2
        self.text1 = font_main_text.render(element_name, 1, "black")
        self.text2 = font_m.render(str(self.m), 1, "black")

        # image
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA, 32).convert_alpha()
        pygame.draw.circle(self.image, "red", (self.size/2,self.size/2), self.size/2)
        pygame.draw.circle(self.image, "black", (self.size/2,self.size/2), self.size/2, 2)
        self.image.blit(self.text1, (self.size/3,self.size/3))
        self.image.blit(self.text2, (self.size/5,self.size/5))

        self.destination = None
    
    def move(self, new_pos):
        self.destination = Vector2(new_pos)
    
    def update(self):
        if self.destination is not None:
            # update pos
            movement = self.speed*(self.destination - self.pos).normalize()
            self.pos += movement

            # end of movement
            if (self.destination - self.pos).magnitude() < self.speed:
                self.pos = self.destination
                self.destination = None
    
    def draw(self, surf):
        if self.visible:
            surf.blit(self.image, (self.pos.x-self.size/2, self.pos.y-self.size/2))

class Grid:
    def __init__(self, pos, rows=4, cols=4, cell_size=70) -> None:
        self.pos = Vector2(pos)
        self.rows, self.cols = rows, cols
        self.cell_size = cell_size

        self.items = [0 for _ in range(rows*cols)]

        self.array = np.zeros((self.rows, self.cols), dtype=object)
        self.array[1,0] = Atom(1, pos=self.get_pos((1,0)))
        self.array[1,2] = Atom(1, pos=self.get_pos((1,2)))
        self.array[1,3] = Atom(1, pos=self.get_pos((1,3)))
    
    def get_pos(self, ix):
        i, j = ix
        return self.pos.x + j*self.cell_size + self.cell_size/2, self.pos.y + i*self.cell_size + self.cell_size/2
    
    def add_atom(self):
        empty_cells = [(i,j) for i,row in enumerate(self.array) for j,el in enumerate(row) if el is 0]
        i,j = choice(empty_cells)
        self.array[i,j] = Atom(3, pos=self.get_pos( (i,j) ))
    
    def check_collision(self, a, b):
        if a is 0 or b is 0:
            return a, b
        # PLACEHOLDER RULES
        new_z, new_m = a.z + b.z, a.m + b.m
        # PLACEHOLDER COLLISION
        return Atom(new_z, a.pos, new_m, visible=False), 0

    def slide_left(self):
        list_rows = []
        for i,row in enumerate(self.array):
            # remove zeros
            new_row = [el for el in row if el is not 0]

            # collision
            for j in range(len(new_row)):
                b = new_row[j]
                if j==0:
                    continue

                a = new_row[j-1]
                new_a, new_b = self.check_collision(a, b)
                new_row[j-1:j+1] = [new_a, new_b]
            
            # remove zeros
            new_row = [el for el in new_row if el is not 0]
            # add zeros
            new_row += [0 for _ in range(self.rows-len(row))]

            list_rows.append(new_row)
        
        new_array = np.array(list_rows)
        self.array = np.array(new_array, dtype=object)
        
        # TODO: add new atom

    
    def draw(self, surf):
        for i in range(self.rows):
            for j in range(self.cols):
                x, y = self.pos.x + j*(self.cell_size), self.pos.y + i*self.cell_size
                pygame.draw.rect(surf, "white", (x,y,self.cell_size,self.cell_size), 1)

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()
font1 = pygame.font.Font(None, 35)
font2 = pygame.font.Font(None, 30)
font_m = pygame.font.Font(None, 20)

a = Atom(1, pos=SCREEN_SIZE/2-Vector2(0,100))
b = Atom(2, pos=SCREEN_SIZE/2- Vector2(100,100))
grid = Grid(SCREEN_SIZE/2)
grid.add_atom()

running = True
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
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                grid.slide_left()

    # [UPDATE]
    keys = pygame.key.get_pressed()
    
    # [DRAW]
    grid.draw(screen)
    for atom in Atom.instances:
        atom.update()
        atom.draw(screen)

    pygame.display.flip()
    

pygame.quit()