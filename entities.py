import pygame
import random
import math
import settings as cfg

# Initialize the font module for the power-up letters
pygame.font.init()
POWERUP_FONT = pygame.font.Font(None, 20)

class Paddle:
    # (This class is unchanged from the previous version)
    def __init__(self):
        self.screen_width = cfg.WIDTH
        self.screen_height = cfg.HEIGHT
        self.original_width = cfg.PADDLE_WIDTH
        self.height = cfg.PADDLE_HEIGHT
        self.speed = cfg.PADDLE_SPEED
        self.color = cfg.PADDLE_COLOR
        
        self.width = self.original_width
        self.power_up_timers = {
            'shrink': 0,
            'grow': 0
        }


        self.rect = pygame.Rect(
            self.screen_width // 2 - self.width // 2,
            self.screen_height - 30,
            self.width,
            self.height
        )

    def reset(self):
        self.rect.x = self.screen_width // 2 - self.original_width // 2
        self.width = self.original_width
        self.rect.width = self.width

        for power_up in self.power_up_timers:
            self.power_up_timers[power_up] = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT]:
            self.rect.x += self.speed

        if self.rect.left < cfg.FIELD_LEFT:
            self.rect.left = cfg.FIELD_LEFT
        if self.rect.right > cfg.FIELD_RIGHT:
            self.rect.right = cfg.FIELD_RIGHT
            
        self._update_power_ups()

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect, border_radius=5)
        
    def activate_power_up(self, type):
        duration = 600
        if type == 'shrink':
            if self.power_up_timers['shrink'] <= 0:
                current_center = self.rect.centerx
                self.width = 60
                self.rect.width = self.width
                self.rect.centerx = current_center
            self.power_up_timers['shrink'] = duration
        elif type == 'grow':
            if self.power_up_timers['grow'] <= 0:
                current_center = self.rect.centerx
                self.width = 150
                self.rect.width = self.width
                self.rect.centerx = current_center
            self.power_up_timers['grow'] = duration
            
    def _update_power_ups(self):
        if self.power_up_timers['shrink'] > 0:
            self.power_up_timers['shrink'] -= 1
            if self.power_up_timers['shrink'] <= 0:
                current_center = self.rect.centerx
                self.width = self.original_width
                self.rect.width = self.width
                self.rect.centerx = current_center
        if self.power_up_timers['grow'] > 0:
            self.power_up_timers['grow'] -= 1
            if self.power_up_timers['grow'] <= 0:
                current_center = self.rect.centerx
                self.width = self.original_width
                self.rect.width = self.width
                self.rect.centerx = current_center


