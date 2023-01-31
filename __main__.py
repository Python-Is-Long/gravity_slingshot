# 2023-1-29
import pyautogui
import arcade
from arcade.experimental.shadertoy import Shadertoy
import random
import math
import arcade
import random
import os
from pyglet.math import Vec2
from typing import Tuple, List, Dict, Union, Any, Optional
from stats import GameStats

file_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_path)
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
MAP_WIDTH, MAP_HEIGHT = (2500,2500)
SPRITE_SCALING = 0.5
# How fast the camera pans to the player. 1.0 is instant.
CAMERA_SPEED = 0.1
# How fast the character moves
PLAYER_MOVEMENT_SPEED = 0.01
PLANET_SCALE = 500
PLANET_DENSITY = 100000
G=1e-7


class MassSprite(arcade.Sprite):
    def __init__(self, image_file: str = None, scale: float = 1.0, mass: float = 0, change_angle: float = 0):
        super().__init__(image_file, scale)
        self.mass = mass
        self.speed_vector = Vec2(0, 0)
        self.change_speed_vector = Vec2(0, 0)
        self.change_angle = change_angle

    def update(self):
        self.angle += self.change_angle
        self.speed_vector += self.change_speed_vector
        self.center_x += self.speed_vector[0]
        self.center_y += self.speed_vector[1]
        self.change_speed_vector = Vec2(0, 0)

    @property
    def center(self) -> Vec2:
        return Vec2(self.center_x, self.center_y)

    def fall_towards(self, attractor):
        attractor: Union[MassSprite, MassSpriteCircle]
        vector = attractor.center - self.center
        direction = vector.normalize()
        gravity = G*attractor.mass/vector.mag**2
        self.change_speed_vector += direction.scale(gravity)


class MassSpriteCircle(arcade.SpriteCircle):
    def __init__(self, radius: int = 1, color=arcade.color.WHITE, soft=False, mass: float = 0):
        super().__init__(radius, color, soft)
        self.radius = radius
        self.mass = mass
        self.speed_vector = Vec2(0, 0)
        self.change_speed_vector = Vec2(0, 0)

    def update(self):
        self.speed_vector += self.change_speed_vector
        self.center_x += self.speed_vector[0]
        self.center_y += self.speed_vector[1]
        self.change_speed_vector = Vec2(0, 0)

    @property
    def center(self) -> Vec2:
        return Vec2(self.center_x, self.center_y)

    def fall_towards(self, attractor):
        attractor: Union[MassSprite, MassSpriteCircle]
        vector = attractor.center - self.center
        direction = vector.normalize()
        gravity = G * attractor.mass / vector.mag ** 2
        self.change_speed_vector += direction.scale(gravity)


class Planet(MassSpriteCircle):
    def __init__(self, radius: int = 1, color1=(69, 137, 133, 127), color2=(7, 67, 88, 127), soft=False, mass=0):
        super().__init__(radius=radius, color=color1, soft=soft, mass=mass)
        self.color1 = color1
        self.color2 = color2

    def draw(self):
        self.shape = arcade.create_ellipse_filled_with_colors(self.center_x, self.center_y, self.radius, self.radius,
                                                              inside_color=self.color1, outside_color=self.color2)
        self.shape.draw()


class Bullet(MassSprite):
    def __init__(self, image_file=None, scale=1.0, mass=0, player_index=0):
        super().__init__(image_file=image_file, scale=scale, mass=mass)
        self.player_index = player_index

    def draw(self):
        pass


class Coin(MassSprite):
    def __init__(self, image_file=None, scale=1.0, mass=0, change_angle=0):
        super().__init__(image_file=image_file, scale=scale, mass=mass, change_angle=change_angle)

    def draw(self):
        pass


class Player(MassSprite):
    def __init__(self, image_file=None, scale=1.0, mass=0):
        super().__init__(image_file=image_file, scale=scale, mass=mass)

    def draw(self):
        pass


class MenuView(arcade.View):
    def on_show_view(self):
        arcade.set_background_color(arcade.color.WHITE)

    def on_draw(self):
        self.clear()
        arcade.draw_text("Menu Screen", self.window.width / 2, self.window.height / 2,
                         arcade.color.BLACK, font_size=50, anchor_x="center")
        arcade.draw_text("Click to advance", self.window.width / 2, self.window.height / 2 - 75,
                         arcade.color.GRAY, font_size=20, anchor_x="center")

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = GameView()
        self.window.show_view(game_view)


