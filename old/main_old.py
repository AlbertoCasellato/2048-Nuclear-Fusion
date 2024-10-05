import pygame, math
from random import choice, random

# game config
SCREEN_WIDTH, SCREEN_HEIGHT  = 1280, 720
GRID_SIZE = 4 # number of rows and columns
TILE_SIZE = int(SCREEN_HEIGHT // (1.85 + 1.15 * GRID_SIZE))
TILE_PADDING = 0.15 * TILE_SIZE
TILE_BORDER_RADIUS = 4
TABLE_SIZE = TILE_SIZE * GRID_SIZE + (GRID_SIZE - 1) * TILE_PADDING
TABLE_OFFSET_X = (SCREEN_WIDTH - TABLE_SIZE) // 2
TABLE_OFFSET_Y= (SCREEN_HEIGHT - TABLE_SIZE) // 2
TILE_SPEED = TILE_SIZE / (2/30)
TOLERANCE = 20

# game colors
COLORS = {
    "background": "#faf9ed",
    "board": "#b9afa0",
    "empty_tile": "#ccc3b3",
    "text": "#8b8376",
    1: "#eee4da", 2: "#ede0c8", 3: "#f2b179", 4: "#f59563",
    5: "#f67c5f", 6: "#f65e3b", 7: "#edcf72", 8: "#edcc61",
    9: "#edc850", 10: "#edc53f", 11: "#edc22e"
}

# rules
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

# e: electron
# p: positron
# g: photon
# n: neutrino
RULES = {
    "1,1-1,1": "1,2-p-n",
    "1,1-1,2": "2,3-g",
    "2,3-2,3": "2,4-1,1-1,1", # PPI
    "2,3-2,4": "4,7-g",
    "4,7-e": "3,7-n", # PPII
    "3,7-1,1": "2,4-2,4",
    "4,7-1,1": "2,4-2,4", # PPIII (without some steps)

}


class Tile:
    instances = []

    def __init__(self, value, position):
        # self.value = [a, z],  a: atomic number, z: atomic mass number
        self.value = value
        self.row, self.col = position
        self.pos = list(get_pos(self.row, self.col))

        self.new_value = None
        self.target_row, self.target_col = None, None
        self.moving = False
        
        self.merging = False
        self.merging_output = None

        self.create_surf()
        Tile.instances.append(self)
    
    def create_surf(self):
        surf = pygame.Surface((TILE_SIZE,TILE_SIZE), pygame.SRCALPHA)
        rect = surf.get_frect()

        # draw tile
        color = COLORS[self.value[0]]
        pygame.draw.rect(surf, color, rect, border_radius=TILE_BORDER_RADIUS)

        # draw value
        a, z = self.value

        x, y = rect.center
        font_element = pygame.font.Font(None, TILE_SIZE * 3 // 4)
        element_surf = font_element.render(ELEMENTS[a], True, COLORS["text"])
        element_rect = element_surf.get_frect(center=(x,y+5))
        surf.blit(element_surf, element_rect)

        font_z = pygame.font.Font(None, TILE_SIZE * 2 // 6)
        z_surf = font_z.render(str(z), True, COLORS["text"])
        z_rect = z_surf.get_frect(topleft=(TILE_SIZE/10,TILE_SIZE/10))
        surf.blit(z_surf, z_rect)

        self.image = surf

    def move_to(self, row, col):
        if (row, col) != (self.row, self.col):
            self.moving = True
            self.target_row, self.target_col = row, col
    
    def update(self, dt, new_board):
        if not self.moving: 
            return
        
        # find the distance to the target
        target_x, target_y = get_pos(self.target_row, self.target_col)
        dx, dy = (target_x - self.pos[0], target_y - self.pos[1])
        distance = (dx**2 + dy**2)**0.5

        if distance > TOLERANCE:
            # change tile position
            self.pos[0] += TILE_SPEED* dx / distance * dt
            self.pos[1] += TILE_SPEED * dy / distance * dt
        else:
            # stop animation
            self.moving = False
            self.row, self.col = self.target_row, self.target_col
            self.pos = list(get_pos(self.row, self.col))

            if self.merging:
                new_tile_value = self.merging_output["value"]
                new_tile_pos = self.merging_output["position"]
                spawn_tile(new_board, new_tile_value, new_tile_pos)
                
                self.merging_output["passive_tile"].kill()
                self.kill()

    def draw(self, screen):
        screen.blit(self.image, self.pos)
    
    def kill(self):
        Tile.instances.remove(self)


def get_pos(i,j):
    x = TABLE_OFFSET_X + j*(TILE_PADDING+TILE_SIZE)
    y = TABLE_OFFSET_Y + i*(TILE_PADDING+TILE_SIZE)
    return x, y

def encrypt(tile1, tile2):
    a1, z1 = tile1.value
    a2, z2 = tile2.value

    if a1 != a2:
        lower = [a1, z1] if a1 < a2 else [a2, z2]
        higher = [a1, z1] if a1 > a2 else [a2, z2]
        text = f"{lower[0]},{lower[1]}-{higher[0]},{higher[1]}"
    else:
        if z1 != z2:
            lower = [a1, z1] if z1 < z2 else [a2, z2]
            higher = [a1, z1] if z1 > z2 else [a2, z2]
            text = f"{lower[0]},{lower[1]}-{higher[0]},{higher[1]}"
        else:
            text = f"{a1},{z1}-{a2},{z2}"
    
    return text

def decrypt(text):
    new_elements = text.split("-")
    output = None
    for element in new_elements[:1]:
        # TODO: add the little particle output
        # random_empty_tiles()
        output = [int(n) for n in element.split(",")]
    
    return output


def rotate(board, n=1, clockwise=True):
        dim = len(board)

        def cw_rotation(i,j):
            new_i, new_j = i, j
            for _ in range(n):
                new_i, new_j = (new_j, dim - 1 - new_i)
            return new_i, new_j

        def ccw_rotation(i,j):
            new_i, new_j = i, j
            for _ in range(n):
                new_i, new_j = (dim - 1 - new_j, new_i)
            return new_i, new_j

        forward, backward = (cw_rotation, ccw_rotation) if clockwise else (ccw_rotation, cw_rotation)

        new_board = [[None for _ in range(dim)] for __ in range(dim)]
        for i in range(dim):
            for j in range(dim):
                new_i, new_j = forward(i,j)
                new_board[new_i][new_j] = board[i][j]
        
        return new_board, backward

def is_available(board, tile, i, new_j):
    """ Return True if the tile can go to the target tile. """
    # check if the current tile can move
    if tile.merging or (new_j == 0):
        return False

    tile_to_check = board[i][new_j-1]

    # tile_to_check is empty
    if tile_to_check is None:
        return True

    # tile_to_check is a Tile object
    if tile_to_check.merging or not can_merge(tile_to_check, tile):
        return False
    else:
        # merge the two tiles
        tile.merging = True
        tile.merging_output = find_merger_output(tile_to_check, tile)
        return True

def can_merge(tile1, tile2):
    text = encrypt(tile1, tile2)
    return text in RULES

def find_merger_output(passive_tile, active_tile):
    text = encrypt(passive_tile, active_tile)
    new_value = decrypt(RULES[text])

    new_pos = (passive_tile.row, passive_tile.col)
    if passive_tile.target_row is not None:
        new_pos = (passive_tile.target_row, passive_tile.target_col)

    return {"value": new_value, "position": new_pos, "passive_tile": passive_tile}

def move_tiles(board, direction):
    rotations = {"left": 0, "up": 1, "right": 2, "down": 3}
    
    board_rotated, converter = rotate(board, n=rotations[direction], clockwise=False)
    new_board = [[None for _ in range(GRID_SIZE)] for __ in range(GRID_SIZE)]
    will_be_animated = False

    for i,row in enumerate(board_rotated):
        for j,tile in enumerate(row):
            if (tile is None) or (j == 0):
                new_board[i][j] = tile
                continue
            
            # find where to move tiles
            new_j = j
            stop = False
            while not stop:
                if is_available(new_board, tile, i, new_j):
                    new_j -= 1
                else:
                    stop = True
            new_board[i][new_j] = tile
            
            # move tiles
            if j != new_j:
                target_i, target_j = converter(i,new_j)
                tile.move_to(target_i, target_j)
                will_be_animated = True
    
    new_board, _ = rotate(new_board, n=rotations[direction])
    return new_board, will_be_animated

def draw_grid():
    # board
    x = TABLE_OFFSET_X - TILE_PADDING
    y = TABLE_OFFSET_Y - TILE_PADDING
    w = TABLE_SIZE + 2 * TILE_PADDING
    h = TABLE_SIZE + 2 * TILE_PADDING

    grid_surf = pygame.Surface((w,h), pygame.SRCALPHA)
    grid_rect = grid_surf.get_frect(topleft=(x,y))
    pygame.draw.rect(grid_surf, COLORS["board"], (0,0,w,h), border_radius=7)

    # empty tiles
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            tile_x = TILE_PADDING+j*(TILE_PADDING+TILE_SIZE)
            tile_y = TILE_PADDING+i*(TILE_PADDING+TILE_SIZE)
            tile_rect = (tile_x, tile_y, TILE_SIZE, TILE_SIZE)
            pygame.draw.rect(grid_surf, COLORS["empty_tile"], tile_rect, border_radius=TILE_BORDER_RADIUS)

    return grid_surf, grid_rect

def draw_fps(surf, fps):
    font = pygame.font.Font(None, 50)
    text_surf = font.render(f"FPS: {int(fps)}", True, "black")
    surf.blit(text_surf, (10,10))

def new_game():
    Tile.instances = []
    board = [[None for _ in range(GRID_SIZE)] for __ in range(GRID_SIZE)]
    for _ in range(2): 
        spawn_tile(board)
    state = "input"

    return board, state

def random_empty_tiles(game_board):
    empty_tiles = [(i,j) for i,row in enumerate(game_board) for j,tile in enumerate(row) if tile is None]
    return empty_tiles


def spawn_tile(game_board, value=None, pos=None):
    if value is None:
        value = [1,1] if random() < 0.9 else [1,2]
    
    if pos:
        game_board[pos[0]][pos[1]] = Tile(value, pos)
    else:
        empty_tiles = random_empty_tiles(game_board)
        if empty_tiles:
            row, col = choice(empty_tiles)
            game_board[row][col] = Tile(value, (row,col))
        else:
            # TODO: Game over
            pass
    
def text_with_outline(surf, text, font, text_color, outline_color, x, y, outline_thickness, position="center"):
    # Renderizza il testo del contorno
    text_surface = font.render(text, True, outline_color)
    if position == "center":
        text_rect = text_surface.get_frect(center=(x,y))
    elif position == "topleft":
        text_rect = text_surface.get_frect(topleft=(x,y))
    
    # Disegna il contorno (4 direzioni principali più diagonali)
    for dx in [-outline_thickness, 0, outline_thickness]:
        for dy in [-outline_thickness, 0, outline_thickness]:
            if dx != 0 or dy != 0:  # Evita di ridisegnare al centro
                surf.blit(text_surface, text_rect.move(dx,dy))
    
    # Renderizza il testo al centro
    text_surface = font.render(text, True, text_color)
    surf.blit(text_surface, text_rect)

# initialize pygame
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT ))
pygame.display.set_caption("2048 - Nuclear Synthesis")
clock = pygame.time.Clock()

grid_surf, grid_rect = draw_grid()

images = {}
background_img = pygame.image.load("images/background_blurred.jpg").convert_alpha()
ratio = SCREEN_WIDTH/background_img.width
images["background"] = pygame.transform.scale_by(background_img, ratio)
# TODO: scale images based on TILE_SIZE
for name in ["proton", "neutron"]:
    surf = pygame.image.load(f"images/{name}.png").convert_alpha()
    images[name] = pygame.transform.scale_by(surf, TILE_SIZE/800)

# new game instance
game_board, state = new_game()

show_info = False
running = True
while running:
    dt = clock.tick() / 1000

    # events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_h:
                show_info = not show_info
    
    # update game state
    match state:
        case "input":
            keys = pygame.key.get_just_pressed()
            direction = None

            # restart the game
            if keys[pygame.K_r]:
                game_board, state = new_game()

            # move tiles
            if keys[pygame.K_LEFT]:
                direction = "left"
            elif keys[pygame.K_UP]:
                direction = "up"
            elif keys[pygame.K_RIGHT]:
                direction = "right"
            elif keys[pygame.K_DOWN]:
                direction = "down"
            
            if direction:
                state = "animation"
                new_game_board, will_be_animated = move_tiles(game_board, direction)

        case "animation":
            # update position and check if animation ends
            stop_animation = True
            for row in game_board:
                for tile in row:
                    if tile is None:
                        continue

                    tile.update(dt, new_game_board)
                    if tile.moving:
                        stop_animation = False
                    
            if stop_animation:
                state = "input"
                game_board = new_game_board.copy()
                if will_be_animated:
                    spawn_tile(game_board)
    
    # draw on screen
    screen.fill(COLORS["background"])
    # screen.blit(images["background"], (0,0))
    screen.blit(grid_surf, grid_rect)
    # draw_grid(screen)
    for tile in Tile.instances:
        tile.draw(screen)
    if show_info:
        draw_fps(screen, clock.get_fps())
    
    pygame.display.flip()

pygame.quit()
