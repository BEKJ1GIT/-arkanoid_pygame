import pygame
from pathlib import Path

# --- Paths -------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
LEVELS_DIR = BASE_DIR / "levels"

# --- Screen Setup ------------------------------------------------------------
WIDTH = 800
HEIGHT = 600
FPS = 60

# --- Colors ------------------------------------------------------------------
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
ORANGE = (255, 165, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (60, 60, 60)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
PINK = (255, 105, 180)

BG_COLOR = pygame.Color('grey12')

# Brick Color and HP
BRICK_COLORS = [
    GRAY,     # HP 0 (Indestructible)
    RED,      # HP 1
    ORANGE,   # HP 2
    YELLOW,   # HP 3
    GREEN     # HP 4
]

PADDLE_COLOR = CYAN
BALL_COLOR = WHITE
TEXT_COLOR = WHITE

# --- Playing Field -------------------------------------------------------------
BRICK_WIDTH = 80
BRICK_HEIGHT = 20
TOP_OFFSET = 40
FIELD_LEFT = 0
BRICK_PADDING_X = 0
BRICK_PADDING_Y = 5
BRICK_COLS = (WIDTH - 2 * FIELD_LEFT) // (BRICK_WIDTH + BRICK_PADDING_X)
FIELD_RIGHT = FIELD_LEFT + BRICK_COLS * (BRICK_WIDTH + BRICK_PADDING_X)

WALL_START_Y = TOP_OFFSET

# --- Paddle, Ball -----------------------------------------------------------
PADDLE_WIDTH = 100
PADDLE_HEIGHT = 12
PADDLE_SPEED = 7

BALL_RADIUS = 8
BALL_SPEED = 5
MAX_BALL_SPEED_X = 8

# --- Laser --------------------------------------------------------------------
LASER_WIDTH = 4
LASER_HEIGHT = 15
LASER_SPEED = 10
LASER_COLOR = RED

# --- Visual Effects -----------------------------------------------------------
PARTICLE_COUNT = 10
PARTICLE_LIFETIME = (12, 24)
PARTICLE_SPEED = (1.5, 4.0)
PARTICLE_GRAVITY = 0.15