class GameView(arcade.View):
    def __init__(self):
        super().__init__()

        self.stats = GameStats()
        self.last_mouse_location = self.mouse_location = Vec2(0, 0)

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.planet_list = arcade.SpriteList()


        # Set up the player
        self.player_sprite = Player(":resources:images/space_shooter/playerShip1_Orange.png", SPRITE_SCALING, mass=100)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)

        for i in range(5):

            # Create the coin instance
            coin = Coin(
                ":resources:images/items/star.png",
                SPRITE_SCALING/3,
                mass=10,
                change_angle=random.normalvariate(0, 10),
            )
            coin.speed_vector = Vec2(random.normalvariate(0,3), random.normalvariate(0,3))
            coin.center_x = random.randrange(MAP_WIDTH)
            coin.center_y = random.randrange(MAP_HEIGHT)

            # Add the coin to the lists
            self.coin_list.append(coin)


        # -- Set up several columns of walls
        for x in range(200, 1650, 210):
            for y in range(0, 1600, 64):
                # Randomly skip a box so the player can find a way through
                if random.randrange(100) < 2:
                    radius = PLANET_SCALE * random.uniform(1, 3)
                    mass = PLANET_DENSITY*radius**2
                    planet = Planet(
                        radius=int(PLANET_SCALE),
                        color1=(255, 255, 255, 127),
                        color2=(127, 127, 127, 127),
                        mass=mass,
                    )
                    planet.speed_vector = Vec2(random.normalvariate(0,3), random.normalvariate(0,3))
                    planet.center_x = x
                    planet.center_y = y
                    self.planet_list.append(planet)

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.planet_list)
        self.list_physics_engines = [arcade.PhysicsEngineSimple(planet, self.planet_list) for planet in self.planet_list]
        self.list_physics_engines += [arcade.PhysicsEngineSimple(coin, self.planet_list) for coin in self.coin_list]

        # Track the current state of what key is pressed
        self.left_pressed = False
        self.right_pressed = False
        self.up_pressed = False
        self.down_pressed = False
        self.mouse_pressed = False

        # Create the cameras. One for the GUI, one for the sprites.
        # We scroll the 'sprite world' but not the GUI.
        self.camera_sprites = arcade.Camera(self.window.width, self.window.height)
        self.camera_gui = arcade.Camera(self.window.width, self.window.height)

    @property
    def mouse_x(self):
        return self.mouse_location[0]

    @property
    def mouse_y(self):
        return self.mouse_location[1]

    @property
    def last_mouse_x(self):
        return self.last_mouse_location[0]

    @property
    def last_mouse_y(self):
        return self.last_mouse_location[1]

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

        # Don't show the mouse cursor
        # self.window.set_mouse_visible(False)

    def on_draw(self):
        self.clear()

        # Select the camera we'll use to draw all our sprites
        self.camera_sprites.use()

        # Draw all the sprites.
        self.player_list.draw()
        self.coin_list.draw()
        for planet in self.planet_list:
            planet: Planet
            planet.draw()
        self.planet_list.draw()

        # Select the (unscrolled) camera for our GUI
        self.camera_gui.use()

        # Draw the GUI
        output = f"Score: {self.stats.score}"
        arcade.draw_text(output, 10, 10, arcade.color.WHITE, 14)
        output = f"Moves: {self.stats.moves}"
        arcade.draw_text(output, 10, 30, arcade.color.WHITE, 14)

        # draw mouse drag speed vector
        if self.mouse_pressed:
            speed_vector = Vec2(self.mouse_x-self.last_mouse_x, self.mouse_y-self.last_mouse_y)
            delta_v = speed_vector.mag
            heading = math.degrees(speed_vector.heading)
            arcade.draw_line(start_x=self.last_mouse_x, start_y=self.last_mouse_y,
                             end_x=self.mouse_x, end_y=self.mouse_y,
                             color=arcade.color.ORANGE, line_width=min(5, math.ceil(delta_v/30)))
            arcade.draw_text(f"∆v: {round(delta_v, 2)} m/s", self.mouse_x + 20, self.mouse_y, arcade.color.WHITE, 14)
            arcade.draw_text(f"heading: {round(heading, 2)}°", self.mouse_x + 20, self.mouse_y+20, arcade.color.WHITE, 14)


    def on_update(self, delta_time):
        self.stats.time_taken += delta_time

        # Generate a list of all sprites that collided with the player.
        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)

        # Loop through each colliding sprite, remove it, and add to the
        # score.
        for coin in hit_list:
            coin.kill()
            self.stats.score += 1
            self.window.total_score += 1

        # If we've collected all the games, then move to a "GAME_OVER"
        # state.
        if len(self.coin_list) == 0:
            self.game_over()

        # gravity system
        for planet in self.planet_list:
            planet: Planet
            for player in self.player_list:
                player: Player
                player.fall_towards(planet)
            for coin in self.coin_list:
                coin: Coin
                coin.fall_towards(planet)
            for planet2 in self.planet_list:
                planet2: Planet
                if planet2 is not planet:
                    planet2.fall_towards(planet)

        # Call update on all sprites
        self.planet_list.update()
        self.player_list.update()
        self.coin_list.update()

        self.physics_engine.update()
        for engine in self.list_physics_engines:
            engine.update()

        # Scroll the screen to the player
        self.scroll_to_player()

    def game_over(self):
        game_over_view = GameOverView()
        game_over_view.stats = self.stats
        self.window.set_mouse_visible(True)
        self.window.show_view(game_over_view)

    def restart(self):
        menu_view = MenuView()
        self.window.set_mouse_visible(True)
        self.window.show_view(menu_view)

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.ESCAPE:
            self.restart()
        if key in (arcade.key.UP, arcade.key.W):
            self.up_pressed = True
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down_pressed = True
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = True
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = True

    def on_key_release(self, key, modifiers):
        """Called when the user releases a key. """
        if key in (arcade.key.UP, arcade.key.W):
            self.up_pressed = False
        elif key in (arcade.key.DOWN, arcade.key.S):
            self.down_pressed = False
        elif key in (arcade.key.LEFT, arcade.key.A):
            self.left_pressed = False
        elif key in (arcade.key.RIGHT, arcade.key.D):
            self.right_pressed = False

    def on_mouse_press(self, x, y, button, key_modifiers):
        self.mouse_pressed = True
        self.last_mouse_location = Vec2(x, y)

    def on_mouse_motion(self, x, y, _dx, _dy):
        """
        Called whenever the mouse moves.
        """
        self.mouse_location = Vec2(x, y)
        if self.mouse_pressed:
            angle = math.atan2(y-self.last_mouse_y, x-self.last_mouse_x)
            self.player_sprite.angle = math.degrees(angle)-90
        else:
            self.last_mouse_location = Vec2(x, y)

    def on_mouse_release(self, x, y, button, key_modifiers):
        if self.mouse_pressed:
            speed_vector = Vec2(self.mouse_x - self.last_mouse_x, self.mouse_y - self.last_mouse_y)
            # delta_v = speed_vector.mag
            # heading = math.degrees(speed_vector.heading)
            self.player_sprite.change_speed_vector += speed_vector.scale(PLAYER_MOVEMENT_SPEED)
            self.stats.moves += 1
            self.mouse_pressed = False

    def scroll_to_player(self):
        """
        Scroll the window to the player.
        if CAMERA_SPEED is 1, the camera will immediately move to the desired position.
        Anything between 0 and 1 will have the camera move to the location with a smoother
        pan.
        """
        position = Vec2(self.player_sprite.center_x - self.window.width / 2,
                        self.player_sprite.center_y - self.window.height / 2)
        self.camera_sprites.move_to(position, CAMERA_SPEED)

    def on_resize(self, width, height):
        """
        Resize window
        Handle the user grabbing the edge and resizing the window.
        """
        self.camera_sprites.resize(int(width), int(height))
        self.camera_gui.resize(int(width), int(height))


