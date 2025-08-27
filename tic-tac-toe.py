import random
import pygame
import math
import time

pygame.init()

SCREEN_WIDTH, SCREEN_HEIGHT = 445, 670  # screen size
default_pole = ['' for _ in range(9)]

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

tic_tac_toe_icon = pygame.image.load('images_and_sounds/tic-tac-toe.ico').convert_alpha()  # icon
metal_circle_image = pygame.image.load('images_and_sounds/metal_circle.png').convert_alpha()  # level regulator
hint_bulb_image = pygame.image.load('images_and_sounds/hint_bulb.png').convert_alpha()  # hint light bulb
two_people_image = pygame.image.load('images_and_sounds/2_people.png').convert_alpha()  # two person
take_back_image = pygame.image.load('images_and_sounds/arrow_back.png').convert_alpha()  # take back arrow

move_sound = pygame.mixer.Sound('images_and_sounds/move.mp3')  # sound of human move
game_ends_sound = pygame.mixer.Sound('images_and_sounds/game_ends.mp3')  # sound when game will stop or start
hint_sound = pygame.mixer.Sound('images_and_sounds/hint.mp3')  # sound when computer helps you
other_buttons_sound = pygame.mixer.Sound('images_and_sounds/other_buttons.mp3')  # sound of other switches

