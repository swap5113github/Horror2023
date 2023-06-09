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
                
    def starting_cells_coordinates(self):
        for i in range(0, 9):
            self.Cells_coordinates.append((0, i))

    def produce_cells_coordinates(self):
        LAST_x = 0
        LAST_y = 0

        # clean the coordinates that are out of the screen
        # cell_y < self.present_yloop
        for i in range(len(self.Cells_coordinates)-1, -1, -1):
            if self.Cells_coordinates[i][1] < self.present_yloop:
                del self.Cells_coordinates[i]

        if len(self.Cells_coordinates) > 0:
            LAST_coordinates = self.Cells_coordinates[-1]
            LAST_x = LAST_coordinates[0]
            LAST_y = LAST_coordinates[1] + 1

        for i in range(len(self.Cells_coordinates), self.len_visible_cells):
            r = random.randint(0, 2)
            # 0 -> move straight
            # 1 -> move right
            # 2 -> move left
            starting_index = -int(self.Num_vertical_lines / 2) + 1
            ending_index = starting_index + self.Num_vertical_lines - 1
            if LAST_x <= starting_index:
                r = 1
            if LAST_x >= ending_index - 1:
                r = 2

            self.Cells_coordinates.append((LAST_x, LAST_y))
            if r == 1:
                LAST_x += 1
                self.Cells_coordinates.append((LAST_x, LAST_y))
                LAST_y += 1
                self.Cells_coordinates.append((LAST_x, LAST_y))
            if r == 2:
                LAST_x -= 1
                self.Cells_coordinates.append((LAST_x, LAST_y))
                LAST_y += 1
                self.Cells_coordinates.append((LAST_x, LAST_y))

            LAST_y += 1

    def init_Vertical_Lines(self):
        # Initialize vertical lines
        with self.canvas:
            Color(0, 0, 0,0)
            for i in range(0, self.Num_vertical_lines):
                self.List_of_VLines.append(Line())

    def init_Horizontal_Lines(self):
        # Initialize horizontal lines
        with self.canvas:
            Color(0, 0, 0,0)
            for i in range(0, self.Num_horizontal_lines):
                self.List_of_HLines.append(Line())

    def from_index_obtain_line_x(self, index):
        mid_line_x = int(self.width/2)  
        screen_dependent_spacing = self.Space_vertical_lines * self.width
        ofset = index - 0.5
        single_line_x = mid_line_x + ofset*screen_dependent_spacing + self.present_offset_x
        return single_line_x

    def from_index_obtain_line_y(self, index):
        screen_dependent_spacing_y = self.Space_horizontal_lines*self.height
        single_line_y = index*screen_dependent_spacing_y-self.present_offest_y
        return single_line_y

    def obtain_cell_coordinates(self, cell_x, cell_y):
        cell_y = cell_y - self.present_yloop
        x = self.from_index_obtain_line_x(cell_x)
        y = self.from_index_obtain_line_y(cell_y)
        return x, y

    def Update_cells(self):
        for i in range(0, self.len_visible_cells):
            specific_cell = self.Cells[i]
            specific_cell_coordinates = self.Cells_coordinates[i]
            x_min, y_min = self.obtain_cell_coordinates(specific_cell_coordinates[0], specific_cell_coordinates[1])
            x_max, y_max = self.obtain_cell_coordinates(specific_cell_coordinates[0]+1, specific_cell_coordinates[1]+1)

            # 1   2     
            #
            # 4   3
            a1, b1 = self.transforming_function(x_min, y_max)
            a2, b2 = self.transforming_function(x_max, y_max)
            a3, b3 = self.transforming_function(x_max, y_min)
            a4, b4 = self.transforming_function(x_min, y_min)
            specific_cell.points = [a1, b1, a2, b2, a3, b3, a4, b4]

    def Update_vertical_lines(self):
        # -1 0 1 2
        # Update vertical lines
        starting_index = -int(self.Num_vertical_lines/2)+1
        for i in range(starting_index, starting_index+self.Num_vertical_lines):
            single_line_x = self.from_index_obtain_line_x(i)
            a1, b1 = self.transforming_function(single_line_x, 0)
            a2, b2 = self.transforming_function(single_line_x, self.height)
            self.List_of_VLines[i].points = [a1, b1, a2, b2]

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
        time_factor = dt*60
        self.Update_vertical_lines()
        self.Update_horizontal_lines()
        self.Update_cells()
        self.Update_rocket()
        self.Update_score_bag()
        self.Update_speed_per_score()

        if not self.Game_Over_Boolean and self.state_game_has_started:
            screen_dependent_y_speed = self.speed_of_track * self.height / 100
            self.present_offest_y += screen_dependent_y_speed * time_factor

            screen_dependent_spacing_y = self.Space_horizontal_lines * self.height
            while self.present_offest_y >= screen_dependent_spacing_y:
                self.present_offest_y -= screen_dependent_spacing_y
                self.present_yloop += 1
                self.score_counter = "SCORE: " + str(self.present_yloop)
                self.produce_cells_coordinates()
    
            screen_dependent_x_speed = self.present_speed_x * self.width / 100
            self.present_offset_x += screen_dependent_x_speed * time_factor

        if not self.check_rocket_collision() and not self.Game_Over_Boolean:
            self.Game_Over_Boolean = True
            self.options_title = "G A M E  O V E R\n   R E S T A R T"
            self.options_button_title_easy = "EASY"
            self.options_button_title_medium = "MEDIUM"
            self.options_button_title_hard = "HARD"
            self.options_widget.opacity = 1
            self.playing_music.stop()
            self.gameover_impact_sound.play()
            Clock.schedule_once(self.play_game_over_voice_sound, 3)
    
    def Update_score_bag(self):
        if self.Game_Over_Boolean:
            self.score_bag.append(self.present_yloop)
    
    def Update_speed_per_score(self):
        if self.present_yloop % self.speed_increment_per_score == 0 and self.present_yloop!=0 :
            self.speed_of_track += self.speed_increment
            
    def play_game_over_voice_sound(self, dt):
        if self.Game_Over_Boolean:
            self.gameover_voice.play()
    
    def on_options_button_easy_pressed(self):
        if self.Game_Over_Boolean:
            self.restart_voice.play()    
        else:
            self.begin_voice.play()
        self.playing_music.play()
        self.Restart_Game()
        self.state_game_has_started = True
        self.speed_of_track = 0.4
        self.Update_speed_per_score()
        self.speed_along_X = 2.0
        self.options_widget.opacity = 0
        
    def on_options_button_medium_pressed(self):
        if self.Game_Over_Boolean:
            self.restart_voice.play()
        else:
            self.begin_voice.play()
        self.playing_music.play()
        self.Restart_Game()
        self.state_game_has_started = True
        self.speed_of_track = 0.6
        self.Update_speed_per_score()
        self.speed_along_X = 3.0
        self.options_widget.opacity = 0
        
    def on_options_button_hard_pressed(self):
        if self.Game_Over_Boolean:
            self.restart_voice.play()
        else:
            self.begin_voice.play()
        self.playing_music.loop
        self.playing_music.play()
        self.Restart_Game()
        self.state_game_has_started = True
        self.speed_of_track = 0.9
        self.Update_speed_per_score()
        self.speed_along_X = 4.0
        self.options_widget.opacity = 0
        
class Mission_MoonApp(App):
    pass

Mission_MoonApp().run()     
