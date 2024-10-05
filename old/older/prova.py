import pygame
from pygame import Vector2
import numpy as np
from random import choice


class Grid:
    def __init__(self, rows=4, cols=4, cell_size=120, cell_gap=5):
        # default parameters
        self.rows, self.cols = rows, cols
        self.cell_size = cell_size
        self.cell_gap = cell_gap

        # cells
        self.cells = np.array( [[Cell( (i,j), self ) for j in range(self.cols)] for i in range(self.rows)], dtype=object )

        # grid parameters
        w = self.cols*(self.cell_size+self.cell_gap-1)+2*self.cell_gap
        h = self.rows*(self.cell_size+self.cell_gap-1)+2*self.cell_gap
        self.background_size = Vector2(w,h)
        self.pos = (SCREEN_SIZE-self.background_size)/2
        self.background_pos = self.pos-Vector2(self.cell_gap, self.cell_gap)

    def get_pos(self, i, j):
        x = self.pos.x + j*(self.cell_size+self.cell_gap)
        y = self.pos.y + i*(self.cell_size+self.cell_gap)
        return Vector2(x, y)

    def add_tile(self):
        empty_cells = [(i,j) for i,row in enumerate(self.cells) for j,cell in enumerate(row) if cell.tile is None]
        i,j = choice(empty_cells)
        value = choice([2,4])
        self.cells[i,j].set_tile(value)
    
    def slide_tiles(self, movement):
        if movement == "left":
            for i,row in enumerate(self.cells):
                for j,cell in enumerate(row):
                    if cell.tile is None:
                        continue
                    last_valid_cell = None
                    for k in range(j-1,-1,-1):
                        move_to_cell = row[k]
                        if not move_to_cell.can_accept(cell.tile):
                            break
                        last_valid_cell = move_to_cell
                    
                    if last_valid_cell is not None:
                        if last_valid_cell.tile is not None:
                            last_valid_cell.merge_tile = cell.tile
                        else:
                            last_valid_cell.tile = cell.tile
                        cell.tile = None

        elif movement == "right":
            pass
        elif movement == "up":
            pass
        elif movement == "down":
            pass

    def draw(self, surf):
        pygame.draw.rect(surf, "gray80", (*self.background_pos, *self.background_size))

        for i in range(self.rows):
            for j in range(self.cols):
                pos = self.get_pos(i, j)
                pygame.draw.rect(surf, "white", (*pos, self.cell_size, self.cell_size))


class Cell:
    def __init__(self, ix, grid):
        self.i, self.j = ix
        self.grid = grid

        self.tile = None
        self.merge_tile = None
    
    def set_tile(self, value):
        pos = self.grid.get_pos(self.i, self.j)
        self.tile = Tile(value, pos=pos, grid=self.grid)
    
    def can_accept(self, tile):
        return tile is None or (self.merge_tile is None and self.tile.value == tile.value)

    def merge_tiles(self):
        if self.tile is None or self.merge_tile is None:
            return
        self.tile.value += self.merge_tile.value
        self.merge_tile.remove()
        self.merge_tile = None


class Tile:
    instances = []

    def __init__(self, value, pos, grid):
        if value is None: 
            return None
        Tile.instances.append(self)

        self.value = value
        self.pos = pos
        self.grid = grid

        self.update_image()

        self.speed = 3
    
    def update_image(self):
        size = self.grid.cell_size
        self.image = pygame.Surface((size,size), pygame.SRCALPHA, 32).convert_alpha()

        pygame.draw.circle(self.image, "red", (size/2,size/2), size/2)
        pygame.draw.circle(self.image, "black", (size/2,size/2), size/2, 2)

        text1 = font1.render(str(self.value), 1, "black")
        self.image.blit(text1, (size/3,size/3))
    
    def update(self):
        pass

    def remove(self):
        Tile.instances.remove(self)
    
    def draw(self, surf):
        surf.blit(self.image, self.pos)


SCREEN_SIZE = SCREEN_WIDTH, SCREEN_HEIGHT = Vector2(1280, 720)

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
clock = pygame.time.Clock()
font1 = pygame.font.Font(None, 50)

grid = Grid()
grid.add_tile()

status = "input"
running = True
while running:
    clock.tick(60)
    mouse_pos = pygame.mouse.get_pos()
    keys = pygame.key.get_pressed()

    screen.fill("gray20")

    # [EVENTS]
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE):
            running = False
    
    movement = None
    if status == "input":
        if keys[pygame.K_LEFT]:
            movement = "left"
        elif keys[pygame.K_RIGHT]:
            movement = "right"
        elif keys[pygame.K_UP]:
            movement = "up"
        elif keys[pygame.K_DOWN]:
            movement = "down"
        
        if movement is not None:
            status = "animation"
            grid.slide_tiles(movement)

    elif status == "animation":
        for tile in Tile.instances:
            tile.update()
    
    grid.draw(screen)
    for tile in Tile.instances:
        tile.draw(screen)

    pygame.display.flip()
    

pygame.quit()