class Ball:
    # (This class is unchanged from the previous version)
    def __init__(self):
        self.screen_width = cfg.WIDTH
        self.screen_height = cfg.HEIGHT
        self.radius = cfg.BALL_RADIUS
        self.color = cfg.BALL_COLOR
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        
        self.is_fast = False
        self.fast_timer = 0
        self.is_slowed = False
        self.slow_timer = 0
        self.base_speed = cfg.BALL_SPEED
        
        self.reset()

    def reset(self):
        self.rect.center = (self.screen_width // 2, self.screen_height // 2)
        self.speed_x = self.base_speed * random.choice((1, -1))
        self.speed_y = -self.base_speed
        self.is_fast = False
        self.fast_timer = 0
        self.is_slowed = False
        self.slow_timer = 0

    def update(self):
        wall_collision = False

        if self.is_fast:
            self.fast_timer -= 1
            if self.fast_timer <= 0:
                self.speed_x = self.speed_x / 2
                self.speed_y = self.speed_y / 2
                self.is_fast = False

        if self.is_slowed:
            self.slow_timer -= 1
            if self.slow_timer <= 0:
                self.speed_x = self.speed_x * 2
                self.speed_y = self.speed_y * 2
                self.is_slowed = False

        self.rect.x += self.speed_x
        self.rect.y += self.speed_y

        if self.rect.top <= 0:
            self.speed_y *= -1
            wall_collision = True
        if self.rect.left <= 0 or self.rect.right >= self.screen_width:
            self.speed_x *= -1
            wall_collision = True

        if self.rect.top > self.screen_height:
            return 'lost', False
        
        return 'playing', wall_collision

    def bounce_off(self, rect: pygame.Rect):
        # Calculate ball's overlaps and find the smallest one
        overlap_left = self.rect.right - rect.left
        overlap_right = rect.right - self.rect.left
        overlap_top = self.rect.bottom - rect.top
        overlap_bottom = rect.bottom - self.rect.top

        min_overlap = min(overlap_bottom, overlap_left, overlap_right, overlap_top)
        
        # Calculate the Ball's final velocities
        if min_overlap == overlap_top and self.speed_y > 0:
            self.rect.bottom = rect.top
            self.speed_y *= -1
        elif min_overlap == overlap_bottom and self.speed_y < 0:
            self.rect.top = rect.bottom
            self.speed_y *= -1
        elif min_overlap == overlap_left and self.speed_x > 0:
            self.rect.right = rect.left
            self.speed_x *= -1
        elif min_overlap == overlap_right and self.speed_x < 0:
            self.rect.left = rect.right
            self.speed_x *= -1

    def draw(self, screen):
        pygame.draw.ellipse(screen, self.color, self.rect)
        
    def activate_power_up(self, type):
        if type == 'slow' and not self.is_slowed:
            if self.is_fast:
                self.speed_x /= 2
                self.speed_y /= 2
                self.is_fast = False
            self.speed_x /= 2
            self.speed_y /= 2
            self.is_slowed = True
            self.slow_timer = 600
        elif type == 'speed_up' and not self.is_fast:
            if self.is_slowed:
                self.speed_x *= 2
                self.speed_y *= 2
                self.is_slowed = False
            self.speed_x *= 2
            self.speed_y *= 2
            self.is_fast = True
            self.fast_timer = 600


class Brick:
    def __init__(self, x, y, hp, moving=False):
        self.rect = pygame.Rect(x, y, cfg.BRICK_WIDTH, cfg.BRICK_HEIGHT)
        self.hp = hp
        self.color = cfg.BRICK_COLORS[min(self.hp, len(cfg.BRICK_COLORS) - 1)]
        self.moving = moving
        self.indestructible = (self.hp == 0)
        self.direction = 1
        self.speed = 1.5 if moving else 0
        self.boundary = 50
        self.start_x = x

    def update(self):
        if self.moving:
            self.rect.x += self.direction * self.speed
            if abs(self.rect.centerx - self.start_x) > self.boundary:
                self.direction *= -1


    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        pygame.draw.rect(screen, cfg.DARK_GRAY, self.rect, 2)

    def hit(self):
        if self.hp > 0:
            self.hp -= 1
            if self.hp > 0:
                self.color = cfg.BRICK_COLORS[min(self.hp, len(cfg.BRICK_COLORS) - 1)]
                return False
            return True
        return False



class PowerUp:
    # (This class is unchanged from the previous version)
    PROPERTIES = {
        'shrink': {'color': cfg.RED, 'char': 'S', 'message': 'PADDLE SHRINK'},
        'grow': {'color': cfg.BLUE if hasattr(cfg, 'BLUE') else (60, 60, 255), 'char': 'G', 'message': 'PADDLE GROW'},
        'speed_up': {'color': cfg.CYAN, 'char': 'F', 'message': 'FAST BALL'},
        'slow': {'color': cfg.ORANGE, 'char': 'D', 'message': 'SLOW BALL'},
        'extra_life': {'color': cfg.PINK, 'char': '1', 'message': 'EXTRA LIFE'},
    }
    
    def __init__(self, x, y, type):
        self.width = 30
        self.height = 15
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.speed_y = 3
        self.type = type
        self.color = self.PROPERTIES[type]['color']
        self.char = self.PROPERTIES[type]['char']

    def update(self):
        self.rect.y += self.speed_y

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)
        text_surf = POWERUP_FONT.render(self.char, True, (255, 255, 255))
        text_rect = text_surf.get_rect(center=self.rect.center)
        screen.blit(text_surf, text_rect)


# ! PHASE: VISUAL EFFECTS !
class Particle:
    def __init__(self, x, y, color, min_size, max_size, min_speed, max_speed, gravity):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(min_size, max_size)
        self.gravity = gravity
        angle = random.uniform(0, 360)
        speed = random.uniform(min_speed, max_speed)
        self.vx = speed * math.cos(math.radians(angle))
        self.vy = speed * math.sin(math.radians(angle))

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.vy += self.gravity
        self.size -= 0.1 

    def draw(self, screen):
        if self.size > 0:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(self.size))

class Firework:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.x = random.randint(0, screen_width)
        self.y = screen_height
        self.vy = -random.uniform(8, 12) 
        self.color = (255, 255, 255) 
        self.exploded = False
        self.particles = []
        self.explosion_y = random.uniform(screen_height * 0.2, screen_height * 0.5)

    def update(self):
        if not self.exploded:
            self.y += self.vy
            if self.y <= self.explosion_y:
                self.exploded = True
                explosion_color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))
                for _ in range(cfg.PARTICLE_COUNT * 5): 
                    self.particles.append(Particle(self.x, self.y, explosion_color, 2, 4, cfg.PARTICLE_SPEED[0], cfg.PARTICLE_SPEED[1], cfg.PARTICLE_GRAVITY))
        else:
            for particle in self.particles[:]:
                particle.update()
                if particle.size <= 0:
                    self.particles.remove(particle)

    def draw(self, screen):
        if not self.exploded:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 3)
        else:
            for particle in self.particles:
                particle.draw(screen)

    def is_dead(self):
        return self.exploded and not self.particles
    