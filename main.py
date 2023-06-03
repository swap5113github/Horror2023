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

    def starting_tiles_coordinates(self):
        for i in range(0, 9):
            self.Tiles_coordinates.append((0, i))

    def produce_tiles_coordinates(self):
        LAST_x = 0
        LAST_y = 0

        # clean the coordinates that are out of the screen
        # tile_y < self.present_yloop
        for i in range(len(self.Tiles_coordinates)-1, -1, -1):
            if self.Tiles_coordinates[i][1] < self.present_yloop:
                del self.Tiles_coordinates[i]

        if len(self.Tiles_coordinates) > 0:
            LAST_coordinates = self.Tiles_coordinates[-1]
            LAST_x = LAST_coordinates[0]
            LAST_y = LAST_coordinates[1] + 1

        #print("foo1")

        for i in range(len(self.Tiles_coordinates), self.len_visible_tiles):
            r = random.randint(0, 2)
            # 0 -> straight
            # 1 -> right
            # 2 -> left
            starting_index = -int(self.Num_vertical_lines / 2) + 1
            ending_index = starting_index + self.Num_vertical_lines - 1
            if LAST_x <= starting_index:
                r = 1
            if LAST_x >= ending_index:
                r = 2

            self.Tiles_coordinates.append((LAST_x, LAST_y))
            if r == 1:
                LAST_x += 1
                self.Tiles_coordinates.append((LAST_x, LAST_y))
                LAST_y += 1
                self.Tiles_coordinates.append((LAST_x, LAST_y))
            if r == 2:
                LAST_x -= 1
                self.Tiles_coordinates.append((LAST_x, LAST_y))
                LAST_y += 1
                self.Tiles_coordinates.append((LAST_x, LAST_y))

            LAST_y += 1

        #print("foo2")

    def init_Vertical_Lines(self):
        with self.canvas:
            Color(0, 0, 0,0)
            #self.line = Line(points=[100, 0, 100, 100])
            for i in range(0, self.Num_vertical_lines):
                self.List_of_VLines.append(Line())

    def from_index_obtain_line_x(self, index):
        mid_line_x = self.point_x_in_perspective_view
        screen_dependent_spacing = self.Space_vertical_lines * self.width
        ofset = index - 0.5
        single_line_x = mid_line_x + ofset*screen_dependent_spacing + self.present_offset_x
        return single_line_x

    def from_index_obtain_line_y(self, index):
        screen_dependent_spacing_y = self.Space_horizontal_lines*self.height
        single_line_y = index*screen_dependent_spacing_y-self.present_offest_y
        return single_line_y

    def obtain_tile_coordinates(self, tile_x, tile_y):
        tile_y = tile_y - self.present_yloop
        x = self.from_index_obtain_line_x(tile_x)
        y = self.from_index_obtain_line_y(tile_y)
        return x, y

    def Update_tiles(self):
        # self.Update_path_color()
        for i in range(0, self.len_visible_tiles):
            specific_tile = self.Tiles[i]
            specific_tile_coordinates = self.Tiles_coordinates[i]
            x_min, y_min = self.obtain_tile_coordinates(specific_tile_coordinates[0], specific_tile_coordinates[1])
            x_max, y_max = self.obtain_tile_coordinates(specific_tile_coordinates[0]+1, specific_tile_coordinates[1]+1)

            #  2    3
            #
            #  1    4
            a1, b1 = self.transforming_function(x_min, y_min)
            a2, b2 = self.transforming_function(x_min, y_max)
            a3, b3 = self.transforming_function(x_max, y_max)
            a4, b4 = self.transforming_function(x_max, y_min)

            specific_tile.points = [a1, b1, a2, b2, a3, b3, a4, b4]

    def Update_vertical_lines(self):
        # -1 0 1 2
        starting_index = -int(self.Num_vertical_lines/2)+1
        for i in range(starting_index, starting_index+self.Num_vertical_lines):
            single_line_x = self.from_index_obtain_line_x(i)

            a1, b1 = self.transforming_function(single_line_x, 0)
            a2, b2 = self.transforming_function(single_line_x, self.height)
            self.List_of_VLines[i].points = [a1, b1, a2, b2]

    def init_Horizontal_Lines(self):
        with self.canvas:
            Color(0, 0, 0,0)
            for i in range(0, self.Num_horizontal_lines):
                self.List_of_HLines.append(Line())

    def Update_horizontal_lines(self):
        starting_index = -int(self.Num_vertical_lines / 2) + 1
        ending_index = starting_index+self.Num_vertical_lines-1

        x_min = self.from_index_obtain_line_x(starting_index)
        x_max = self.from_index_obtain_line_x(ending_index)
        for i in range(0, self.Num_horizontal_lines):
            single_line_y = self.from_index_obtain_line_y(i)
            a1, b1 = self.transforming_function(x_min, single_line_y)
            a2, b2 = self.transforming_function(x_max, single_line_y)
            self.List_of_HLines[i].points = [a1, b1, a2, b2]

    def Update(self, dt):
        # print("dt: " + str(dt*60))
        time_factor = dt*60
        self.Update_vertical_lines()
        self.Update_horizontal_lines()
        self.Update_tiles()
        self.Update_rocket()
        self.Update_score_bag()
        # self.score=self.present_yloop
        # print(self.present_yloop)
        self.Update_speed_per_score()

        if not self.Game_Over_Boolean and self.state_game_has_started:
            
            screen_dependent_y_speed = self.speed_of_track * self.height / 100
            self.present_offest_y += screen_dependent_y_speed * time_factor

            screen_dependent_spacing_y = self.Space_horizontal_lines * self.height
            if self.present_offest_y >= screen_dependent_spacing_y:
                self.present_offest_y -= screen_dependent_spacing_y
                self.present_yloop += 1
                self.score_counter = "SCORE: " + str(self.present_yloop)
                self.produce_tiles_coordinates()
                #print("loop : " + str(self.present_yloop))

            screen_dependent_x_speed = self.present_speed_x * self.width / 100
            self.present_offset_x += screen_dependent_x_speed * time_factor

        if not self.check_rocket_collision() and not self.Game_Over_Boolean:
            self.Game_Over_Boolean = True
            self.options_title = "G A M E  O V E R\n\n   R E S T A R T"
            self.options_button_title_easy = "EASY"
            self.options_button_title_medium = "MEDIUM"
            self.options_button_title_hard = "HARD"
            self.options_widget.opacity = 1
            self.sound_music1.stop()
            self.sound_gameover_impact.play()
            Clock.schedule_once(self.play_game_over_voice_sound, 3)
    def Update_score_bag(self):
        if self.Game_Over_Boolean:
            self.score_bag.append(self.present_yloop)
    
    def Update_speed_per_score(self):
        if self.present_yloop % self.speed_increment_per_score == 0 and self.present_yloop!=0 :
            self.speed_of_track += self.speed_increment
            
    def play_game_over_voice_sound(self, dt):
        if self.Game_Over_Boolean:
            self.sound_gameover_voice.play()
    
    #def on_menu_button_pressed(self):


    def on_options_button_easy_pressed(self):
        if self.Game_Over_Boolean:
            self.sound_restart.play()
            
        else:
            self.sound_begin.play()
        self.sound_music1.play()
        self.state_game_has_started = True
        self.speed_of_track = 0.4
        #print(self.present_yloop)
        self.Update_speed_per_score()
        self.speed_X = 2.0
        #print(self.speed_of_track)
        self.options_widget.opacity = 0
        self.Restart_Game()
        
        
    def on_options_button_medium_pressed(self):
        if self.Game_Over_Boolean:
            self.sound_restart.play()
            
        else:
            self.sound_begin.play()
        self.sound_music1.play()
        self.state_game_has_started = True
        self.speed_of_track = 0.6
        self.Update_speed_per_score()
        self.speed_X = 2.0
        self.options_widget.opacity = 0
        self.Restart_Game()
    def on_options_button_hard_pressed(self):
        if self.Game_Over_Boolean:
            self.sound_restart.play()
            
        else:
            self.sound_begin.play()
        self.sound_music1.loop
        self.sound_music1.play()
        self.state_game_has_started = True
        self.speed_of_track = 0.9
        self.Update_speed_per_score()
        self.speed_X = 2.0
        self.options_widget.opacity = 0
        self.Restart_Game()


class Mission_MoonApp(App):
    pass


Mission_MoonApp().run()
     
