import pygame
import random
import sys

# Constants
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SKY_BLUE = (135, 206, 235)
YELLOW = (255, 255, 0)
GREEN = (0, 200, 0)
BROWN = (139, 69, 19)
DARK_BROWN = (101, 67, 33)

# Game Physics
GRAVITY = 0.25
FLAP_STRENGTH = -6.5
PIPE_SPEED = 3
PIPE_FREQUENCY = 1500  # milliseconds
GAP_SIZE = 150

class Bird:
    def __init__(self):
        self.width = 30
        self.height = 30
        self.x = 50
        self.y = WINDOW_HEIGHT // 2
        self.velocity = 0
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        self.rect.y = int(self.y)

    def draw(self, screen):
        # Draw bird (yellow circle)
        pygame.draw.circle(screen, YELLOW, (int(self.x + self.width // 2), int(self.y + self.height // 2)), self.width // 2)
        # Draw eye (small black circle)
        eye_x = int(self.x + self.width * 0.7)
        eye_y = int(self.y + self.height * 0.3)
        pygame.draw.circle(screen, BLACK, (eye_x, eye_y), 3)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = 70
        self.gap_y = random.randint(100, WINDOW_HEIGHT - 100 - GAP_SIZE)
        self.top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        self.bottom_rect = pygame.Rect(self.x, self.gap_y + GAP_SIZE, self.width, WINDOW_HEIGHT - (self.gap_y + GAP_SIZE))
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED
        self.top_rect.x = int(self.x)
        self.bottom_rect.x = int(self.x)

    def draw(self, screen):
        pygame.draw.rect(screen, GREEN, self.top_rect)
        pygame.draw.rect(screen, GREEN, self.bottom_rect)
        # Add a small border to pipes
        pygame.draw.rect(screen, BLACK, self.top_rect, 2)
        pygame.draw.rect(screen, BLACK, self.bottom_rect, 2)

class FlappyBirdGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Flappy Bird Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 32)
        self.large_font = pygame.font.SysFont("Arial", 48)
        
        self.reset_game()
        self.game_started = False
        self.paused = False

    def reset_game(self):
        self.bird = Bird()
        self.pipes = []
        self.score = 0
        self.game_over = False
        self.last_pipe_time = pygame.time.get_ticks()
        self.game_started = False
        self.paused = False

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if not self.game_started:
                        self.game_started = True
                    if not self.game_over and not self.paused:
                        self.bird.flap()
                
                if event.key == pygame.K_p:
                    if not self.game_over and self.game_started:
                        self.paused = not self.paused
                
                if event.key == pygame.K_r:
                    self.reset_game()

    def update(self):
        if not self.game_started or self.game_over or self.paused:
            return

        # Update bird
        self.bird.update()

        # Check collisions with ground and ceiling
        if self.bird.rect.top < 0 or self.bird.rect.bottom > WINDOW_HEIGHT - 50:
            self.game_over = True

        # Generate pipes
        current_time = pygame.time.get_ticks()
        if current_time - self.last_pipe_time > PIPE_FREQUENCY:
            self.pipes.append(Pipe(WINDOW_WIDTH))
            self.last_pipe_time = current_time

        # Update pipes
        for pipe in self.pipes[:]:
            pipe.update()
            
            # Check collisions with pipes
            if self.bird.rect.colliderect(pipe.top_rect) or self.bird.rect.colliderect(pipe.bottom_rect):
                self.game_over = True

            # Scoring
            if not pipe.passed and pipe.x + pipe.width < self.bird.x:
                pipe.passed = True
                self.score += 1
            
            # Remove off-screen pipes
            if pipe.x + pipe.width < 0:
                self.pipes.remove(pipe)

    def draw(self):
        # Background
        self.screen.fill(SKY_BLUE)

        # Draw pipes
        for pipe in self.pipes:
            pipe.draw(self.screen)

        # Ground
        pygame.draw.rect(self.screen, BROWN, (0, WINDOW_HEIGHT - 50, WINDOW_WIDTH, 50))
        pygame.draw.rect(self.screen, GREEN, (0, WINDOW_HEIGHT - 50, WINDOW_WIDTH, 10))

        # Draw bird
        self.bird.draw(self.screen)

        # Draw score
        score_surface = self.font.render(f"Score: {self.score}", True, WHITE)
        score_rect = score_surface.get_rect(center=(WINDOW_WIDTH // 2, 50))
        self.screen.blit(score_surface, score_rect)

        # UI Messages
        if not self.game_started:
            start_surface = self.font.render("Press SPACE to Start", True, WHITE)
            start_rect = start_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(start_surface, start_rect)
        
        if self.game_over:
            # Semi-transparent overlay for game over
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))

            over_surface = self.large_font.render("GAME OVER", True, WHITE)
            over_rect = over_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 20))
            self.screen.blit(over_surface, over_rect)

            restart_surface = self.font.render("Press 'R' to Restart", True, WHITE)
            restart_rect = restart_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 40))
            self.screen.blit(restart_surface, restart_rect)

        if self.paused:
            pause_surface = self.large_font.render("PAUSED", True, WHITE)
            pause_rect = pause_surface.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2))
            self.screen.blit(pause_surface, pause_rect)

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = FlappyBirdGame()
    game.run()
