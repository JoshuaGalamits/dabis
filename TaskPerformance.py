import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30

# Colors
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
CYAN = (0, 255, 255)
PURPLE = (160, 32, 240)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
BLUE = (0, 0, 255)

# Shapes in Tetris (rotations of each shape)
SHAPES = [
    [[1, 1, 1, 1]],  # I
    [[1, 1, 1], [0, 1, 0]],  # T
    [[1, 1], [1, 1]],  # O
    [[0, 1, 1], [1, 1, 0]],  # S
    [[1, 1, 0], [0, 1, 1]],  # Z
    [[1, 1, 1], [1, 0, 0]],  # L
    [[1, 1, 1], [0, 0, 1]]   # J
]

COLORS = [CYAN, PURPLE, YELLOW, GREEN, RED, ORANGE, BLUE]

# Screen setup
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Tetris')

# Clock to control frame rate
clock = pygame.time.Clock()

class Piece:
    def __init__(self, shape):
        self.shape = shape
        self.color = random.choice(COLORS)
        self.x = SCREEN_WIDTH // BLOCK_SIZE // 2 - len(shape[0]) // 2
        self.y = 0
        self.rotation = 0

    def rotate(self):
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

    def draw(self, screen):
        for i, row in enumerate(self.shape):
            for j, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(
                        screen,
                        self.color,
                        pygame.Rect(
                            (self.x + j) * BLOCK_SIZE,
                            (self.y + i) * BLOCK_SIZE,
                            BLOCK_SIZE,
                            BLOCK_SIZE
                        )
                    )

def create_grid(locked_positions={}):
    grid = [[BLACK for _ in range(SCREEN_WIDTH // BLOCK_SIZE)] for _ in range(SCREEN_HEIGHT // BLOCK_SIZE)]
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            if (x, y) in locked_positions:
                color = locked_positions[(x, y)]
                grid[y][x] = color
    return grid

def draw_grid(screen, grid):
    for y in range(len(grid)):
        for x in range(len(grid[y])):
            pygame.draw.rect(screen, grid[y][x], pygame.Rect(x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)
    
    for x in range(SCREEN_WIDTH // BLOCK_SIZE):
        pygame.draw.line(screen, GRAY, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, SCREEN_HEIGHT))
    for y in range(SCREEN_HEIGHT // BLOCK_SIZE):
        pygame.draw.line(screen, GRAY, (0, y * BLOCK_SIZE), (SCREEN_WIDTH, y * BLOCK_SIZE))

def valid_space(piece, grid):
    for i, row in enumerate(piece.shape):
        for j, cell in enumerate(row):
            if cell:
                if not (0 <= piece.x + j < SCREEN_WIDTH // BLOCK_SIZE and 0 <= piece.y + i < SCREEN_HEIGHT // BLOCK_SIZE):
                    return False
                if grid[piece.y + i][piece.x + j] != BLACK:
                    return False
    return True

def check_lost(positions):
    for pos in positions:
        x, y = pos
        if y < 1:
            return True
    return False

def clear_rows(grid, locked_positions):
    increment = 0
    for y in range(len(grid) - 1, -1, -1):
        row = grid[y]
        if BLACK not in row:
            increment += 1
            # Delete the filled row
            for x in range(SCREEN_WIDTH // BLOCK_SIZE):
                try:
                    del locked_positions[(x, y)]
                except KeyError:
                    continue

            # Shift every row above down by one
            for k in sorted(list(locked_positions), key=lambda pos: pos[1])[::-1]:
                x, y_pos = k
                if y_pos < y:  # Move down only the rows above the cleared row
                    new_key = (x, y_pos + 1)
                    locked_positions[new_key] = locked_positions.pop(k)
    
    return increment

def draw_text_middle(text, size, color, screen):
    font = pygame.font.SysFont('comicsans', size)
    label = font.render(text, 1, color)
    screen.blit(label, (SCREEN_WIDTH / 2 - (label.get_width() / 2), SCREEN_HEIGHT / 2 - (label.get_height() / 2)))

def main():
    locked_positions = {}
    grid = create_grid(locked_positions)
    
    change_piece = False
    run = True
    current_piece = Piece(random.choice(SHAPES))
    next_piece = Piece(random.choice(SHAPES))
    clock = pygame.time.Clock()
    fall_time = 0
    fall_speed = 0.27

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        # Piece falling mechanism
        if fall_time / 1000 >= fall_speed:
            current_piece.y += 1
            if not (valid_space(current_piece, grid)) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True
            fall_time = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                elif event.key == pygame.K_UP:
                    current_piece.rotate()
                    if not valid_space(current_piece, grid):
                        current_piece.rotate()

        shape_pos = [(current_piece.x + j, current_piece.y + i) for i, row in enumerate(current_piece.shape) for j, cell in enumerate(row) if cell]

        # Lock piece if it hits bottom or other pieces
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            current_piece = next_piece
            next_piece = Piece(random.choice(SHAPES))
            change_piece = False
            if check_lost(locked_positions):
                draw_text_middle("YOU LOST", 40, RED, screen)
                pygame.display.update()
                pygame.time.delay(1500)
                run = False

        draw_grid(screen, grid)
        current_piece.draw(screen)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()
