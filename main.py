import pygame
import sys
import random
import math
from entities import Paddle, Ball, Brick, PowerUp, Particle, Firework
import settings as cfg

# -- General Setup --
pygame.init()
pygame.mixer.init()
clock = pygame.time.Clock()
sound_enabled = True

# -- Screen Setup --
screen_width = cfg.WIDTH
screen_height = cfg.HEIGHT
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("PyGame Arkanoid")
sound_button_rect = pygame.Rect(screen_width - 180, screen_height - 80, 160, 40)

# -- Colors --
BG_COLOR = cfg.BG_COLOR

# --- Game Variables ---
# ! PHASE: TITLE SCREEN !
# The game now starts on the title screen
game_state = 'title_screen' 
# ! END PHASE: TITLE SCREEN !
score = 0
lives = 3
current_level = 1
max_level = 3
display_message = ""
message_timer = 0
firework_timer = 0

# -- Font Setup --
# ! PHASE: TITLE SCREEN !
title_font = pygame.font.Font(None, 70)
# ! END PHASE: TITLE SCREEN !
game_font = pygame.font.Font(None, 40)
message_font = pygame.font.Font(None, 30)

# -- Sound Setup --
try:
    bounce_sound = pygame.mixer.Sound('bounce.wav')
    brick_break_sound = pygame.mixer.Sound('brick_break.wav')
    game_over_sound = pygame.mixer.Sound('game_over.wav')
except pygame.error as e:
    print(f"Warning: Sound file not found. {e}")
    class DummySound:
        def play(self): pass
    bounce_sound, brick_break_sound, game_over_sound = DummySound(), DummySound(), DummySound()

def toggle_sound():
    global sound_enabled
    sound_enabled = not sound_enabled

# -- Game Objects --
paddle = Paddle()
ball = Ball()

# --- Brick Wall Setup Function ---
def create_brick_wall(level=1):
    bricks = []

    if level == 1:
        brick_rows = 4
        pattern = lambda r, c: True
        moving_rows = []
        indestructible_positions = set()
    elif level == 2:
        brick_rows = 5
        pattern = lambda r, c: (r + c) % 2 == 0
        moving_rows = [2]
        indestructible_positions = {(2, 3), (2, 4), (2, 5), (2, 6)}
    elif level == 3:
        brick_rows = 6
        pattern = lambda r, c: True
        moving_rows = []
        indestructible_positions = {(5, 3), (5, 4), (5, 5)}
        indestructible_positions |= {(1, 4), (1, 5)}
    else:
        brick_rows = 4 + (level % 3)
        pattern = lambda r, c: True
        moving_rows = []
        indestructible_positions = set()

    for row in range(brick_rows):
        for col in range(cfg.BRICK_COLS):
            if pattern(row, col):
                x = col * (cfg.BRICK_WIDTH + cfg.BRICK_PADDING) + cfg.FIELD_LEFT
                y = row * (cfg.BRICK_HEIGHT + cfg.BRICK_PADDING) + cfg.WALL_START_Y
                
                moving = row in moving_rows
                
                if (row, col) in indestructible_positions:
                    hp = 0
                else:
                    hp = max(1, min(4, 4 - row)) # Top rows have more HP
                
                bricks.append(Brick(x, y, hp, moving))

    return bricks





bricks = create_brick_wall(current_level)
power_ups = []
particles = []
fireworks = []


