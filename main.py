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

        #print("foo1")

        for i in range(len(self.Cells_coordinates), self.len_visible_cells):
            r = random.randint(0, 2)
            # 0 -> straight
            # 1 -> right
            # 2 -> left
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

        #print("foo2")

    def init_Vertical_Lines(self):
        # Initialize vertical lines
        with self.canvas:
            Color(0, 0, 0,0)
            #self.line = Line(points=[100, 0, 100, 100])
            for i in range(0, self.Num_vertical_lines):
                self.List_of_VLines.append(Line())

    def init_Horizontal_Lines(self):
        # Initialize horizontal lines
        with self.canvas:
            Color(0, 0, 0,0)
            for i in range(0, self.Num_horizontal_lines):
                self.List_of_HLines.append(Line())

    def from_index_obtain_line_x(self, index):
        mid_line_x = int(self.width/2)  ######
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
        # self.Update_path_color()
        # Update cell positions
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
        # print("dt: " + str(dt*60))
        time_factor = dt*60
        self.Update_vertical_lines()
        self.Update_horizontal_lines()
        self.Update_cells()
        self.Update_rocket()
        self.Update_score_bag()
        # self.score=self.present_yloop
        # print(self.present_yloop)
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
                #print("loop : " + str(self.present_yloop))

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
    
    #def on_menu_button_pressed(self):


    def on_options_button_easy_pressed(self):
        if self.Game_Over_Boolean:
            self.restart_voice.play()
            
        else:
            self.begin_voice.play()
        self.playing_music.play()
        self.Restart_Game()
        self.state_game_has_started = True
        self.speed_of_track = 0.4
        #print(self.present_yloop)
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
