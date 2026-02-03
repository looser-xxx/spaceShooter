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

    def update(self, x, y) -> None:
        """Update the ship's state each frame."""
        self.direction.update(x, y)

    def move(self, dt):
        """Move the ship based on its direction and delta time."""
        self.rect.centerx += self.direction.x * self.playerSpeed * dt
        self.rect.centery += self.direction.y * self.playerSpeed * dt


class Stars(pygame.sprite.Sprite):
    """
    Represents a background star decoration.
    """

    def __init__(self, x, y, groups) -> None:
        """Initialize a star at a specific position."""
        super().__init__(groups)
        self.image = pygame.image.load("./images/star.png").convert_alpha()
        self.rect = self.image.get_frect(center=(x, y))


class SpaceShooter:
    """
    The main game class responsible for state and the game loop.
    """

    def __init__(self) -> None:
        """Initialize game resources, window, and entities."""
        self.window = (1920, 1080)
        self.allSprites = pygame.sprite.Group()
        self.playerSpeed = 300
        self.numberOfStars = 50
        self.screen = pygame.display.set_mode(self.window)
        self.createStars()
        self.player = Ship(self.playerSpeed, self.allSprites, self.window)
        self.runGame = True

    def checkEvents(self):
        """Handle all user input and system events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.runGame = False
    def movePlayer(x,y):
        self.player.update(x,y):
        

    def keyboardInput(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            pass
        if keys[pygame.K_s]:
            pass
        if keys[pygame.K_a]:
            pass
        if keys[pygame.K_d]:
            pass

    def createStars(self):
        """Populate the background with star sprites."""
        for i in range(self.numberOfStars):
            Stars(
                random.randint(0, self.window[0]),
                random.randint(0, self.window[1]),
                self.allSprites,
            )

    def run(self):
        """The main game loop."""
        while self.runGame:
            self.checkEvents()
            self.screen.fill("#212326")
            self.allSprites.draw(self.screen)
            pygame.display.flip()


def main():
    """Entry point for the application."""
    print("welcome to space shooter")
    game = SpaceShooter()
    game.run()


if __name__ == "__main__":
    main()
