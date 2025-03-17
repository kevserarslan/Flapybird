import pygame
from pygame.locals import *
import random

pygame.init()

clock = pygame.time.Clock()
fps = 60

screen_width = 864
screen_height = 700

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption('Flappy Bird')

# Define font
font = pygame.font.SysFont('Bauhaus 93', 60)

# Define colors
white = (255, 255, 255)

# Define game variables
ground_scroll = 0
scroll_speed = 4
flying = True
game_over = False
pipe_gap = 150
pipe_frequency = 1500  # milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False
lives = 5  # Initial number of lives
collision_cooldown = 0  # Cooldown for collisions

# Load images
bg = pygame.image.load('bg.png')
ground_img = pygame.image.load('ground.png')
button_img = pygame.image.load('restart.png')
heart_img = pygame.image.load('heart.png')  # Kalp resminizin dosya yolunu buraya girin
heart_img = pygame.transform.scale(heart_img, (40, 40))  # Kalp resminin boyutunu ayarlayın

def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

def reset_game():
    global lives, score, pass_pipe, flying, game_over
    pipe_group.empty()
    flappy.rect.x = 100
    flappy.rect.y = int(screen_height / 2)
    score = 0
    lives = 5  # Canları sıfırla
    pass_pipe = False
    flying = True
    game_over = False
    return score

class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0
        for num in range(1, 4):
            img = pygame.image.load(f'bird{num}.png')
            self.images.append(img)
        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.clicked = False

    def update(self):
        global lives, game_over

        if flying:
            # Gravity
            self.vel += 0.5
            if self.vel > 8:
                self.vel = 8
            if self.rect.bottom < 768:
                self.rect.y += int(self.vel)

        if not game_over:
            # Jump
            if pygame.mouse.get_pressed()[0] == 1 and not self.clicked:
                self.clicked = True
                self.vel = -10
            if pygame.mouse.get_pressed()[0] == 0:
                self.clicked = False

            # Handle the animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1
                if self.index >= len(self.images):
                    self.index = 0
            self.image = self.images[self.index]

            # Rotate the bird
            self.image = pygame.transform.rotate(self.images[self.index], self.vel * -2)
        else:
            self.image = pygame.transform.rotate(self.images[self.index], -90)

class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('pipe.png')
        self.rect = self.image.get_rect()
        # Position 1 is from the top, -1 is from the bottom
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - int(pipe_gap / 2)]
        if position == -1:
            self.rect.topleft = [x, y + int(pipe_gap / 2)]

    def update(self):
        self.rect.x -= scroll_speed
        if self.rect.right < 0:
            self.kill()

class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        # Get mouse position
        pos = pygame.mouse.get_pos()
        # Check if mouse is over the button
        if self.rect.collidepoint(pos):
            if pygame.mouse.get_pressed()[0] == 1:
                action = True
        # Draw button
        screen.blit(self.image, (self.rect.x, self.rect.y))
        return action

bird_group = pygame.sprite.Group()  # Sprite oyundaki grafiksel ögeler
pipe_group = pygame.sprite.Group()

flappy = Bird(100, int(screen_height / 2))
bird_group.add(flappy)

# Create restart button instance
button = Button(screen_width // 2 - 50, screen_height // 2 - 100, button_img)

run = True
while run:
    clock.tick(fps)

    # Draw background
    screen.blit(bg, (0, 0))

    bird_group.draw(screen)
    pipe_group.draw(screen)

    # Draw the ground
    screen.blit(ground_img, (ground_scroll, 600))  # Groundun yüksekliği

    # Draw hearts for remaining lives
    for i in range(lives):
        screen.blit(heart_img, (10 + i * (heart_img.get_width() + 5), 50))  # Kalpleri ekrana yerleştirme

    # Check the score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                and not pass_pipe:
            pass_pipe = True
        if pass_pipe:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                score += 1
                pass_pipe = False

    draw_text(str(score), font, white, int(screen_width / 2), 20)

    # Update collision cooldown
    if collision_cooldown > 0:
        collision_cooldown -= 1

    # Çarpışmayı kontrol et
    if collision_cooldown == 0:
        if pygame.sprite.groupcollide(bird_group, pipe_group, False, False):
            lives -= 1
            collision_cooldown = 20  # Çarpışma sonrası kısa bir süre çarpışmayı engelle
            if lives <= 0:
                game_over = True
            else:
                flappy.rect.x = 100
                flappy.rect.y = int(screen_height / 2)
                pass_pipe = False

    # Kuşun yere çarpıp çarpmadığını kontrol et
    if flappy.rect.bottom >= 600 and collision_cooldown == 0:
        lives -= 1
        collision_cooldown = 20  # Çarpışma sonrası kısa bir süre çarpışmayı engelle
        if lives <= 0:
            game_over = True
        else:
            flappy.rect.x = 100
            flappy.rect.y = int(screen_height / 2)
            pass_pipe = False

    if not game_over and flying:
        # Generate new pipes
        time_now = pygame.time.get_ticks()
        if time_now - last_pipe > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            btm_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, -1)
            top_pipe = Pipe(screen_width, int(screen_height / 2) + pipe_height, 1)
            pipe_group.add(btm_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        # Draw and scroll the ground
        ground_scroll -= scroll_speed
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        bird_group.update()
        pipe_group.update()

    # Look for game over and reset
    if game_over:
        if button.draw():
            game_over = False
            score = reset_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN and not flying and not game_over:
            flying = True

    pygame.display.update()

pygame.quit()
