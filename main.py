import math
import os
import random
import sys

import pygame


def resource_path(relative_path) -> str:
    """
    Get absolute path to resource, works for dev and for PyInstaller.

    Args:
        relative_path (str): The relative path to the resource.

    Returns:
        str: The absolute path to the resource.
    """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


def loadAfterCooldown(eventTime, delay) -> bool:
    """
    Check if a cooldown period has passed.

    Args:
        eventTime (int): The timestamp when the event last occurred.
        delay (int): The duration of the cooldown in milliseconds.

    Returns:
        bool: True if the cooldown has passed, False otherwise.
    """
    if (eventTime + delay) < pygame.time.get_ticks():
        return True
    else:
        return False


class Ship(pygame.sprite.Sprite):
    """
    Represents the player's spaceship.
    """

    def __init__(self, speed, groups, window) -> None:
        """
        Initialize the ship with a specific speed.

        Args:
            speed (float): The movement speed of the ship.
            groups (pygame.sprite.Group): The sprite groups to add the ship to.
            window (tuple): The dimensions of the game window.
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
        """
        Update the ship's state each frame.

        Args:
            dt (float): Time delta since the last frame.
        """
        self.move(dt)
        self.checkCollisionWithWalls()

    def checkCollisionWithWalls(self) -> None:
        """
        Constrain the ship within the game window boundaries.
        """
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.playArea[0]:
            self.rect.right = self.playArea[0]
        if self.rect.top < 0:
            self.rect.top = 0
        if self.rect.bottom > self.playArea[1]:
            self.rect.bottom = self.playArea[1]

    def updateDirection(self, direction) -> None:
        """
        Update the ship's movement direction based on input key.

        Args:
            direction (str): The key corresponding to the direction ('w', 'a', 's', 'd').
        """
        if direction == "w":
            self.direction.y = -1
        if direction == "s":
            self.direction.y = 1
        if direction == "a":
            self.direction.x = -1
        if direction == "d":
            self.direction.x = 1

    def move(self, dt) -> None:
        """
        Move the ship based on its direction and delta time.

        Args:
            dt (float): Time delta since the last frame.
        """
        self.rect.centerx += self.direction.x * self.playerSpeed * dt
        self.rect.centery += self.direction.y * self.playerSpeed * dt


class Stars(pygame.sprite.Sprite):
    """
    Represents a background star decoration.
    """

    def __init__(self, x, y, groups) -> None:
        """
        Initialize a star at a specific position.

        Args:
            x (int): The x-coordinate.
            y (int): The y-coordinate.
            groups (pygame.sprite.Group): The sprite groups this star belongs to.
        """
        super().__init__(groups)
        self.image = pygame.image.load(resource_path("images/star.png")).convert_alpha()
        self.rect = self.image.get_frect(center=(x, y))


class Laser(pygame.sprite.Sprite):
    """
    Represents a projectile fired by the player.
    """

    def __init__(self, groups, pos, speed) -> None:
        """
        Initialize the laser.

        Args:
            groups (pygame.sprite.Group): The sprite groups to add the laser to.
            pos (tuple): The starting position (x, y).
            speed (float): The speed of the laser.
        """
        super().__init__(groups)
        self.image = pygame.image.load(resource_path("images/laser.png"))
        self.rect = self.image.get_frect(center=pos)
        self.speed = speed

    def update(self, dt) -> None:
        """
        Move the laser and remove it if it goes off-screen.

        Args:
            dt (float): Time delta since the last frame.
        """
        self.rect.centery -= dt * self.speed
        if self.rect.bottom < 0:
            self.kill()


class Meteor(pygame.sprite.Sprite):
    """
    Represents an obstacle that flies across the screen.
    """

    def __init__(self, groups, pos, speed, direction, playSpace) -> None:
        """
        Initialize the meteor with speed, direction, and spawn position.

        Args:
            groups (pygame.sprite.Group): The sprite groups to add the meteor to.
            pos (tuple): The starting position (x, y).
            speed (float): The speed of the meteor.
            direction (tuple): The direction vector (x, y).
            playSpace (tuple): The dimensions of the game window.
        """
        super().__init__(groups)
        self.speed = speed
        self.playSpace = playSpace
        self.image = pygame.image.load(
            resource_path("images/meteor.png")
        ).convert_alpha()
        self.rect = self.image.get_frect(center=pos)
        self.direction = pygame.Vector2(direction[0], direction[1])

    def update(self, dt) -> None:
        """
        Update meteor position and check for out-of-bounds.

        Args:
            dt (float): Time delta since the last frame.
        """
        self.move(dt)
        if (
            self.rect.top > self.playSpace[1] + 500
            or self.rect.top > self.playSpace[0] + 500
            or self.rect.left < -500
            or self.rect.left < -500
        ):
            self.kill()

    def move(self, dt) -> None:
        """
        Move the meteor based on direction and speed.

        Args:
            dt (float): Time delta since the last frame.
        """
        self.rect.centerx += self.direction.x * self.speed * dt
        self.rect.centery += self.direction.y * self.speed * dt


class tempRect(pygame.sprite.Sprite):
    def __init__(self, groups, x, y) -> None:
        super().__init__(groups)
        pass


class SpaceShooter:
    """
    The main game class responsible for state and the game loop.
    """

    def __init__(self) -> None:
        """
        Initialize game resources, window, and entities.
        """
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

    def setUpMeteors(self) -> None:
        """
        Initialize meteor spawning parameters.
        """
        self.meteorSponTime = 0
        self.canSponMeteor = True
        self.meteorSpeed = 1000
        self.meteorSponRate = 1000

    def findSponPoint(self):
        pass

    def sponMeteor(self) -> None:
        """
        Spawn a single meteor at a random position outside the screen.
        """
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
        Meteor(
            self.allSprites,
            pos,
            random.randint(int(self.meteorSpeed / 2), self.meteorSpeed),
            direction,
            self.window,
        )

    def spawnObjects(self) -> None:
        """
        Manage object spawning logic (e.g., meteors).
        """
        if self.canSponMeteor:
            self.sponMeteor()
            self.canSponMeteor = False
            self.meteorSponTime = pygame.time.get_ticks()

        self.draw_aim_line()

    def draw_aim_line(self):
        # 1. Define how long the line MUST be (e.g., 200 pixels)
        radius = 320

        # 2. Get Start (Player) and Target (Mouse)
        start_pos = pygame.Vector2(self.player.rect.center)
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

        # 3. Get the Direction
        direction_vector = mouse_pos - start_pos

        # Safety check: avoid crash if mouse is perfectly on player
        if direction_vector.length() > 0:

            # 4. Normalize (Make length 1) and Scale (Make length 'radius')
            direction_normalized = direction_vector.normalize()
            fixed_length_vector = direction_normalized * radius

            # 5. Calculate the FINAL position
            self.tpPos = start_pos + fixed_length_vector

            # 6. Draw the line
            # CHECK THIS LINE CAREFULLY:
            # We draw from 'start_pos' to 'end_pos' (NOT mouse_pos)
            pygame.draw.line(self.screen, "red", start_pos, self.tpPos, 2)

    def setUpPlayer(self) -> None:
        """
        Initialize player settings and cooldowns.
        """
        self.playerSpeed = 300
        self.player = Ship(self.playerSpeed, self.allSprites, self.window)
        self.canTP = True
        self.canShoot = True
        self.tpUseTime = 0
        self.shootTime = 0
        self.laserSpeed = 2800
        self.teleportCoolDownTime = 5000
        self.tpPos = (0, 0)
        self.laserCoolDownTime = 250

    def checkEvents(self) -> None:
        """
        Handle all user input and system events.
        """
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

    def movePlayer(self, direction) -> None:
        """
        Handle player movement input.

        Args:
            direction (str): The direction key pressed.
        """
        self.player.updateDirection(direction)

    def keyboardInput(self) -> None:
        """
        Check and respond to keyboard presses.
        """
        keys = pygame.key.get_pressed()
        mouse = pygame.mouse.get_pressed()
        if keys[pygame.K_w]:
            self.movePlayer("w")
        if keys[pygame.K_s]:
            self.movePlayer("s")
        if keys[pygame.K_a]:
            self.movePlayer("a")
        if keys[pygame.K_d]:
            self.movePlayer("d")
        if keys[pygame.K_t] and self.canTP:
            self.player.rect.centerx, self.player.rect.centery = self.tpPos
            # self.player.direction.update(random.randint(-1, 1), random.randint(-1, 1))
            self.canTP = False
            self.tpUseTime = pygame.time.get_ticks()

        if mouse[0] and self.canShoot:
            Laser(self.allSprites, self.player.rect.center, self.laserSpeed)
            self.canShoot = False
            self.shootTime = pygame.time.get_ticks()

    def createStars(self) -> None:
        """
        Populate the background with star sprites.
        """
        for i in range(self.numberOfStars):
            Stars(
                random.randint(0, self.window[0]),
                random.randint(0, self.window[1]),
                self.allSprites,
            )

    def run(self) -> None:
        """
        The main game loop.
        """
        while self.runGame:
            dt = self.clock.tick() / 1000
            self.checkEvents()
            self.screen.fill("#212326")
            self.spawnObjects()
            self.allSprites.update(dt)
            self.allSprites.draw(self.screen)
            pygame.display.flip()


def main() -> None:
    """
    Entry point for the application.
    """
    print("welcome to space shooter")
    game = SpaceShooter()
    game.run()


if __name__ == "__main__":
    main()
