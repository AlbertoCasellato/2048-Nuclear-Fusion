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


class Grid:
    def __init__(self, pos=(0,0), grid_size=4, cell_size=70, cell_gap=5):
        # self.pos = Vector2(pos)
        self.rows, self.cols = grid_size, grid_size
        self.cell_size = cell_size
        self.cell_gap = cell_gap

        self.cells = np.array( [[Cell(i,j, size=self.cell_size) for j in range(self.cols)] for i in range(self.rows) ], dtype=object )

        # dimensions grid
        self.backgrid_size = self.rows*(self.cell_size+self.cell_gap-1)+2*self.cell_gap
        x = (SCREEN_WIDTH-self.backgrid_size)/2
        y = (SCREEN_HEIGHT-self.backgrid_size)/2
        self.pos = Vector2(x,y)
        self.backgrid_pos = self.pos.x-self.cell_gap, self.pos.y-self.cell_gap

    def get_pos(self, i, j):
        x = self.pos.x + j*(self.cell_size+self.cell_gap)
        y = self.pos.y + i*(self.cell_size+self.cell_gap)
        return Vector2(x, y)
    
    def draw(self, surf):
        pygame.draw.rect(surf, "gray80", (*self.backgrid_pos, self.backgrid_size, self.backgrid_size))
        for i in range(self.rows):
            for j in range(self.cols):
                pos = self.get_pos(i,j)
                pygame.draw.rect(surf, "white", (*pos, self.cell_size, self.cell_size))

                # check if tile is present
                if self.cells[i,j].tile == 0:
                    image = self.cells[i,j].image

                    surf.blit(image, pos)



class Cell:
    def __init__(self, i, j, size, tile=0):
        self.i, self.j = i, j
        self.size = size
        self.tile = tile
        self.merge_tile = None

        self.generate_image()
    
    def generate_image(self):
        self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA, 32).convert_alpha()
        pygame.draw.circle(self.image, "red", (self.size/2,self.size/2), self.size/2)
        pygame.draw.circle(self.image, "black", (self.size/2,self.size/2), self.size/2, 2)
        # self.text = 

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()
font1 = pygame.font.Font(None, 35)
font2 = pygame.font.Font(None, 30)
font_m = pygame.font.Font(None, 20)

grid = Grid(pos=(20,20))

running = True
while running:
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()

    screen.fill("gray20")

    # [EVENTS]
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE):
            running = False
    
    grid.draw(screen)

    pygame.display.flip()
    

pygame.quit()