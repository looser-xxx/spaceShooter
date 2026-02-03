import random
import pygame

class Ship(pygame.sprite.Sprite):
    """
    Represents the player's spaceship.
    """
    def __init__(self, speed, groups, window) -> None:
        """
        Initialize the ship with a specific speed.
        """
        super().__init__(groups)
        self.image = pygame.image.load("./images/player.png").convert_alpha()
        self.rect = self.image.get_frect(center=(window[0] / 2, window[1] / 2))
        self.direction = pygame.Vector2(1, 1)
        self.playerSpeed = speed

    def update(self) -> None:
        """Update the ship's state each frame."""
        pass

    def move(self, dt):
        """Move the ship based on its direction and delta time."""
        self.rect.centerx += self.direction.x * self.playerSpeed * dt
