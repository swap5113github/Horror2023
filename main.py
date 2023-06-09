import random
from kivy.config import Config

Config.set('graphics', 'width', '900')
Config.set('graphics', 'height', '400')

from kivy.app import App
from kivy.properties import Clock
from kivy.metrics import dp
from kivy.graphics.context_instructions import Color
from kivy.graphics.vertex_instructions import Line, Quad,Triangle,Ellipse
from kivy.properties import NumericProperty, ObjectProperty, StringProperty , ListProperty
from kivy.lang.builder import Builder
from kivy.core.audio import SoundLoader
from kivy.uix.image import Widget
from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.relativelayout import RelativeLayout
Builder.load_file("options.kv")

class MainWidget(RelativeLayout):
    # Importing functions from other files
    from user_actions import keyboard_is_closed, on_press_keyboard_up, on_press_keyboard_down, on_touching_up, on_touching_down
    from transforms import transforming_function, transforming_function_for_2D, transforming_function_for_perspective
    
    options_widget = ObjectProperty()
    vanishing_point_x = NumericProperty(0)
    vanishing_point_y = NumericProperty(0)

    Num_vertical_lines = 18
    Space_vertical_lines = .4  # percentage in screen width
    List_of_VLines = []

    Num_horizontal_lines = 25
    Space_horizontal_lines = .1  # percentage in screen height
    List_of_HLines = []

    speed_of_track = 0
    present_offest_y = 0
    present_yloop = 0
    speed_increment = 0.1/60
    speed_increment_per_score = 5

    speed_along_X = 0
    present_speed_x = 5
    present_offset_x = 0

    len_visible_cells = 16
    Cells = []
    Cells_coordinates = []

    rocket_WIDTH = .1
    rocket_HEIGHT = 0.035
    rocket_BASE_Y = 0.04
    rocket = None
    rocket_coordinates = [(0, 0), (0, 0), (0, 0),(0,0)]

    Game_Over_Boolean = False
    state_game_has_started = False
    options_title = StringProperty("M I S S I O N\n    M O O N ")

    options_button_title_easy = StringProperty("Easy")
    options_button_title_medium = StringProperty("Medium")
    options_button_title_hard = StringProperty("Hard")
    score_counter = StringProperty()
    best_score_counter = StringProperty()

    score_bag = [0]

    begin_voice = None
    mission_moon_voice=None
    mission_moon_sound = None
    gameover_impact_sound = None
    gameover_voice = None
    playing_music = None
    restart_voice = None

    def __init__(self, **kwargs):
        super(MainWidget, self).__init__(**kwargs)
        self.init_Vertical_Lines()
        self.init_Horizontal_Lines()
        self.init_Cells()
        self.init_rocket()
        self.score_counter = "SCORE: " + str(self.present_yloop)
        self.starting_cells_coordinates()
        self.produce_cells_coordinates()

        self.init_Audio_File()

        # Keyboard events
        self._keyboard = Window.request_keyboard(self.keyboard_is_closed, self)
        self._keyboard.bind(on_key_down=self.on_press_keyboard_down)
        self._keyboard.bind(on_key_up=self.on_press_keyboard_up)

        # Schedule the update function to run at 60 FPS
        Clock.schedule_interval(self.Update, 1.0 / 60.0)
        self.mission_moon_sound.play()
        self.mission_moon_voice.play()

    def init_Audio_File(self):
        # Load audio files
        self.begin_voice = SoundLoader.load("begin.wav")
        self.mission_moon_voice = SoundLoader.load("missionmoonvoice.mp3")
        self.mission_moon_sound = SoundLoader.load("transformer-hi-tech-audio-logo-digital-reveal-intro-122757.mp3")
        self.gameover_impact_sound = SoundLoader.load("gameover_impact.wav")
        self.gameover_voice = SoundLoader.load("gameover_voice.wav")
        self.playing_music = SoundLoader.load("gamemusic.mp3")
        self.restart_voice = SoundLoader.load("restart.wav")

        self.playing_music.volume = 1
        self.mission_moon_voice.volume = 1
        self.begin_voice.volume = .25
        self.mission_moon_sound.volume = .25
        self.gameover_voice.volume = .25
        self.restart_voice.volume = .25
        self.gameover_impact_sound.volume = .6
    
    def Restart_Game(self):
        # Reset game state
        self.present_offest_y = 0
        self.present_yloop = 0
        self.present_speed_x = 0
        self.present_offset_x = 0

        self.Cells_coordinates = []
        self.score_counter = "SCORE: " + str(self.present_yloop)
        self.best_score_counter = "BEST SCORE: " + str(max(self.score_bag))
        self.starting_cells_coordinates()
        self.produce_cells_coordinates()

        self.Game_Over_Boolean = False
    
    def init_rocket(self):
        color = (random.random(),random.random(), random.random())
        with self.canvas:
            Color(*color)
            self.rocket = Quad()

    def Update_rocket(self):
        center_x = self.width / 2
        base_y = self.rocket_BASE_Y * self.height
        rocket_half_width = self.rocket_WIDTH * self.width / 2
        rocket_height = self.rocket_HEIGHT * self.height
        #  2   3
        #  1   4
        # self.transforming_function
        self.rocket_coordinates[0] = (center_x-rocket_half_width, base_y)
        self.rocket_coordinates[1] = (center_x-rocket_half_width, base_y + rocket_height)
        self.rocket_coordinates[2] = (center_x + rocket_half_width, base_y+rocket_height)
        self.rocket_coordinates[3] = (center_x + rocket_half_width, base_y)

        a1, b1 = self.transforming_function(*self.rocket_coordinates[0])
        a2, b2 = self.transforming_function(*self.rocket_coordinates[1])
        a3, b3 = self.transforming_function(*self.rocket_coordinates[2])
        a4, b4 = self.transforming_function(*self.rocket_coordinates[3])
        self.rocket.points = [a1, b1, a2, b2, a3, b3, a4, b4]

    def check_rocket_collision(self):
        for i in range(0, len(self.Cells_coordinates)):
            cell_x, cell_y = self.Cells_coordinates[i]
            if cell_y > self.present_yloop + 1:
                return False
            if self.check_rocket_collision_with_cell(cell_x, cell_y):
                return True
        return False

    def check_rocket_collision_with_cell(self, cell_x, cell_y):
        x_min, y_min = self.obtain_cell_coordinates(cell_x, cell_y)
        x_max, y_max = self.obtain_cell_coordinates(cell_x + 1, cell_y + 1)
        rocket_center_x=(self.rocket_coordinates[3][0]+self.rocket_coordinates[0][0])/2
        rocket_center_y=(self.rocket_coordinates[0][1]+self.rocket_coordinates[1][1])/2
    
        if x_min <= rocket_center_x <= x_max and y_min <= rocket_center_y <= y_max:
            return True
    
        return False

    def init_Cells(self):
        with self.canvas:
            Color(0,0,0,0.9)
            for i in range(0, self.len_visible_cells):
                self.Cells.append(Quad())
