import math
import os
import random
import sys

import pygame


# --- Utility Functions ---


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


# --- Sprite Classes ---


class Stars(pygame.sprite.Sprite):
    """
    Represents a background star decoration.
    """

    def __init__(self, x, y, groups, speed, screen, size, image, angle) -> None:
        """
        Initialize a star at a specific position.

        Args:
            x (int): The x-coordinate.
            y (int): The y-coordinate.
            groups (pygame.sprite.Group): The sprite groups this star belongs to.
            speed (float): The speed at which the star moves down.
            screen (tuple): The screen dimensions.
            size (int): The size of the star.
            image (pygame.Surface): The image of the star.
            angle (float): The initial rotation angle.
        """
        self._layer = 0
        super().__init__(groups)
        self.orignalImagje = image
        self.orignalImagje = pygame.transform.scale(self.orignalImagje, (size, size))
        self.image = self.orignalImagje
        self.rect = self.image.get_frect(center=(x, y))
        self.speed = speed
        self.playArea = screen
        self.angle = angle
        self.rotSpeed = 10

    def update(self, dt) -> None:
        """
        Update the star's position and rotation.

        Args:
            dt (float): Time delta since the last frame.
        """
        self.rect.bottom += dt * self.speed
        self.rotate(dt)
        if self.rect.top > self.playArea[1]:
            self.kill()

    def rotate(self, dt):
        """
        Rotate the star based on its rotation speed and delta time.

        Args:
            dt (float): Time delta since the last frame.
        """
        self.angle += self.rotSpeed * dt
        self.image = pygame.transform.rotate(self.orignalImagje, self.angle)
        self.rect = self.image.get_frect(center=self.rect.center)


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
        self._layer = 1
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


class Laser(pygame.sprite.Sprite):
    """
    Represents a projectile fired by the player.
    """

    def __init__(self, groups, pos, speed, angle) -> None:
        """
        Initialize the laser.

        Args:
            groups (pygame.sprite.Group): The sprite groups to add the laser to.
            pos (tuple): The starting position (x, y).
            speed (float): The speed of the laser.
            angle (float): The angle at which the laser is fired.
        """
        self._layer = 2
        super().__init__(groups)
        self.image = pygame.image.load(resource_path("images/laser.png"))
        self.image = pygame.transform.scale(self.image, (15.5, 97.7))
        self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_frect(center=pos)
        self.speed = speed
        self.angleFactor = pygame.Vector2(0, 0)
        self.angle = angle
        self.pos = self.rect.center

    def update(self, dt) -> None:
        """
        Move the laser and remove it if it goes off-screen.

        Args:
            dt (float): Time delta since the last frame.
        """
        print(self.angleFactor.x)
        print(self.angleFactor.y)
        self.rect.center = self.pos
        self.pos += self.angleFactor * dt * 1000

        if self.rect.bottom < -15 or self.rect.bottom > 1920:
            self.kill()
        self.findAngle()

    def findAngle(self):
        """
        Calculate the movement vector based on the firing angle.
        """
        rad = math.radians(self.angle)
        self.angleFactor.update(-math.sin(rad), -math.cos(rad))


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
        self._layer = 3
        super().__init__(groups)
        self.playArea = window
        self.orignalImagge = pygame.image.load(
            resource_path("images/player.png")
        ).convert_alpha()

        self.orignalImagge = pygame.transform.scale(self.orignalImagge, (69.5, 97.7))
        self.image = self.orignalImagge
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
        self.dt = dt

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
        self.direction.update(0, 0)

    def rotate(self, angle):
        """
        Rotate the ship to a specific angle.

        Args:
            angle (float): The target rotation angle.
        """
        oldCenter = self.rect.center
        self.image = pygame.transform.rotate(self.orignalImagge, angle)
        self.rect = self.image.get_frect(center=oldCenter)


class tempRect(pygame.sprite.Sprite):
    """
    A temporary rectangle sprite (placeholder).
    """

    def __init__(self, groups, x, y) -> None:
        """
        Initialize the temporary rectangle.

        Args:
            groups (pygame.sprite.Group): The sprite groups this belongs to.
            x (int): x-coordinate.
            y (int): y-coordinate.
        """
        super().__init__(groups)
        pass


