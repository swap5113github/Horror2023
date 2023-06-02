import random

from kivy.config import Config

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy import platform
from kivy.core.window import Window
from kivy.app import App
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad, Triangle , Ellipse
from kivy.properties import NumericProperty, Clock, ObjectProperty, StringProperty
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout
from kivy.lang.builder import Builder
from kivy.core.audio import SoundLoader
from kivy.metrics import dp

Builder.load_file("options.kv")


class MainWidget(RelativeLayout):
    from transforms import transform, transform_2D, transform_perspective
    from user_actions import keyboard_closed, on_keyboard_up, on_keyboard_down, on_touch_up, on_touch_down

    menu_widget = ObjectProperty()
    options_widget = ObjectProperty()
    perspective_point_x = NumericProperty(0)
    perspective_point_y = NumericProperty(0)

    V_NB_LINES = 18
    V_LINES_SPACING = .4  # percentage in screen width
    vertical_lines = []

    H_NB_LINES = 25
    H_LINES_SPACING = .1  # percentage in screen height
    horizontal_lines = []

    SPEED = 0
    current_offset_y = 0
    current_yloop = 0
    # score=0
    speed_increment = 0.1/60
    speed_increment_per_score = 20

    SPEED_X = 0
    current_speed_x = 0
    current_offset_x = 0

    NB_TILES = 16
    tiles = []
    tiles_coordinates = []

    SHIP_WIDTH = .08
    SHIP_HEIGHT = 0.035
    SHIP_BASE_Y = 0.04
    ship = None
    ship_coordinates = [(0, 0), (0, 0), (0, 0)]

    state_game_over = False
    state_game_has_started = False

    #menu_title = StringProperty("N I G H T M A R E")
    options_title = StringProperty("SELECT AT YOUR OWN RISK")
    #
    # menu_button_title = StringProperty("START")
    options_button_title_easy = StringProperty("Easy")
    options_button_title_medium = StringProperty("Medium")
    options_button_title_hard = StringProperty("Hard")
    score_txt = StringProperty()
    best_score_txt = StringProperty()

    score_bag = [0]

    sound_begin = None
    sound_galaxy = None
    sound_gameover_impact = None
    sound_gameover_voice = None
    sound_music1 = None
    sound_restart = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        # print("INIT W:" + str(self.width) + " H:" + str(self.height))
        self.init_vertical_lines()
        self.init_horizontal_lines()
        self.init_tiles()
        self.init_ship()
        self.reset_game()
        self.init_audio()

        self._keyboard = Window.request_keyboard(self.keyboard_closed, self)
        self._keyboard.bind(on_key_down=self.on_keyboard_down)
        self._keyboard.bind(on_key_up=self.on_keyboard_up)

        Clock.schedule_interval(self.update, 1.0 / 60.0)
        self.sound_galaxy.play()
    

    def init_audio(self):
        self.sound_begin = SoundLoader.load("audio/begin.wav")
        self.sound_galaxy = SoundLoader.load("audio/galaxy.wav")
        self.sound_gameover_impact = SoundLoader.load("audio/gameover_impact.wav")
        self.sound_gameover_voice = SoundLoader.load("audio/gameover_voice.wav")
        self.sound_music1 = SoundLoader.load("audio/music1.wav")
        self.sound_restart = SoundLoader.load("audio/restart.wav")

        self.sound_music1.volume = 1
        self.sound_begin.volume = .25
        self.sound_galaxy.volume = .25
        self.sound_gameover_voice.volume = .25
        self.sound_restart.volume = .25
        self.sound_gameover_impact.volume = .6
    
    
    def reset_game(self):

        self.tiles_coordinates = []
        self.pre_fill_tiles_coordinates()
        self.generate_tiles_coordinates()
        self.current_offset_y = 0
        self.current_yloop = 0
        self.current_speed_x = 0
        self.current_offset_x = 0
        self.score_txt = "SCORE: " + str(self.current_yloop)
        self.best_score_txt = "BEST SCORE: " + str(max(self.score_bag))



        self.state_game_over = False

    def is_desktop(self):
        if platform in ('linux', 'windows', 'macosx'):
            return True
        return False

    def init_ship(self):
        with self.canvas:
            Color(0,0,1)
            self.ship = Triangle()

    def update_ship(self):
        center_x = self.width / 2
        base_y = self.SHIP_BASE_Y * self.height
        ship_half_width = self.SHIP_WIDTH * self.width / 2
        ship_height = self.SHIP_HEIGHT * self.height
        # ....
        #    2
        #  1   3
        # self.transform
        self.ship_coordinates[0] = (center_x-ship_half_width, base_y)
        self.ship_coordinates[1] = (center_x, base_y + ship_height)
        self.ship_coordinates[2] = (center_x + ship_half_width, base_y)

        x1, y1 = self.transform(*self.ship_coordinates[0])
        x2, y2 = self.transform(*self.ship_coordinates[1])
        x3, y3 = self.transform(*self.ship_coordinates[2])

        self.ship.points = [x1, y1, x2, y2, x3, y3]

    def check_ship_collision(self):
        for i in range(0, len(self.tiles_coordinates)):
            ti_x, ti_y = self.tiles_coordinates[i]
            if ti_y > self.current_yloop + 1:
                return False
            if self.check_ship_collision_with_tile(ti_x, ti_y):
                return True
        return False

    def check_ship_collision_with_tile(self, ti_x, ti_y):
        xmin, ymin = self.get_tile_coordinates(ti_x, ti_y)
        xmax, ymax = self.get_tile_coordinates(ti_x + 1, ti_y + 1)
        for i in range(0, 3):
            px, py = self.ship_coordinates[i]
            if xmin <= px <= xmax and ymin <= py <= ymax:
                return True
        return False

    def init_tiles(self):
        with self.canvas:
            Color(0, 0, 0,1)
            for i in range(0, self.NB_TILES):
                self.tiles.append(Quad())

    def pre_fill_tiles_coordinates(self):
        for i in range(0, 10):
            self.tiles_coordinates.append((0, i))

    def generate_tiles_coordinates(self):
        last_x = 0
        last_y = 0
        for i in range(len(self.tiles_coordinates), self.NB_TILES):
            r = random.randint(0, 2)
            # 0 -> straight
            # 1 -> right
            # 2 -> left
            start_index = -int(self.V_NB_LINES / 2) + 1
            end_index = start_index + self.V_NB_LINES - 1
            if last_x <= start_index:
                r = 1
            if last_x >= end_index:
                r = 2

            self.tiles_coordinates.append((last_x, last_y))
            if r == 1:
                last_x += 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))
            if r == 2:
                last_x -= 1
                self.tiles_coordinates.append((last_x, last_y))
                last_y += 1
                self.tiles_coordinates.append((last_x, last_y))

            last_y += 1

        #print("foo2")

    def init_vertical_lines(self):
        with self.canvas:
            Color(0, 0, 0,0)
            #self.line = Line(points=[100, 0, 100, 100])
            for i in range(0, self.V_NB_LINES):
                self.vertical_lines.append(Line())

    def get_line_x_from_index(self, index):
        central_line_x = self.perspective_point_x
        spacing = self.V_LINES_SPACING * self.width
        offset = index - 0.5
        line_x = central_line_x + offset*spacing + self.current_offset_x
        return line_x

    def get_line_y_from_index(self, index):
        spacing_y = self.H_LINES_SPACING*self.height
        line_y = index*spacing_y-self.current_offset_y
        return line_y

    def get_tile_coordinates(self, ti_x, ti_y):
        ti_y = ti_y - self.current_yloop
        x = self.get_line_x_from_index(ti_x)
        y = self.get_line_y_from_index(ti_y)
        return x, y

    def update_tiles(self):
        for i in range(0, self.NB_TILES):
            tile = self.tiles[i]
            tile_coordinates = self.tiles_coordinates[i]
            xmin, ymin = self.get_tile_coordinates(tile_coordinates[0], tile_coordinates[1])
            xmax, ymax = self.get_tile_coordinates(tile_coordinates[0]+1, tile_coordinates[1]+1)

            #  2    3
            #
            #  1    4
            x1, y1 = self.transform(xmin, ymin)
            x2, y2 = self.transform(xmin, ymax)
            x3, y3 = self.transform(xmax, ymax)
            x4, y4 = self.transform(xmax, ymin)

            tile.points = [x1, y1, x2, y2, x3, y3, x4, y4]

    def update_vertical_lines(self):
        # -1 0 1 2
        start_index = -int(self.V_NB_LINES/2)+1
        for i in range(start_index, start_index+self.V_NB_LINES):
            line_x = self.get_line_x_from_index(i)

            x1, y1 = self.transform(line_x, 0)
            x2, y2 = self.transform(line_x, self.height)
            self.vertical_lines[i].points = [x1, y1, x2, y2]

    def init_horizontal_lines(self):
        with self.canvas:
            Color(0, 0, 0,0)
            for i in range(0, self.H_NB_LINES):
                self.horizontal_lines.append(Line())

    def update_horizontal_lines(self):
        start_index = -int(self.V_NB_LINES / 2) + 1
        end_index = start_index+self.V_NB_LINES-1

        xmin = self.get_line_x_from_index(start_index)
        xmax = self.get_line_x_from_index(end_index)
        for i in range(0, self.H_NB_LINES):
            line_y = self.get_line_y_from_index(i)
            x1, y1 = self.transform(xmin, line_y)
            x2, y2 = self.transform(xmax, line_y)
            self.horizontal_lines[i].points = [x1, y1, x2, y2]

    def update(self, dt):
        # print("dt: " + str(dt*60))
        time_factor = dt*60
        self.update_vertical_lines()
        self.update_horizontal_lines()
        self.update_tiles()
        self.update_ship()
        self.update_score_bag()
        # self.score=self.current_yloop
        # print(self.current_yloop)
        self.update_speed_per_score()

        if not self.state_game_over and self.state_game_has_started:
            
            speed_y = self.SPEED * self.height / 100
            self.current_offset_y += speed_y * time_factor

            spacing_y = self.H_LINES_SPACING * self.height
            if self.current_offset_y >= spacing_y:
                self.current_offset_y -= spacing_y
                self.current_yloop += 1
                self.score_txt = "SCORE: " + str(self.current_yloop)
                self.generate_tiles_coordinates()
                #print("loop : " + str(self.current_yloop))

            speed_x = self.current_speed_x * self.width / 100
            self.current_offset_x += speed_x * time_factor

        if not self.check_ship_collision() and not self.state_game_over:
            self.state_game_over = True
            self.options_title = "G A M E  O V E R\n\n   R E S T A R T"
            self.options_button_title_easy = "EASY"
            self.options_button_title_medium = "MEDIUM"
            self.options_button_title_hard = "HARD"
            self.options_widget.opacity = 1
            self.sound_music1.stop()
            self.sound_gameover_impact.play()
            Clock.schedule_once(self.play_game_over_voice_sound, 3)
    def update_score_bag(self):
        if self.state_game_over:
            self.score_bag.append(self.current_yloop)
    
    def update_speed_per_score(self):
        if self.current_yloop % self.speed_increment_per_score == 0 and self.current_yloop!=0 :
            self.SPEED += self.speed_increment
            
    def play_game_over_voice_sound(self, dt):
        if self.state_game_over:
            self.sound_gameover_voice.play()
    
    #def on_menu_button_pressed(self):


    def on_options_button_easy_pressed(self):
        if self.state_game_over:
            self.sound_restart.play()
            
        else:
            self.sound_begin.play()
        self.sound_music1.play()
        self.state_game_has_started = True
        self.SPEED = 0.4
        print(self.current_yloop)
        self.update_speed_per_score()
        self.SPEED_X = 2.0
        print(self.SPEED)
        self.options_widget.opacity = 0
        self.reset_game()
        
        
    def on_options_button_medium_pressed(self):
        if self.state_game_over:
            self.sound_restart.play()
            
        else:
            self.sound_begin.play()
        self.sound_music1.play()
        self.state_game_has_started = True
        self.SPEED = 0.6
        self.update_speed_per_score()
        self.SPEED_X = 2.0
        self.options_widget.opacity = 0
        self.reset_game()
    def on_options_button_hard_pressed(self):
        if self.state_game_over:
            self.sound_restart.play()
            
        else:
            self.sound_begin.play()
        self.sound_music1.play()
        self.state_game_has_started = True
        self.SPEED = 0.9
        self.update_speed_per_score()
        self.SPEED_X = 2.0
        self.options_widget.opacity = 0
        self.reset_game()


class GalaxyApp(App):
    pass


GalaxyApp().run()
     