# Изменение размера изображения
metal_circle_image = pygame.transform.scale(metal_circle_image, tuple((i // 2 for i in metal_circle_image.get_size())))

pygame.display.set_icon(tic_tac_toe_icon)
pygame.display.set_caption('Tic-Tac-Toe')  # name of the game
app_is_opened = True

level_font = pygame.font.SysFont('TimesNewRoman', 16)
evaluation_font = pygame.font.SysFont('TimesNewRoman', 20)
notation_font = pygame.font.SysFont('TimesNewRoman', 25)
analyze_font = pygame.font.SysFont('TimesNewRoman', 30)
game_result_font = pygame.font.SysFont('TimesNewRoman', 50)

x_coord_for_level_names = [79, 176, 289, 374]

LIGHT_YELLOW = (255, 255, 127)
LIGHT_GRAY = (191, 191, 191)
DARK_GREEN = (0, 95, 0)
LIGHT_RED = (255, 159, 159)
LIGHT_BLUE = (159, 159, 255)
LIGHT_GREEN = (159, 255, 159)

level_bar_possible_colors = ('green', 'yellow', 'orange', 'red')
level_names_to_blit = (level_font.render('easy', 1, level_bar_possible_colors[0]),
                       level_font.render('normal', 1, level_bar_possible_colors[1]),
                       level_font.render('hard', 1, level_bar_possible_colors[2]),
                       level_font.render('impossible', 1, level_bar_possible_colors[3]))

FPS = 60
clock = pygame.time.Clock()


class PositionObj:
    def __init__(self, position, prev=None):
        self.position = position.copy()
        self.prev = prev.copy() if type(prev) is list else prev


class Analysis:
    def __init__(self):
        self.game_history = []
        self.analyzed_game_history = []
        self.stack_link = default_pole.copy()

    def add(self, position_evaluation):
        if not settings.analysis_on:
            self.game_history.append(pole_evaluation.position.copy())
            self.analyzed_game_history.append(position_evaluation)
            self.stack_link = self.game_history[-1].copy()
        else:
            self.stack_link = PositionObj(pole_evaluation.position, self.stack_link)

    def pop(self):
        if self.game_history and settings.analysis_on and type(self.stack_link) == PositionObj and self.stack_link.position in self.game_history:
            self.stack_link = self.game_history[self.game_history.index(self.stack_link.position)].copy()
        if self.game_history and not settings.analysis_on:
            self.game_history.pop(-1)
            self.analyzed_game_history.pop(-1)
            self.stack_link = self.game_history[-1].copy() if self.game_history else default_pole.copy()
        elif type(self.stack_link) == PositionObj:
            self.stack_link = self.stack_link.prev
        elif self.stack_link not in self.game_history or self.stack_link == default_pole.copy() or type(self.stack_link) != PositionObj and self.game_history.index(self.stack_link) == 0:
            self.stack_link = default_pole.copy()
        elif type(self.stack_link) != PositionObj and self.game_history.index(self.stack_link) > 0:
            self.stack_link = self.game_history[self.game_history.index(self.stack_link) - 1].copy()
        else:
            self.stack_link = default_pole.copy()
            
            
    def change_link(self):
        self.stack_link = self.game_history[-1].copy() if self.game_history else default_pole.copy()
    

    def analyze_current_position(self):
        try:
            if not settings.analysis_on:
                return
        except NameError:
            return
        possible_position = (self.stack_link.copy() if type(self.stack_link) != PositionObj else self.stack_link.position.copy())
        stack_link_list = [possible_position.copy()]
        move_indexes = [None]
        while pole_evaluation.evaluate_pole_if_game_ended(possible_position) is None:
            try:
                good_index = random.choice(pole_evaluation.get_right_move_indexes('impossible', possible_position))
                possible_position[good_index] = ('o', 'x')[possible_position.count('') % 2 == 1]
                move_indexes.append(good_index)
                stack_link_list.append(possible_position.copy())
            except IndexError:
                break
        return stack_link_list, move_indexes

    def analyze_game(self):
        position_eval_for_comfortable_drawing = []
        for position_eval_to_human in self.analyzed_game_history:
            for letter in position_eval_to_human:
                if letter.isdigit():
                    abs_eval = 6 - int(letter)
                    break
            else:
                abs_eval = 6  # when x or o wins abs level is maximum

            if '=' in position_eval_to_human:
                position_eval_for_comfortable_drawing.append(0)
            elif 'x' in position_eval_to_human:
                position_eval_for_comfortable_drawing.append(abs_eval)
            else:
                position_eval_for_comfortable_drawing.append(-abs_eval)

        return position_eval_for_comfortable_drawing

    def get_analysis_info(self):
        return self.analyze_game(), self.game_history.copy()


analysis = Analysis()


class PoleEvaluation:
    def __init__(self):
        self.position = default_pole.copy()  # creates information about game position
        analysis.__init__()
        
        
    def get_indexes_if_game_ended(self, position=None):
        if position is None:
            position = self.position
        if type(position) is PositionObj:
            position = position.position
        res_indexes = set()

        for index in (0, 1, 2):
            if '' != position[index] == position[index + 3] == position[index + 6]:
                [res_indexes.add(i) for i in (index, index + 3, index + 6)]

        for index in (0, 3, 6):
            if '' != position[index] == position[index + 1] == position[index + 2]:
                [res_indexes.add(i) for i in (index, index + 1, index + 2)]

        for index in (2, 4):
            if '' != position[4 - index] == position[4] == position[4 + index]:
                [res_indexes.add(i) for i in (4 - index, 4, 4 + index)]
                
        if position.count('') == 0 and not res_indexes:
            return list(range(9))
        
        return list(res_indexes)
        

    def evaluate_pole_if_game_ended(self, position=None):
        if position is None:
            position = self.position
        if type(position) is PositionObj:
            position = position.position
        empty_fields = position.count('')
        evals = {'x': 10, 'o': -10}

        for index in (0, 1, 2):
            if '' != position[index] == position[index + 3] == position[index + 6]:
                return evals[position[index]]

        for index in (0, 3, 6):
            if '' != position[index] == position[index + 1] == position[index + 2]:
                return evals[position[index]]

        for index in (2, 4):
            if '' != position[4 - index] == position[4] == position[4 + index]:
                return evals[position[4]]

        if empty_fields == 0:
            return 0

        return None

    # minimax algorithm
    def evaluate_position(self, position, min_or_max, max_depth, depth=0):
        game_result = self.evaluate_pole_if_game_ended(position)
        if game_result == 0 or depth >= max_depth:
            return 0
        if game_result == 10:
            return 512
        if game_result == -10:
            return -512

        field_value = 'x' if min_or_max == 'max' else 'o'
        next_min_or_max = 'min' if min_or_max == 'max' else 'max'
        all_possible_moves = []

        for index in range(9):
            if position[index] != '':
                continue

            position[index] = field_value
            all_possible_moves.append(self.evaluate_position(position, next_min_or_max, max_depth, depth + 1))
            position[index] = ''

        return max(all_possible_moves) / 2 if min_or_max == 'max' else min(all_possible_moves) / 2
    
    
    def get_right_human_like_indexes(self, position, field_value):
        empty_poles = [i for i in range(9) if position[i] == '']
        good_indexes = set()
        for indx1 in empty_poles:
            for indx2 in empty_poles:
                if indx1 == indx2:
                    continue
                position[indx1] = field_value
                position[indx2] = field_value
                if self.evaluate_pole_if_game_ended(position) in (-10, 10):
                    good_indexes.add(indx1)
                    good_indexes.add(indx2)
                position[indx1] = ''
                position[indx2] = ''
        return good_indexes
    

    def get_right_move_indexes(self, level, position=None):
        if position is None:
            position = self.position.copy()
        max_depth_from_level = {'easy': 0, 'normal': 2, 'hard': 4, 'impossible': 10}
        good_indexes, next_position_from_index = list(), dict()

        if self.evaluate_pole_if_game_ended(position) is not None:
            return []

        if position.count('') == 9:
            good_indexes = range(9)
            return good_indexes

        field_value, non_min_or_max, min_or_max = ('x', 'min', 'max') if position.count('') % 2 == 1 else ('o', 'max', 'min')
        not_field_value = 'x' if field_value == 'o' else 'o'
        
        human_like = self.get_right_human_like_indexes(position, field_value) if position.count('') in (3, 4, 5) else set()  # humanizing engine
        
        if level != 'easy':
            # humanizing engine
            for possible_value in (field_value, not_field_value):
                for index in range(9):
                    if position[index] != '':
                        continue
                    position[index] = possible_value
                    if self.evaluate_pole_if_game_ended(position) in (-10, 10):
                        good_indexes.append(index)
                    position[index] = ''
                if good_indexes:
                    break
            intersected_good_indexes = list(human_like & set(good_indexes))
            if self.evaluate_position(position, min_or_max, max_depth=max_depth_from_level[level] - 1) == 0 and intersected_good_indexes:
                return intersected_good_indexes
            if good_indexes:
                return good_indexes
            
        for index in range(9):
            if position[index] != '':
                continue
            position[index] = ('o', 'x')[position.count('') % 2 == 1]
            next_position_from_index[index] = self.evaluate_position(position, non_min_or_max, max_depth=max_depth_from_level[level] - 1)
            position[index] = ''

        if non_min_or_max == 'min':
            extreme_value = max(next_position_from_index.values())
        else:
            extreme_value = min(next_position_from_index.values())

        for key in next_position_from_index:
            if next_position_from_index[key] == extreme_value:
                good_indexes.append(key)
        intersected_good_indexes = list(human_like & set(good_indexes))
        if level in ('hard', 'impossible') and self.evaluate_position(position, min_or_max, max_depth=max_depth_from_level[level] - 1) == 0 and intersected_good_indexes:
            return intersected_good_indexes
        if good_indexes:
            return good_indexes


pole_evaluation = PoleEvaluation()


class Engine:
    def __init__(self):
        self.__level = 'easy'

    @property
    def level(self):
        return self.__level

    @level.setter
    def level(self, value):
        if value not in ('easy', 'normal', 'hard', 'impossible'):
            raise ValueError('Incorrect value of level!')
        self.__level = value

    def move(self):
        if pole_evaluation.evaluate_pole_if_game_ended() is not None or settings.analysis_on:
            return
        if ('x', 'o')[pole_evaluation.position.count('') % 2 == 1] != settings.play_as:
            return
        if pole_evaluation.position.count('') == 9:
            pole_evaluation.position[random.choice([1, 3, 5, 7] + 2 * [0, 2, 6, 8] + 4 * [4])] = 'x'
        else:
            move_symbol = 'x' if pole_evaluation.position.count('') % 2 == 1 else 'o'
            try:
                pole_evaluation.position[random.choice(pole_evaluation.get_right_move_indexes(self.level))] = move_symbol
            except IndexError:
                pass
            if pole_evaluation.evaluate_pole_if_game_ended() is not None:
                game_ends_sound.play()
        picture.evaluation, picture.evaluation_color, picture.pointer = picture.get_position_evaluation_to_human_eyes()
        analysis.add(picture.evaluation)
        settings.get_analysis_of_current_position()


engine = Engine()


class PoleButton:
    def __init__(self, row, column, color):
        self.rect = (row * 140 + 5, column * 140 + 5, 138, 138)
        self.color = color
        self.row, self.column = row, column

    def draw(self, light):
        pygame.draw.rect(screen, color='white' if light else self.color, rect=self.rect, border_radius=2)  # draws button


class TicTacToePole:
    def __init__(self):
        self.__font = pygame.font.SysFont('TimesNewRoman', 140)
        try:
            self.__pole = [PoleButton(col, row, color=settings.default_color) for row in range(3) for col in range(3)]
        except NameError:
            self.__pole = [PoleButton(col, row, color=LIGHT_YELLOW) for row in range(3) for col in range(3)]

    def draw(self):
        detect_res_indexes = pole_evaluation.get_indexes_if_game_ended(analysis.stack_link)
        [button.draw(detect_res_indexes is not None and index in detect_res_indexes) for index, button in enumerate(self.__pole)]  # draws game field
        for index in range(9):
            color = 'red' if pole_evaluation.position[index] == 'x' else 'blue'
            text = self.__font.render(pole_evaluation.position[index], 1, color)
            screen.blit(text, (self.__pole[index].rect[0] + 35, self.__pole[index].rect[1] - 25))

    def hint(self, light_up=True):
        for index in range(9):
            self.__pole[index].color = settings.default_color
        if not light_up:
            return
        right_move_indexes = pole_evaluation.get_right_move_indexes('impossible')
        for index in range(9):
            if index in right_move_indexes:
                self.__pole[index].color = (LIGHT_RED, LIGHT_BLUE)[pole_evaluation.position.count('') % 2 == 0]

    def check_if_there_is_a_move(self):
        move_symbol = 'x' if pole_evaluation.position.count('') % 2 == 1 else 'o'
        mouse_coordinates = pygame.mouse.get_pos()

        if pole_evaluation.evaluate_pole_if_game_ended() is not None or settings.play_as not in (move_symbol, '2h'):
            return
        flag_add_picture_evaluation = False
        for pole_button in self.__pole:
            if not pygame.Rect(pole_button.rect).collidepoint(mouse_coordinates):
                continue
            if pole_evaluation.position[pole_button.column * 3 + pole_button.row] == '':
                pole_evaluation.position[pole_button.column * 3 + pole_button.row] = move_symbol
                (move_sound if pole_evaluation.evaluate_pole_if_game_ended() is None else game_ends_sound).play()
                flag_add_picture_evaluation = True
        picture.evaluation, picture.evaluation_color, picture.pointer = picture.get_position_evaluation_to_human_eyes()
        if flag_add_picture_evaluation:
            analysis.add(picture.evaluation)
            settings.get_analysis_of_current_position()


tic_tac_toe_pole = TicTacToePole()  # 9 tic-tac-toe buttons


class Settings:
    def __init__(self):
        self.switcher = ['easy', 'normal', 'hard', 'impossible'].index(engine.level) + 1
        self.__rects_to_switch_level = [pygame.Rect((-63 + 105 * index, 423, 100, 44)) for index in range(1, 5)]
        self.evaluation_on = False
        self.hint_time = 0
        self.analysis_on = False
        self.play_as = '2h'
        self.default_color = LIGHT_YELLOW
        self.best_positions, self.best_moves = None, None

    @property
    def evaluation_on(self):
        return self.__evaluation_on

    @evaluation_on.setter
    def evaluation_on(self, value):
        if type(value) != bool:
            raise TypeError('type of attribute "evaluation_on" must be bool!')
        self.__evaluation_on = value

    @property
    def analysis_on(self):
        return self.__analysis_on

    @analysis_on.setter
    def analysis_on(self, value):
        if type(value) != bool:
            raise TypeError('type of attribute "analysis_on" must be bool!')
        self.__analysis_on = value
        self.default_color = (LIGHT_YELLOW, LIGHT_GRAY)[self.__analysis_on]
        tic_tac_toe_pole.__init__()
        if not self.analysis_on:
            if analysis.game_history:
                pole_evaluation.position = analysis.game_history[-1].copy()
            else:
                pole_evaluation.__init__()

    @property
    def play_as(self):
        return self.__play_as

    @play_as.setter
    def play_as(self, value):
        # 2h means 2 humans play with each other
        if value not in ('x', 'o', '2h'):
            raise TypeError('private play_as attribute value must be "x" or "o" or "2h"!')
        if not self.analysis_on or value == '2h':
            self.__play_as = value

    def __check_if_level_switch_is_changed(self, mouse_pos):
        for level_index, level_rect in enumerate(self.__rects_to_switch_level):
            if not level_rect.collidepoint(mouse_pos) or (mouse_pos[0] - (429 + 5)) ** 2 + (mouse_pos[1] - (4 + 35 * 12 + 2 + 5)) ** 2 <= 11 ** 2:
                continue

            new_engine_level = ('easy', 'normal', 'hard', 'impossible')[level_index]
            if engine.level != new_engine_level:
                other_buttons_sound.play()
                engine.level = new_engine_level

            self.switcher = ['easy', 'normal', 'hard', 'impossible'].index(engine.level) + 1

    def __check_if_play_as_switch_is_changed(self, mouse_pos):
        new_play_as = self.play_as
        if pygame.Rect((10, 475, 50, 50)).collidepoint(mouse_pos):
            new_play_as = '2h'
        if pygame.Rect((62, 475, 50, 50)).collidepoint(mouse_pos):
            new_play_as = 'x'
        if pygame.Rect((114, 475, 50, 50)).collidepoint(mouse_pos):
            new_play_as = 'o'

        if new_play_as != self.play_as:
            other_buttons_sound.play()
            self.play_as = new_play_as

    def __check_if_evaluation_switch_is_changed(self, mouse_pos):
        if (mouse_pos[0] - (429 + 5)) ** 2 + (mouse_pos[1] - (4 + 35 * 12 + 2 + 5)) ** 2 <= 11 ** 2:
            self.evaluation_on = not self.evaluation_on
            other_buttons_sound.play()

    def __get_analysis_info_if_analyze_button_clicked(self, mouse_coordinates):
        if pygame.Rect((10, 595, 185, 50)).collidepoint(mouse_coordinates):
            self.analysis_on = not self.analysis_on
            other_buttons_sound.play()
            analysis.change_link()
            if self.analysis_on:
                self.play_as = '2h'
                self.get_analysis_of_current_position()
                

    def __take_back_if_cancel_button_clicked(self, mouse_pos):
        if not pygame.Rect((10, 535, 185, 50)).collidepoint(mouse_pos):
            return
        other_buttons_sound.play()
        analysis.pop()
        if self.play_as == 'x' and pole_evaluation.position.count('') % 2 == 1:
            analysis.pop()
        elif self.play_as == 'o' and pole_evaluation.position.count('') % 2 == 0:
            analysis.pop()
        if type(analysis.stack_link) == PositionObj:
            pole_evaluation.position = analysis.stack_link.position.copy()
        else:
            pole_evaluation.position = analysis.stack_link.copy()
        if self.analysis_on:
            self.get_analysis_of_current_position()

    def get_analysis_of_current_position(self):
        analyzed_position = analysis.analyze_current_position()
        if analyzed_position is not None:
            self.best_positions, self.best_moves = analyzed_position

    @staticmethod
    def __play_game_if_start_button_clicked(mouse_pos):
        if pygame.Rect((180, 475, 120, 50)).collidepoint(mouse_pos):
            game_ends_sound.play()
            pole_evaluation.__init__()
            settings.get_analysis_of_current_position()

    def __light_correct_squares_if_hint_button_clicked(self, mouse_pos):
        if pygame.Rect((320, 475, 120, 50)).collidepoint(mouse_pos):
            tic_tac_toe_pole.hint()
            hint_sound.play()
            self.hint_time = time.time()

    def __check_if_new_position_is_chosen(self, mouse_pos):
        if not self.analysis_on:
            return
        position_coordinates, game_positions = picture.draw_analysis()
        index = 0
        for x_coord, y_coord in position_coordinates:
            if pygame.Rect((x_coord - 10, 590 - 6 * 8 - 5, 10 * 2, 12 * 8 + 10)).collidepoint(mouse_pos):
                other_buttons_sound.play()
                pole_evaluation.position = game_positions[index].copy()
                analysis.stack_link = pole_evaluation.position.copy()
                if type(analysis.stack_link) == PositionObj:
                    pole_evaluation.position = analysis.stack_link.position.copy()
                else:
                    pole_evaluation.position = analysis.stack_link.copy()
                self.get_analysis_of_current_position()
            index += 1

    def get_analysis_of_engine_line_position(self, mouse_pos):
        if not self.analysis_on:
            return

        x_coord = 5

        for index in range(len(settings.best_moves)):
            x_coord += 40

            if not pygame.Rect(x_coord - 8, 645, 40, 23).collidepoint(mouse_pos):
                continue

            other_buttons_sound.play()

            while type(analysis.stack_link) == PositionObj:
                analysis.pop()

            for position_on_computer_line in self.best_positions[:index + 1]:
                pole_evaluation.position = position_on_computer_line.copy()
                analysis.add(position_evaluation=None)

    def check_if_any_switch_is_changed(self):
        mouse_coordinates = pygame.mouse.get_pos()

        # setting buttons
        self.__play_game_if_start_button_clicked(mouse_coordinates)
        self.__take_back_if_cancel_button_clicked(mouse_coordinates)
        self.__light_correct_squares_if_hint_button_clicked(mouse_coordinates)
        self.__get_analysis_info_if_analyze_button_clicked(mouse_coordinates)

        # setting switches
        self.__check_if_play_as_switch_is_changed(mouse_coordinates)
        self.__check_if_level_switch_is_changed(mouse_coordinates)
        self.__check_if_evaluation_switch_is_changed(mouse_coordinates)

        # analyze_positions
        self.__check_if_new_position_is_chosen(mouse_coordinates)
        self.get_analysis_of_engine_line_position(mouse_coordinates)


settings = Settings()


class Picture:
    def __init__(self):
        self.evaluation, self.evaluation_color, self.pointer = self.get_position_evaluation_to_human_eyes()

    def __call__(self, *args, **kwargs):
        screen.fill('black')

        self.draw_play_as_switches()
        self.draw_rect_bar()

        if settings.evaluation_on:
            self.draw_evaluation()

        self.draw_rest()
        self.draw_evaluation_switch()

        # must be after function draw rest
        if settings.analysis_on:
            self.draw_analysis()
            self.draw_analysis_of_current_position()

        if 1.5 > time.time() - settings.hint_time > 1:
            tic_tac_toe_pole.hint(False)

        pygame.display.update()

    @staticmethod
    def draw_analysis_of_current_position():
        x_coord, y_coord = 5, 555
        screen.blit(evaluation_font.render('best:', 1, 'yellow'), (5, 645))
        mouse_position = pygame.mouse.get_pos()

        for index, move_index in enumerate(settings.best_moves):
            x_coord += 40

            recommended_move_by_computer = evaluation_font.render(f'{('C', 'B', 'A')[2 - move_index % 3]}{4 - (move_index // 3 + 1)}' if move_index is not None else '__', 1, 'yellow')

            screen.blit(recommended_move_by_computer, (x_coord, 645))
            if index:
                screen.blit(evaluation_font.render('→', 1, 'yellow'), (x_coord - 18, 645))

            if not pygame.Rect(x_coord - 8, 645, 40, 23).collidepoint(mouse_position):
                continue
            if index > 8:
                x_coord -= 40
            
            index = index if index is not None else 0
            pygame.draw.rect(screen, 'black', rect=(x_coord - 30, y_coord + 3, 83, 83))
            detect_res_indexes = pole_evaluation.get_indexes_if_game_ended(settings.best_positions[index])
            color = 'white'
            if not detect_res_indexes and settings.best_positions[index] != default_pole.copy():
                detect_res_indexes = pole_evaluation.get_right_move_indexes('impossible', position=settings.best_positions[index])
                color = (LIGHT_BLUE, LIGHT_RED)[settings.best_positions[index].count('') % 2]
            
            for mini_row in range(3):
                for mini_column in range(3):
                    do_paint = detect_res_indexes is not None and (mini_column * 3 + mini_row) in detect_res_indexes
                    mini_x, mini_y = x_coord - 33 + 30 * mini_row, y_coord + 30 * mini_column
                    pygame.draw.rect(screen, (LIGHT_GRAY, color)[do_paint], rect=(mini_x, mini_y, 29, 29), border_radius=2)
                    symbol = settings.best_positions[index][mini_column * 3 + mini_row]
                    screen.blit(analyze_font.render(symbol, 1, ('blue', 'red')[symbol == 'x']), (mini_x + 7, mini_y - 6))

    def draw_evaluation(self):
        if self.pointer in (4, 4 + 35 * 12):
            pygame.draw.rect(screen, ('blue', 'red')[self.pointer == 4], (429, 4, 10, 35 * 12), border_radius=10)
        else:
            pygame.draw.rect(screen, 'blue', (429, 4, 10, self.pointer - 4), border_top_left_radius=10, border_top_right_radius=10)
            pygame.draw.rect(screen, 'red', (430, self.pointer, 10, 4 + 35 * 12 - self.pointer), border_bottom_left_radius=10, border_bottom_right_radius=10)
        for line_number in range(1, 12):
            y_coord = 4 + 35 * line_number
            pygame.draw.line(screen, 'black', start_pos=(429, y_coord), end_pos=(441, y_coord), width=(1, 3)[line_number == 6])

    @staticmethod
    def draw_analysis():
        game_evals_for_drawing, game_positions = analysis.get_analysis_info()
        game_evals_for_drawing = [0] + game_evals_for_drawing
        game_positions = [default_pole.copy()] + game_positions
        coordinates_joining_lines = [(250, 590)]

        # drawing white net
        for y_coord in range(590 - 8 * 6, 590 + 8 * 7, 8):
            pygame.draw.line(screen, 'white', start_pos=(250, y_coord), end_pos=(250 + 20 * 9, y_coord), width=(1, 3)[(y_coord - 590) % 48 == 0])
        for x_coord in range(250, 250 + 200, 20):
            pygame.draw.line(screen, 'white', start_pos=(x_coord, 590 - 8 * 6), end_pos=(x_coord, 590 + 8 * 6))

        for move_number in range(10):
            screen.blit(level_font.render(str(move_number), 1, 'white'), (247 + move_number * 20, 715 - 192))

        for w in range(-6, 8, 2):
            screen.blit(level_font.render((f'{('x', 'o')[w > 0]}, W{abs(w)}', f'{('x, W', 'x = o', 'o, W')[w // 4 + 1]}')[w % 6 == 0], 1, 'white'), (210, 590 + 8 * (w - 1)))

        x_coord = 250
        for index_for_drawing in range(len(game_evals_for_drawing) - 1):
            start_y_eval, end_y_eval = game_evals_for_drawing[index_for_drawing: index_for_drawing + 2]
            start_y_coord, end_y_coord = 590 - start_y_eval * 8, 590 - end_y_eval * 8
            end_pos = (x_coord + 20, end_y_coord)
            pygame.draw.line(screen, (LIGHT_BLUE, LIGHT_RED)[index_for_drawing % 2 == 0], start_pos=(x_coord, start_y_coord), end_pos=end_pos, width=5)
            coordinates_joining_lines.append(end_pos)
            x_coord += 20

        for position_index, coord_between_lines in enumerate(coordinates_joining_lines):
            x_coord, y_coord = coord_between_lines[0], 546
            if not pygame.Rect((x_coord - 10, 590 - 6 * 8 - 5, 10 * 2, 12 * 8 + 10)).collidepoint(pygame.mouse.get_pos()):
                continue
            pygame.draw.rect(screen, 'black', rect=(x_coord - 97, y_coord + 3, 83, 83))
            detect_res_indexes = pole_evaluation.get_indexes_if_game_ended(game_positions[position_index])
            for mini_row in range(3):
                for mini_column in range(3):
                    do_paint = detect_res_indexes is not None and (mini_column * 3 + mini_row) in detect_res_indexes
                    mini_x, mini_y = x_coord - 100 + 30 * mini_row, y_coord + 30 * mini_column
                    pygame.draw.rect(screen, (LIGHT_GRAY, 'white')[do_paint], rect=(mini_x, mini_y, 29, 29), border_radius=2)
                    symbol = game_positions[position_index][mini_column * 3 + mini_row]
                    screen.blit(analyze_font.render(symbol, 1, ('blue', 'red')[symbol == 'x']), (mini_x + 7, mini_y - 6))

        return coordinates_joining_lines, game_positions

    @staticmethod
    def draw_rect_bar():
        level_bar_color = level_bar_possible_colors[settings.switcher - 1]
        level_bar_rect = (7, 440, -17 + 105 * settings.switcher, 10)

        pygame.draw.rect(screen, color=level_bar_color, rect=level_bar_rect, border_radius=10)
        for x_coord in range(-13 + 105, -13 + 105 * 5, 105):
            pygame.draw.line(screen, color=LIGHT_GRAY, start_pos=(x_coord, 440), end_pos=(x_coord, 449), width=2)

        screen.blit(metal_circle_image, (-23 + 105 * settings.switcher, 435))
        for rendered_level, level_x_coord in zip(level_names_to_blit, x_coord_for_level_names):
            screen.blit(rendered_level, (level_x_coord, 450))

    @staticmethod
    def draw_play_as_switches():
        pygame.draw.rect(screen, color=(LIGHT_GRAY, LIGHT_GREEN)[settings.play_as == '2h'], rect=(10, 475, 50, 50))
        pygame.draw.rect(screen, color=(LIGHT_GRAY, LIGHT_RED)[settings.play_as == 'x'], rect=(62, 475, 50, 50))
        pygame.draw.rect(screen, color=(LIGHT_GRAY, LIGHT_BLUE)[settings.play_as == 'o'], rect=(114, 475, 50, 50))

        screen.blit(two_people_image, (11, 477))
        screen.blit(game_result_font.render('x', 1, 'red'), (75, 467))
        screen.blit(game_result_font.render('o', 1, 'blue'), (127, 467))

    def draw_evaluation_switch(self):
        pygame.draw.circle(screen, (LIGHT_GRAY, 'white')[settings.evaluation_on], center=(429 + 5, 4 + 35 * 12 + 2 + 5), radius=5)
        mouse_pos = pygame.mouse.get_pos()
        if pygame.Rect((419, 4, 30, 35 * 12)).collidepoint(mouse_pos) and settings.evaluation_on:
            font = evaluation_font.render(self.evaluation if settings.evaluation_on else 'off', 1, self.evaluation_color if settings.evaluation_on else 'black')
            pygame.draw.rect(screen, (LIGHT_GRAY, 'white')[settings.evaluation_on], (429 - 10 - font.get_rect()[2], mouse_pos[1] - 10 - 2, font.get_rect()[2] + 5, font.get_rect()[3] + 4))
            screen.blit(font, (429 - font.get_rect()[2] - 8, mouse_pos[1] - 10))

    @staticmethod
    def draw_rest():
        # drawing tic-tac-toe pole
        tic_tac_toe_pole.draw()
        for row in range(3):
            for column in range(3):
                screen.blit(notation_font.render(f'{('C', 'B', 'A')[2 - row]}{4 - (column + 1)}', 1, DARK_GREEN), (10 + row * 140, 112 + column * 140))

        pygame.draw.rect(screen, color=LIGHT_GRAY, rect=(180, 475, 120, 50))  # start button rect
        screen.blit(game_result_font.render('Start!', 1, 'white'), (185, 470))

        pygame.draw.rect(screen, color=LIGHT_GRAY, rect=(320, 475, 120, 50))  # hint button rect
        screen.blit(game_result_font.render('hint', 1, 'white'), (325, 470))
        screen.blit(hint_bulb_image, (395, 475))

        pygame.draw.rect(screen, color=LIGHT_GRAY, rect=(10, 535, 185, 50))  # cancel button rect
        screen.blit(game_result_font.render('cancel', 1, DARK_GREEN), (15, 530))
        screen.blit(take_back_image, (140, 535))

        pygame.draw.rect(screen, color=(LIGHT_RED, LIGHT_GREEN)[settings.analysis_on], rect=(10, 595, 185, 50))  # analyze button rect
        screen.blit(analyze_font.render('analyze game', 1, 'black'), (20, 600))

    @staticmethod
    def get_position_evaluation_to_human_eyes():
        if pole_evaluation.position.count('') == 9:
            return 'x = o', DARK_GREEN, 4 + 35 * 6
        min_or_max = 'max' if pole_evaluation.position.count('') % 2 == 1 else 'min'
        position_eval = pole_evaluation.evaluate_position(pole_evaluation.position, min_or_max, max_depth=10)
        if position_eval == 0 or abs(position_eval) == 512:
            abs_of_position_eval_to_human = ''
        else:
            abs_of_position_eval_to_human = int(math.log(512 // abs(position_eval), 2))

        if position_eval == 0:
            return 'x = o', DARK_GREEN, 4 + 35 * 6
        elif position_eval > 0:
            if abs_of_position_eval_to_human == '':
                return f'x, W{abs_of_position_eval_to_human}', 'red', 4
            return f'x, W{abs_of_position_eval_to_human}', 'red', 4 + 35 * abs_of_position_eval_to_human
        else:
            if abs_of_position_eval_to_human == '':
                return f'o, W{abs_of_position_eval_to_human}', 'blue', 4 + 35 * 12
            return f'o, W{abs_of_position_eval_to_human}', 'blue', 4 + 35 * 12 - 35 * abs_of_position_eval_to_human


picture = Picture()

while app_is_opened:
    picture()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            app_is_opened = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            settings.check_if_any_switch_is_changed()
            tic_tac_toe_pole.check_if_there_is_a_move()
            engine.move()
    clock.tick(FPS)
