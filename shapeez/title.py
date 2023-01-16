from func import *
from game import GameScreen
from bullet import BulletScreen
import pygame, sys, math, os

# title screen can make the the player quit the game without pressing the red x
class TitleScreen(StateClass):
    def __init__(self, screen_size, stack):
        super().__init__(screen_size, stack)
        self.key_select = True
        self.selected_index = 0

        # buttons
        self.start_button = TextButton('Start game.', (255,255,255), (225,225,225))
        self.start_button.rect.center = (self.screen_size[0]/2, self.screen_size[1]/3)
        self.quit_button = TextButton('Quit game.', (255,255,255), (225,225,225))
        self.quit_button.rect.center = (self.screen_size[0]/2, self.screen_size[1]/3*2)

    def event(self, event):
        if self.start_button.cliked_once(event):
            SelectScreen(self.screen_size, self.stack).enter_state()
        if self.quit_button.cliked_once(event):
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEMOTION:
            self.key_select = False

        if event.type == pygame.KEYDOWN:
            # select options using keys
            if event.key == pygame.K_UP or event.key == pygame.K_DOWN:
                if self.key_select:
                    if event.key == pygame.K_UP:
                        self.selected_index -= 1
                        if self.selected_index < 0:
                            self.selected_index = 0
                    if event.key == pygame.K_DOWN:
                        self.selected_index += 1
                        if self.selected_index > 1:
                            self.selected_index = 1

                self.key_select = True

            # enter to press options
            if event.key == pygame.K_RETURN:
                if self.selected_index == 0:
                    SelectScreen(self.screen_size, self.stack).enter_state()
                if self.selected_index == 1:
                    pygame.quit()
                    sys.exit()

    def draw(self, window):
        window.fill((0,255,0))
        self.start_button.draw(window)
        self.quit_button.draw(window)

        if self.key_select:
            if self.selected_index == 0:
                self.start_button.draw_higlighted(window)
            elif self.selected_index == 1:
                self.quit_button.draw_higlighted(window)
        else:
            # mouse higlight
            if self.start_button.hover():
                self.start_button.draw_higlighted(window)
            if self.quit_button.hover():
                self.quit_button.draw_higlighted(window)

    def resize(self, screen_size):
        self.screen_size = screen_size
        self.start_button.rect.center = (self.screen_size[0]/2, self.screen_size[1]/3)
        self.quit_button.rect.center = (self.screen_size[0]/2, self.screen_size[1]/3*2)



# select screen used to select games (can be used to test diffrent types of games)
class SelectScreen(StateClass):
    def __init__(self, screen_size, stack):
        super().__init__(screen_size, stack)
        self.current_choice = 0

        # game text bounce
        self.text_sine = 0.0

        # images
        image_size = 200
        self.images = {}
        dir = 'images/game_select'
        for file in os.listdir(dir):
            if file[-3:] == 'png':
                self.images[file[:-4]] = pygame.image.load(dir + '/' + file).convert()

        self.choises = ({'image': self.get_textures('nothing'), 'game': GameScreen, 'text': 'Nothing'}, 
                        {'image': self.get_textures('bullet_hell'), 'game': BulletScreen, 'text': 'Bullet hell'}, 
                        {'image': self.get_textures('there is no image'), 'game': None, 'text': '???'})
        # gray out image
        self.dark_image = pygame.Surface((image_size, image_size))
        self.dark_image.fill((0,0,0))
        self.dark_image.set_alpha(150)

        self.change_choise()

    def get_textures(self, texture_name):
        if texture_name not in self.images:
            return self.images['place_holder']
        else:
            return self.images[texture_name]

    def event(self, event):
        if event.type == pygame.KEYDOWN:
            # changes the game selected
            if event.key == pygame.K_LEFT:
                self.change_choise(-1)
            if event.key == pygame.K_RIGHT:
                self.change_choise(1)

            # selects the game
            if event.key == pygame.K_RETURN:
                if self.choises[self.current_choice]['game'] != None:
                    self.choises[self.current_choice]['game'](self.screen_size, self.stack).enter_state()
            
            # return to title screen
            if event.key == pygame.K_ESCAPE:
                self.exit_state()

    def loop(self):
        self.text_sine += 0.05
        if self.text_sine > math.tau:
            self.text_sine = 0

    def draw(self, window):
        window.fill((0,255,0))
        half_screen_x = self.screen_size[0] / 2
        half_screen_y = self.screen_size[1] / 2

        # draws image
        left_image = self.choises[self.loop_list_index(self.current_choice - 1, len(self.choises))]['image']
        image = self.choises[self.current_choice]['image']
        right_image = self.choises[self.loop_list_index(self.current_choice + 1, len(self.choises))]['image']

        # side game image
        window.blit(left_image, (half_screen_x - image.get_width(), half_screen_y - image.get_height() / 2))
        window.blit(right_image, (half_screen_x, half_screen_y - image.get_height() / 2))
        # draws dark image
        window.blit(self.dark_image, (half_screen_x - image.get_width(), half_screen_y - image.get_height() / 2))
        window.blit(self.dark_image, (half_screen_x, half_screen_y - image.get_height() / 2))

        # main game image
        window.blit(image, (half_screen_x - image.get_width() / 2, half_screen_y - image.get_height() / 2))

        window.blit(self.text_image, (self.screen_size[0] / 2 - self.text_image.get_width() / 2, self.screen_size[1] / 6 + math.sin(self.text_sine) * 10))

    def change_choise(self, change=0): # put a bool to change self.current_choice + 1 or - 1 (can pass None to not change self.current_choise)
        self.current_choice = self.loop_list_index(self.current_choice + change, len(self.choises))
        self.text_image = pygame.font.SysFont(None, 60).render(self.choises[self.current_choice]['text'], True, (255,255,255)).convert_alpha()

    def loop_list_index(self, list_index, len_list) -> int:
        if list_index < 0:
            list_index = len_list - 1
        elif list_index > len_list - 1:
            list_index = 0
        return list_index