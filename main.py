import os
import random
import sys

import pygame


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class Ship(pygame.sprite.Sprite):
    """
    Represents the player's spaceship.
    """

    def __init__(self, speed, groups, window) -> None:
        """
        Initialize the ship with a specific speed.
        """
        super().__init__(groups)
        self.playArea = window
        self.image = pygame.image.load(
            resource_path("images/player.png")
        ).convert_alpha()
        self.rect = self.image.get_frect(
            center=(self.playArea[0] / 2, self.playArea[1] / 2)
        )
        self.direction = pygame.Vector2(1, 1)
        self.playerSpeed = speed

    def update(self, dt) -> None:
        """Update the ship's state each frame."""
        self.move(dt)
        self.checkCollisionWithWalls()

    def checkCollisionWithWalls(self):
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.playArea[0]:
            self.rect.right = self.playArea[0]
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.playArea[1]:
            self.rect.bottom = self.playArea[1]

    def updateDirection(self, direction):
        if direction == "w":
            self.direction.y = -1
        if direction == "s":
            self.direction.y = 1
        if direction == "a":
            self.direction.x = -1
        if direction == "d":
            self.direction.x = 1

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
        self.image = pygame.image.load(resource_path("images/star.png")).convert_alpha()
        self.rect = self.image.get_frect(center=(x, y))


class Laser(pygame.sprite.Sprite):
    def __init__(self, groups, pos, speed) -> None:
        super().__init__(groups)
        self.image = pygame.image.load(resource_path("images/laser.png"))
        self.rect = self.image.get_frect(center=pos)
        self.speed = speed

    def update(self, dt) -> None:
        self.rect.centery -= dt * self.speed
        if self.rect.bottom < 0:
            self.kill()


class Meteor(pygame.sprite.Sprite):
    def __init__(self, groups, pos, speed, direction, playSpace) -> None:
        super().__init__(groups)
        self.speed = speed
        self.playSpace = playSpace
        print(self.playSpace)
        self.image = pygame.image.load(
            resource_path("images/meteor.png")
        ).convert_alpha()
        self.rect = self.image.get_frect(center=pos)
        print(direction)
        self.direction = pygame.Vector2(direction[0], direction[1])

    def update(self, dt) -> None:
        self.move(dt)
        if (
            self.rect.top > self.playSpace[1] + 500
            or self.rect.top > self.playSpace[0] + 500
            or self.rect.left < -500
            or self.rect.left < -500
        ):
            self.kill()

    def move(self, dt):
        self.rect.centerx += self.direction.x * self.speed * dt
        self.rect.centery += self.direction.y * self.speed * dt


def loadAfterCooldown(eventTime, delay):
    if (eventTime + delay) < pygame.time.get_ticks():
        return True
    else:
        return False


class SpaceShooter:
    """
    The main game class responsible for state and the game loop.
    """

    def __init__(self) -> None:
        """Initialize game resources, window, and entities."""
        pygame.init()
        self.clock = pygame.time.Clock()
        self.window = (1920, 1080)
        self.allSprites = pygame.sprite.Group()
        self.screen = pygame.display.set_mode(self.window)
        self.numberOfStars = 50
        self.createStars()
        self.setUpMeteors()
        self.setUpPlayer()
        self.runGame = True

    def setUpMeteors(self):
        self.meteorSponTime = 0
        self.canSponMeteor = True
        self.meteorSpeed = 1000
        self.meteorSponRate = 1000

    def sponMeteor(self):
        sponOptionsX = [
            random.randint(-500, -100),
            random.randint(self.window[0] + 100, self.window[0] + 500),
        ]
        sponOptionsY = [
            random.randint(-500, -100),
            random.randint(self.window[1] + 100, self.window[1] + 500),
        ]

        pos = (random.choice(sponOptionsX), random.choice(sponOptionsY))
        options = [-2, -1, 1, 2]
        direction = (random.choice(options), random.randint(-2, 2))
        Meteor(self.allSprites, pos, self.meteorSpeed, direction, self.window)

    def spawnObjects(self):
        if self.canSponMeteor:
            self.sponMeteor()
            self.canSponMeteor = False
            self.meteorSponTime = pygame.time.get_ticks()

    def setUpPlayer(self):
        self.playerSpeed = 300
        self.player = Ship(self.playerSpeed, self.allSprites, self.window)
        self.canTP = True
        self.canShoot = True
        self.tpUseTime = 0
        self.shootTime = 0
        self.laserSpeed = 2800
        self.teleportCoolDownTime = 5000
        self.laserCoolDownTime = 250

    def checkEvents(self):
        """Handle all user input and system events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.runGame = False

        self.keyboardInput()
        if self.canShoot == False:
            self.canShoot = loadAfterCooldown(self.shootTime, self.laserCoolDownTime)
        if self.canTP == False:
            self.canTP = loadAfterCooldown(self.tpUseTime, self.teleportCoolDownTime)
        if self.canSponMeteor == False:
            self.canSponMeteor = loadAfterCooldown(
                self.meteorSponTime, self.meteorSponRate
            )

    def movePlayer(self, direction):
        self.player.updateDirection(direction)

    def keyboardInput(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.movePlayer("w")
        if keys[pygame.K_s]:
            self.movePlayer("s")
        if keys[pygame.K_a]:
            self.movePlayer("a")
        if keys[pygame.K_d]:
            self.movePlayer("d")
        if keys[pygame.K_t] and self.canTP:
            self.player.rect.centerx = random.randint(0, self.window[0])
            self.player.rect.centery = random.randint(0, self.window[1])
            self.player.direction.update(random.randint(-1, 1), random.randint(-1, 1))
            self.canTP = False
            self.tpUseTime = pygame.time.get_ticks()

        if keys[pygame.K_SPACE] and self.canShoot:
            Laser(self.allSprites, self.player.rect.center, self.laserSpeed)
            self.canShoot = False
            self.shootTime = pygame.time.get_ticks()

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
            dt = self.clock.tick() / 1000
            self.checkEvents()
            self.screen.fill("#212326")
            self.spawnObjects()
            self.allSprites.update(dt)
            self.allSprites.draw(self.screen)
            pygame.display.flip()


def main():
    """Entry point for the application."""
    print("welcome to space shooter")
    game = SpaceShooter()
    game.run()


if __name__ == "__main__":
    main()