# --- Main Game Engine ---


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
        self.allSprites = pygame.sprite.LayeredUpdates()
        self.screen = pygame.display.set_mode(self.window)
        self.numberOfStars = 50
        self.loadBackGround()
        self.createStars()
        self.setUpMeteors()
        self.setUpPlayer()
        self.setUpStars()
        self.runGame = True
        self.playerAngle = 0
        self.dt = 0

    # --- Initialization & Setup ---

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
        self.laserCoolDownTime = 150

    def setUpMeteors(self) -> None:
        """
        Initialize meteor spawning parameters.
        """
        self.meteorSponTime = 0
        self.canSponMeteor = True
        self.meteorSpeed = 1000
        self.meteorSponRate = 500

    def setUpStars(self):
        """
        Initialize parameters for star spawning.
        """
        image = pygame.image.load(resource_path("images/player.png")).convert_alpha()
        self.starInfoForSpon = {
            "spon": [True, True, True, True, True, True],
            "itemCount": 6,
            "amount": [50, 60, 55, 1, 1, 1],
            "x": self.window[0],
            "y": -500,
            "speed": [50, 30, 20, 50, 30, 20],
            "size": [100, 75, 50, 100, 75, 50],
            "image": image,
        }

    def loadBackGround(self):
        """
        Load and scale the background image.
        """
        self.backgroundImage = pygame.image.load(
            resource_path("images/backGround.png")
        ).convert()
        self.backgroundImage = pygame.transform.scale(self.backgroundImage, self.window)

    def createStars(self) -> None:
        """
        Populate the background with initial star sprites.
        """
        image = pygame.image.load(resource_path("images/star.png")).convert_alpha()
        for i in range(self.numberOfStars):
            Stars(
                random.randint(0, self.window[0]),
                random.randint(0, self.window[1]),
                self.allSprites,
                10,
                self.window,
                20,
                image,
                random.randint(0, 360),
            )

    # --- Spawning Logic ---

    def spawnObjects(self) -> None:
        """
        Manage object spawning logic (e.g., meteors).
        """
        if self.canSponMeteor:
            self.sponMeteor()
            self.canSponMeteor = False
            self.meteorSponTime = pygame.time.get_ticks()

        self.draw_aim_line()

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

    def sponStars(self, data):
        """
        Spawn stars based on provided configuration data.

        Args:
            data (dict): Star configuration parameters.
        """
        if data["spon"]:
            for j in range(data["itemCount"]):
                y = 0
                if data["y"] > 0:
                    y = random.random(0, data["y"])
                else:
                    y = random.randint(data["y"], 0)
                for i in range(data["amount"][j]):
                    Stars(
                        random.randint(0, data["x"]),
                        y,
                        self.allSprites,
                        data["speed"][j],
                        self.window,
                        data["size"][j],
                        data["image"],
                        random.randint(0, 360),
                    )
                data["spon"] = False

    def findSponPoint(self):
        """
        Logic for finding a spawn point (Placeholder).
        """
        pass

    # --- Input & Event Handling ---

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

    def keyboardInput(self) -> None:
        """
        Check and respond to keyboard presses.
        """
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
            self.player.rect.centerx, self.player.rect.centery = self.tpPos
            self.canTP = False
            self.tpUseTime = pygame.time.get_ticks()

        if keys[pygame.K_SPACE] and self.canShoot:
            Laser(
                self.allSprites,
                self.player.rect.center,
                self.laserSpeed,
                self.playerAngle,
            )
            self.canShoot = False
            self.shootTime = pygame.time.get_ticks()

        if keys[pygame.K_RIGHT]:
            self.playerAngle += 150 * self.dt
        if keys[pygame.K_LEFT]:
            self.playerAngle -= 150 * self.dt
        self.player.rotate(self.playerAngle)

    def movePlayer(self, direction) -> None:
        """
        Handle player movement input.

        Args:
            direction (str): The direction key pressed ('w', 'a', 's', 'd').
        """
        self.player.updateDirection(direction)

    # --- Visuals & Rendering ---

    def draw_aim_line(self):
        """
        Draw a targeting line from the player towards the mouse position.
        """
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
            pygame.draw.line(self.screen, "red", start_pos, self.tpPos, 2)

    # --- Game Loop ---

    def run(self) -> None:
        """
        The main game loop.
        """
        while self.runGame:
            self.dt = self.clock.tick() / 1000
            self.checkEvents()
            self.screen.fill("#212326")
            self.screen.blit(self.backgroundImage, (0, 0))
            self.spawnObjects()
            self.allSprites.update(self.dt)
            self.allSprites.draw(self.screen)
            pygame.display.flip()


# --- Application Entry Point ---


def main() -> None:
    """
    Entry point for the application.
    """
    print("welcome to space shooter")
    game = SpaceShooter()
    game.run()


if __name__ == "__main__":
    main()