class GameOverView(arcade.View):
    def __init__(self):
        super().__init__()
        self.stats = GameStats()

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        """
        Draw "Game over" across the screen.
        """
        arcade.draw_text("Game Over", self.window.width / 2, self.window.height / 2, arcade.color.WHITE, 54, anchor_x="center")
        arcade.draw_text("Click to restart", self.window.width / 2, self.window.height / 2 - 100, arcade.color.WHITE, 24, anchor_x="center")

        time_taken_formatted = f"{round(self.stats.time_taken, 2)} seconds"
        arcade.draw_text(f"Time taken: {time_taken_formatted}",
                         self.window.width / 2,
                         self.window.height / 2 - 200,
                         arcade.color.GRAY,
                         font_size=15,
                         anchor_x="center")

        output_total = f"Score: {self.stats.score}"
        arcade.draw_text(output_total, 10, 10, arcade.color.WHITE, 14)
        output_total = f"Moves: {self.stats.moves}"
        arcade.draw_text(output_total, 10, 30, arcade.color.WHITE, 14)

    def on_mouse_press(self, _x, _y, _button, _modifiers):
        game_view = GameView()
        self.window.show_view(game_view)


def main():
    window = arcade.Window(SCREEN_WIDTH, SCREEN_HEIGHT, "Different Views Example")
    window.set_fullscreen(True)
    window.total_score = 0
    menu_view = MenuView()
    window.show_view(menu_view)
    arcade.run()


if __name__ == "__main__":
    main()