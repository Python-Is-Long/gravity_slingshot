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

file_path = os.path.dirname(os.path.abspath(__file__))
os.chdir(file_path)
SCREEN_WIDTH, SCREEN_HEIGHT = pyautogui.size()
MAP_WIDTH, MAP_HEIGHT = (2500,2500)
SPRITE_SCALING = 0.5
# How fast the camera pans to the player. 1.0 is instant.
CAMERA_SPEED = 0.1
# How fast the character moves
PLAYER_MOVEMENT_SPEED = 7


class Bullet(arcade.Sprite):
    def __init__(self, image_file=None, scale=1.0, shadertoy=None, player_index=0):
        super().__init__(image_file, scale)
        self.type = None
        self.shadertoy = shadertoy
        self.player_index = player_index

    def draw(self):
        pass


class Player(arcade.Sprite):
    """ Player class """

    def __init__(self, image, scale):
        """ Set up the player """

        # Call the parent init
        super().__init__(image, scale)

        # Create a variable to hold our speed. 'angle' is created by the parent
        self.speed_vector = Vec2(0, 0)

    def update(self):
        # Convert angle in degrees to radians.
        angle_rad = math.radians(self.angle)

        # Rotate the ship
        self.angle += self.change_angle

        # Use math to find our change based on our speed and angle
        self.center_x += -self.speed * math.sin(angle_rad)
        self.center_y += self.speed * math.cos(angle_rad)


class MassBody(arcade.Sprite):
    def __init__(self, image_file=None, scale=1.0, shadertoy=None, player_index=0):
        super().__init__(image_file, scale)
        self.type = None
        self.shadertoy = shadertoy
        self.player_index = player_index

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

        self.time_taken = 0
        self.last_mouse_location = self.mouse_location = Vec2(0, 0)

        # Sprite lists
        self.player_list = arcade.SpriteList()
        self.coin_list = arcade.SpriteList()
        self.wall_list = arcade.SpriteList()


        # Set up the player
        self.score = 0
        self.player_sprite = arcade.Sprite(":resources:images/space_shooter/playerShip1_orange.png",
                                           SPRITE_SCALING)
        self.player_sprite.center_x = 50
        self.player_sprite.center_y = 50
        self.player_list.append(self.player_sprite)

        for i in range(5):

            # Create the coin instance
            coin = arcade.Sprite(":resources:images/items/coinGold.png", SPRITE_SCALING / 3)

            # Position the coin
            coin.center_x = random.randrange(MAP_WIDTH)
            coin.center_y = random.randrange(MAP_HEIGHT)

            # Add the coin to the lists
            self.coin_list.append(coin)


        # -- Set up several columns of walls
        for x in range(200, 1650, 210):
            for y in range(0, 1600, 64):
                # Randomly skip a box so the player can find a way through
                if random.randrange(5) > 0:
                    wall = arcade.Sprite(f":resources:images/space_shooter/meteorGrey_big{random.randint(1,4)}.png", SPRITE_SCALING)
                    wall.center_x = x
                    wall.center_y = y
                    self.wall_list.append(wall)

        self.physics_engine = arcade.PhysicsEngineSimple(self.player_sprite, self.wall_list)

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
        arcade.set_background_color(arcade.color.AMAZON)

        # Don't show the mouse cursor
        # self.window.set_mouse_visible(False)

    def on_draw(self):
        self.clear()

        # Select the camera we'll use to draw all our sprites
        self.camera_sprites.use()

        # Draw all the sprites.
        self.player_list.draw()
        self.coin_list.draw()
        self.wall_list.draw()

        # Select the (unscrolled) camera for our GUI
        self.camera_gui.use()

        # Draw the GUI
        output = f"Score: {self.score}"
        arcade.draw_text(output, 10, 30, arcade.color.WHITE, 14)
        output_total = f"Total Score: {self.window.total_score}"
        arcade.draw_text(output_total, 10, 10, arcade.color.WHITE, 14)

        if self.mouse_pressed:
            arcade.draw_line(start_x=self.last_mouse_x, start_y=self.last_mouse_y,
                             end_x=self.mouse_x, end_y=self.mouse_y,
                             color=(0, 255, 255), line_width=5)

    def on_update(self, delta_time):
        self.time_taken += delta_time

        if self.up_pressed and not self.down_pressed:
            self.player_sprite.change_y = PLAYER_MOVEMENT_SPEED
        elif self.down_pressed and not self.up_pressed:
            self.player_sprite.change_y = -PLAYER_MOVEMENT_SPEED
        if self.left_pressed and not self.right_pressed:
            self.player_sprite.change_x = -PLAYER_MOVEMENT_SPEED
        elif self.right_pressed and not self.left_pressed:
            self.player_sprite.change_x = PLAYER_MOVEMENT_SPEED

        # Generate a list of all sprites that collided with the player.
        hit_list = arcade.check_for_collision_with_list(self.player_sprite, self.coin_list)

        # Loop through each colliding sprite, remove it, and add to the
        # score.
        for coin in hit_list:
            coin.kill()
            self.score += 1
            self.window.total_score += 1

        # If we've collected all the games, then move to a "GAME_OVER"
        # state.
        if len(self.coin_list) == 0:
            game_over_view = GameOverView()
            game_over_view.time_taken = self.time_taken
            self.window.set_mouse_visible(True)
            self.window.show_view(game_over_view)

        # Call update on all sprites
        self.physics_engine.update()

        # Scroll the screen to the player
        self.scroll_to_player()

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
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
        self.time_taken = 0

    def on_show_view(self):
        arcade.set_background_color(arcade.color.BLACK)

    def on_draw(self):
        self.clear()
        """
        Draw "Game over" across the screen.
        """
        arcade.draw_text("Game Over", self.window.width / 2, self.window.height / 2, arcade.color.WHITE, 54, anchor_x="center")
        arcade.draw_text("Click to restart", self.window.width / 2, self.window.height / 2 - 100, arcade.color.WHITE, 24, anchor_x="center")

        time_taken_formatted = f"{round(self.time_taken, 2)} seconds"
        arcade.draw_text(f"Time taken: {time_taken_formatted}",
                         self.window.width / 2,
                         self.window.height / 2 - 200,
                         arcade.color.GRAY,
                         font_size=15,
                         anchor_x="center")

        output_total = f"Total Score: {self.window.total_score}"
        arcade.draw_text(output_total, 10, 10, arcade.color.WHITE, 14)

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