import arcade
import os
import math
import random

STATE_PLAYING = 'playing'
STATE_DEFEAT = 'lost'
STATE_WIN = 'win'


SCREEN_WIDTH = 800 * 3
SCREEN_HEIGHT = 600 * 3
SCREEN_TITLE = "Smashaga"
SCREEN_CENTER_X = SCREEN_WIDTH // 2
SCREEN_CENTER_Y = SCREEN_HEIGHT // 2

MOVEMENT_SPEED = 10

PLAYER_SIZE_FACTOR = 0.5
ENEMY_SIZE_FACTOR = 0.5

MISSILE_SPEED = 10

ENEMY_SHOOT_COOLDOWN = 25

ENEMIES = (
    ('enemy_1.png', 100),
    ('enemy_2.png', 200),
    ('enemy_3.png', 300)
)

class Player(arcade.Sprite):

    def update(self):
        self.center_x += self.change_x

        if self.left < 0:
            self.left = 0
        elif self.right > SCREEN_WIDTH - 1:
            self.right = SCREEN_WIDTH - 1

    def shoot(self, missile_list):
        missile = UpMissile('missile_blue.png')
        missile.center_y = self.top
        missile.center_x = self.center_x
        missile_list.append(missile)


class EnemyShip(arcade.Sprite):

    def __init__(self, row, column, *args, **kwargs):
        self.cooldown = random.randint(1, ENEMY_SHOOT_COOLDOWN)
        self.row = row
        self.column = column
        super().__init__(*args, **kwargs)

    def try_to_shoot(self, missile_list, delta_time):
        self.cooldown -= delta_time * 10

        if self.cooldown > 0:
            return

        if random.randint(0, 100) < 20:
            self.cooldown = ENEMY_SHOOT_COOLDOWN
            self.shoot(missile_list)
        

    def shoot(self, missile_list):
        missile = DownMissile('missile_yellow.png')
        missile.center_y = self.bottom
        missile.center_x = self.center_x
        missile_list.append(missile)

class Missile(arcade.Sprite):
    direction = 0

    def update(self):
        self.center_y = self.center_y + (self.direction * MISSILE_SPEED)

class UpMissile(Missile):
    direction = 1

class DownMissile(Missile):
    direction = -1


class MyGame(arcade.Window):
    """ Our custom Window Class"""

    def __init__(self):
        """ Initializer """
        # Call the parent class initializer
        super().__init__(SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE)

        # Set the working directory (where we expect to find files) to the same
        # directory this .py file is in. You can leave this out of your own
        # code, but it is needed to easily run the examples using "python -m"
        # as mentioned at the top of this program.
        file_path = os.path.dirname(os.path.abspath(__file__))
        os.chdir(file_path)

        self.set_mouse_visible(False)
        arcade.set_background_color(arcade.color.BLACK)

    def setup(self):

        self.score = 0
        self.state = STATE_PLAYING

        self.player_list = arcade.SpriteList()
        self.player_sprite = Player('player.png', scale=PLAYER_SIZE_FACTOR)
        self.player_sprite.center_x = SCREEN_WIDTH / 2
        self.player_sprite.center_y = self.player_sprite.height

        self.player_list.append(self.player_sprite)

        self.enemy_list = arcade.SpriteList()
        self.create_enemy_grid(3, 6)

        self.up_missile_list = arcade.SpriteList()
        self.down_missile_list = arcade.SpriteList()


    def spawn_enemy(self, row, column, texture, points):
        enemy = EnemyShip(filename=texture, scale=ENEMY_SIZE_FACTOR, row=row, column=column)
        enemy.center_x = SCREEN_CENTER_X + (1.5 * enemy.width * column)
        enemy.center_y = SCREEN_CENTER_Y + 1.5 * enemy.height * row
        enemy.bonus_points = points
        self.enemy_list.append(enemy)

    def create_enemy_grid(self, rows, columns):
        enemies = []
        middle = (columns // 2)
        for row in range(rows):
            texture, points = random.choice(ENEMIES)
            enemy_row = []
            enemies.append(enemy_row)
            for column in range(-middle, middle + 1):
                enemy_row.append(self.spawn_enemy(row, column, texture, points))

    def on_draw(self):
        """ Draw everything """
        arcade.start_render()
        
        if self.state == STATE_PLAYING:
            self.player_list.draw()
            self.enemy_list.draw()

            self.up_missile_list.draw()
            self.down_missile_list.draw()

        if self.state == STATE_WIN:
            arcade.draw_text('YOU WIN', SCREEN_WIDTH//3, SCREEN_HEIGHT //2, arcade.color.YELLOW, 74, bold=True)

        if self.state == STATE_DEFEAT:
            arcade.draw_text('YOU LOST', SCREEN_WIDTH//3, SCREEN_HEIGHT //2, arcade.color.RED, 74, bold=True)

        output = f"Score: {self.score}"
        arcade.draw_text(output, SCREEN_WIDTH *.1, SCREEN_HEIGHT * .9, arcade.color.WHITE, 24)


    def update(self, delta_time):
        """ Movement and game logic """
        if not self.state == STATE_PLAYING:
            return

        self.player_list.update()
        self.up_missile_list.update()
        self.down_missile_list.update()

        rows_per_column = {}
        for enemy in self.enemy_list:
            rows_per_column.setdefault(enemy.column, []).append(enemy.row)

        lowest_row_per_column = {}
        for column, rows in rows_per_column.items():
            lowest_row_per_column[column] = min(rows)

        for enemy in self.enemy_list:
            if enemy.row == lowest_row_per_column[enemy.column]:
                enemy.try_to_shoot(self.down_missile_list, delta_time)

        for missile in self.up_missile_list:
            collides = arcade.check_for_collision_with_list(missile, self.enemy_list)
            for enemy in collides:
                enemy.kill()
                missile.kill()
                self.score += enemy.bonus_points

            if missile.center_y > SCREEN_HEIGHT:
                missile.kill()

        for missile in self.down_missile_list:
            if missile.center_y < 0:
                missile.kill()

        if not len(self.enemy_list):
            self.state = STATE_WIN

        deadly_missiles = arcade.check_for_collision_with_list(self.player_sprite, self.down_missile_list)
        if deadly_missiles:
            self.player_sprite.kill()
            for missile in deadly_missiles:
                missile.kill()
            self.state = STATE_DEFEAT

    def on_key_press(self, key, modifiers):
        """Called whenever a key is pressed. """
        if key == arcade.key.LEFT:
            self.player_sprite.change_x = -MOVEMENT_SPEED
        elif key == arcade.key.RIGHT:
            self.player_sprite.change_x = MOVEMENT_SPEED
        if key in (arcade.key.UP, arcade.key.SPACE):
            self.player_sprite.shoot(self.up_missile_list)

        if self.state in (STATE_DEFEAT, STATE_WIN):
            if key in (arcade.key.ESCAPE, arcade.key.R):
                self.setup()

def main():
    """ Main method """
    window = MyGame()
    window.setup()
    arcade.run()


if __name__ == "__main__":
    main()