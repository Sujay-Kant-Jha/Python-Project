import pygame
import random
import sys

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Spaceship vs Asteroids")
clock = pygame.time.Clock()

def create_spaceship():
    surf = pygame.Surface((60, 60), pygame.SRCALPHA)
    pygame.draw.polygon(surf, (0, 255, 255), [(30, 0), (0, 60), (60, 60)])
    return surf

def create_bullet():
    surf = pygame.Surface((6, 14), pygame.SRCALPHA)
    pygame.draw.rect(surf, (255, 255, 0), (0, 0, 6, 14))
    return surf

def create_asteroid():
    surf = pygame.Surface((60, 60), pygame.SRCALPHA)
    pygame.draw.circle(surf, (120, 120, 120), (30, 30), 30)
    return surf

def create_star_background():
    return [[random.randint(0, WIDTH), random.randint(0, HEIGHT)] for _ in range(200)]

def draw_text(text, size, x, y, color=(255, 255, 255)):
    font = pygame.font.SysFont("arial", size)
    surface = font.render(text, True, color)
    screen.blit(surface, (x, y))

spaceship_img = create_spaceship()
bullet_img = create_bullet()
asteroid_img = create_asteroid()
stars = create_star_background()

button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 100, 200, 50)

def reset_game():
    return {
        "spaceship_rect": spaceship_img.get_rect(center=(WIDTH // 2, HEIGHT - 60)),
        "bullets": [],
        "asteroids": [],
        "asteroid_timer": 0,
        "bullet_timer": 0,
        "score": 0,
        "game_over": False,
        "lives": 3,
        "kills_since_last_special": 0,
        "special_ready": False,
        "fire_mode": "manual"  # or "auto"
    }

game = reset_game()
game_state = "menu"

while True:
    clock.tick(60)
    screen.fill((0, 0, 20))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Menu start
        if game_state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN and button_rect.collidepoint(event.pos):
                game = reset_game()
                game_state = "playing"

        if game_state == "playing" and not game["game_over"]:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game["fire_mode"] == "manual":
                    bullet_rect = bullet_img.get_rect(midbottom=game["spaceship_rect"].midtop)
                    game["bullets"].append(bullet_rect)
                if event.key == pygame.K_s and game["special_ready"]:
                    game["asteroids"].clear()
                    game["special_ready"] = False
                    game["kills_since_last_special"] = 0
                if event.key == pygame.K_m:
                    game["fire_mode"] = "auto" if game["fire_mode"] == "manual" else "manual"

    keys = pygame.key.get_pressed()

    # Background stars
    for star in stars:
        star[1] += 1
        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)
        pygame.draw.circle(screen, (255, 255, 255), star, 1)

    # Menu screen
    if game_state == "menu":
        draw_text("Spaceship vs Asteroids", 48, WIDTH // 2 - 220, HEIGHT // 2 - 180, (0, 255, 255))
        draw_text("Controls:", 32, WIDTH // 2 - 60, HEIGHT // 2 - 100)
        draw_text("← → to Move", 28, WIDTH // 2 - 60, HEIGHT // 2 - 60)
        draw_text("SPACE to Fire (manual)", 28, WIDTH // 2 - 60, HEIGHT // 2 - 30)
        draw_text("S: Special Fire, M: Toggle Auto/Manual", 24, WIDTH // 2 - 130, HEIGHT // 2)
        pygame.draw.rect(screen, (0, 200, 0), button_rect)
        draw_text("START GAME", 28, button_rect.x + 30, button_rect.y + 10)
        pygame.display.update()
        continue

    # Game Over
    if game["game_over"]:
        draw_text("GAME OVER", 60, WIDTH // 2 - 160, HEIGHT // 2 - 60, (255, 0, 0))
        draw_text(f"Score: {game['score']}", 40, WIDTH // 2 - 60, HEIGHT // 2 + 10)
        draw_text("Press R to Restart", 30, WIDTH // 2 - 110, HEIGHT // 2 + 60)
        pygame.display.update()
        if keys[pygame.K_r]:
            game_state = "menu"
        continue

    # Move spaceship
    if keys[pygame.K_LEFT] and game["spaceship_rect"].left > 0:
        game["spaceship_rect"].x -= 5
    if keys[pygame.K_RIGHT] and game["spaceship_rect"].right < WIDTH:
        game["spaceship_rect"].x += 5

    # Auto fire
    if game["fire_mode"] == "auto":
        game["bullet_timer"] += 1
        if game["bullet_timer"] >= 10:
            bullet_rect = bullet_img.get_rect(midbottom=game["spaceship_rect"].midtop)
            game["bullets"].append(bullet_rect)
            game["bullet_timer"] = 0

    # Bullets
    new_bullets = []
    for bullet in game["bullets"]:
        bullet.y -= 10
        if bullet.bottom > 0:
            screen.blit(bullet_img, bullet)
            new_bullets.append(bullet)
    game["bullets"] = new_bullets

    # Asteroids
    if len(game["asteroids"]) < 3 and game["asteroid_timer"] <= 0:
        x = random.randint(60, WIDTH - 60)
        asteroid_rect = asteroid_img.get_rect(midtop=(x, -60))
        game["asteroids"].append(asteroid_rect)
        game["asteroid_timer"] = 30
    else:
        game["asteroid_timer"] -= 1

    new_asteroids = []
    for asteroid in game["asteroids"]:
        asteroid.y += 3
        if asteroid.top < HEIGHT:
            screen.blit(asteroid_img, asteroid)
            new_asteroids.append(asteroid)
        else:
            game["lives"] -= 1
            if game["lives"] <= 0:
                game["game_over"] = True
    game["asteroids"] = new_asteroids

    # Collisions
    for bullet in game["bullets"][:]:
        for asteroid in game["asteroids"][:]:
            if bullet.colliderect(asteroid):
                try:
                    game["bullets"].remove(bullet)
                    game["asteroids"].remove(asteroid)
                    game["score"] += 1
                    game["kills_since_last_special"] += 1
                    if game["kills_since_last_special"] >= 10:
                        game["special_ready"] = True
                except ValueError:
                    pass
                break

    # Draw UI
    screen.blit(spaceship_img, game["spaceship_rect"])
    draw_text(f"Score: {game['score']}", 28, 10, 10)
    draw_text(f"Lives: {game['lives']}", 28, 10, 40)
    draw_text(f"Fire Mode: {game['fire_mode'].capitalize()}", 24, 10, 70)
    if game["special_ready"]:
        draw_text("Special Fire READY (Press S)", 24, 10, 100, (255, 255, 0))
    else:
        draw_text(f"Special Fire: {game['kills_since_last_special']}/10", 24, 10, 100)

    pygame.display.update()