# -- Main Game Loop --
while True:
    # --- Event Handling ---
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == 'title_screen' and sound_button_rect.collidepoint(event.pos):
                toggle_sound()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.unicode.lower() in ['v', 'м']:
                toggle_sound()
            # ! PHASE: TITLE SCREEN !
            if event.key == pygame.K_SPACE:
                # If on title screen, start the game
                if game_state == 'title_screen':
                    game_state = 'playing'
                # If game is over, go back to title screen
                elif game_state in ['game_over', 'you_win']:
                    if game_state == 'you_win':
                        current_level += 1
                        if current_level > max_level:
                            current_level = 1

                    paddle.reset()
                    ball.reset()
                    bricks = create_brick_wall()
                    score = 0
                    lives = 3
                    power_ups.clear()
                    particles.clear()
                    fireworks.clear()
                    game_state = 'title_screen'
            # ! END PHASE: TITLE SCREEN !

    # --- Drawing and Updating based on Game State ---
    screen.fill(BG_COLOR)

    # ! PHASE: TITLE SCREEN !
    if game_state == 'title_screen':
        # Draw the title
        title_surface = title_font.render("ARKANOID", True, (255, 255, 255))
        title_rect = title_surface.get_rect(center=(screen_width / 2, screen_height / 2 - 50))
        screen.blit(title_surface, title_rect)
        
        # Draw the start message
        start_surface = game_font.render("Press SPACE to Start", True, (255, 255, 255))
        start_rect = start_surface.get_rect(center=(screen_width / 2, screen_height / 2 + 20))
        screen.blit(start_surface, start_rect)

        # Draw the button for setting sound game
        pygame.draw.rect(screen, (30, 30, 30), sound_button_rect, border_radius=5)
        border_color = (0, 200, 0) if sound_enabled else (200, 0, 0)
        pygame.draw.rect(screen, border_color, sound_button_rect, 2, border_radius=5)
        
        sound_status_text = "Sound: ON" if sound_enabled else "Sound: OFF"
        sound_surface = message_font.render(sound_status_text, True, (255, 255, 255))
        sound_rect = sound_surface.get_rect(center=sound_button_rect.center)
        screen.blit(sound_surface, sound_rect)

    elif game_state == 'playing':
        # --- Update all game objects ---
        paddle.update()
        keys = pygame.key.get_pressed()
        ball_status, wall_collision = ball.update()
        if ball_status == 'lost':
            lives -= 1
            if lives <= 0:
                game_state = 'game_over'
                if sound_enabled:
                    game_over_sound.play()

            else:
                ball.reset()
                paddle.reset()
        else:
            if wall_collision:
                if sound_enabled:
                    bounce_sound.play()
                for _ in range(cfg.PARTICLE_COUNT // 2):
                    particles.append(Particle(ball.rect.centerx, ball.rect.centery, cfg.YELLOW, 1, 3, cfg.PARTICLE_SPEED[0], cfg.PARTICLE_SPEED[1], 0))
            
            if ball.rect.colliderect(paddle.rect) and ball.speed_y > 0:
                if sound_enabled:
                    bounce_sound.play()
                ball.bounce_off(paddle.rect)
                offset = (ball.rect.centerx - paddle.rect.centerx) / (paddle.rect.width / 2)
                max_vx = cfg.MAX_BALL_SPEED_X
                ball.speed_x = max(-max_vx, min(max_vx, offset * max_vx))
                for _ in range(cfg.PARTICLE_COUNT // 2):
                    particles.append(Particle(ball.rect.centerx, ball.rect.centery, cfg.YELLOW, 1, 3, cfg.PARTICLE_SPEED[0], cfg.PARTICLE_SPEED[1], 0))

        for brick in bricks:
            brick.update()

        for brick in bricks[:]:
            if ball.rect.colliderect(brick.rect):
                ball.bounce_off(brick.rect)
                if brick.indestructible:
                    bounce_sound.play()
                    break
                else:
                    broken = brick.hit()
                    score += 10
                    
                    if broken:
                        for _ in range(cfg.PARTICLE_COUNT):
                            particles.append(Particle(brick.rect.centerx, brick.rect.centery, brick.color, 1, 4, cfg.PARTICLE_SPEED[0], cfg.PARTICLE_SPEED[1], cfg.PARTICLE_GRAVITY))
                        bricks.remove(brick)
                        if sound_enabled:
                            brick_break_sound.play()
                        if random.random() < 0.3:
                            power_up_type = random.choice(['shrink', 'grow', 'speed_up', 'slow', 'extra_life'])
                            power_ups.append(PowerUp(brick.rect.centerx, brick.rect.centery, power_up_type))
                    else:
                        if sound_enabled:
                            bounce_sound.play()
                    break

        
        for power_up in power_ups[:]:
            power_up.update()
            if power_up.rect.top > screen_height:
                power_ups.remove(power_up)
            elif paddle.rect.colliderect(power_up.rect):
                display_message = power_up.PROPERTIES[power_up.type]['message']
                message_timer = 120
                if power_up.type in ['shrink', 'grow']:
                    paddle.activate_power_up(power_up.type)
                elif power_up.type in ['slow', 'speed_up']:
                    ball.activate_power_up(power_up.type)
                elif power_up.type == 'extra_life':
                    lives += 1         
                power_ups.remove(power_up)
        
        if not any(not b.indestructible for b in bricks):
            current_level += 1
            if current_level > max_level:
                game_state = 'you_win'
            else:
                bricks = create_brick_wall(current_level)
                ball.reset()
                paddle.reset()



        # --- Draw all game objects ---
        paddle.draw(screen)
        ball.draw(screen)
        for brick in bricks:
            brick.draw(screen)
        for power_up in power_ups:
            power_up.draw(screen)
        
        # --- Draw UI ---
        score_text = game_font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        lives_text = game_font.render(f"Lives: {lives}", True, (255, 255, 255))
        screen.blit(lives_text, (screen_width - lives_text.get_width() - 10, 10))
        level_text = game_font.render(f"Level: {current_level}", True, (255, 255, 255))
        screen.blit(level_text, (screen_width // 2 - level_text.get_width() // 2, 10))


    elif game_state in ['game_over', 'you_win']:
        if game_state == 'you_win':
            firework_timer -= 1
            if firework_timer <= 0:
                fireworks.append(Firework(screen_width, screen_height))
                firework_timer = random.randint(20, 50)
            
            for firework in fireworks[:]:
                firework.update()
                if firework.is_dead():
                    fireworks.remove(firework)
            
            for firework in fireworks:
                firework.draw(screen)

        message = "GAME OVER" if game_state == 'game_over' else "YOU WIN!"
        text_surface = game_font.render(message, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(screen_width / 2, screen_height / 2 - 20))
        screen.blit(text_surface, text_rect)
        
        # ! PHASE: TITLE SCREEN !
        restart_surface = game_font.render("Press SPACE to return to Title", True, (255, 255, 255))
        # ! END PHASE: TITLE SCREEN !
        restart_rect = restart_surface.get_rect(center=(screen_width / 2, screen_height / 2 + 30))
        screen.blit(restart_surface, restart_rect)

    # --- Update effects and messages (these run in all states) ---
    if message_timer > 0:
        message_timer -= 1
        message_surface = message_font.render(display_message, True, (255, 255, 255))
        message_rect = message_surface.get_rect(center=(screen_width / 2, screen_height - 60))
        screen.blit(message_surface, message_rect)
        
    for particle in particles[:]:
        particle.update()
        if particle.size <= 0:
            particles.remove(particle)
    for particle in particles:
        particle.draw(screen)
    # ! END PHASE: TITLE SCREEN !

    # --- Final Display Update ---
    pygame.display.flip()
    clock.tick(60)
