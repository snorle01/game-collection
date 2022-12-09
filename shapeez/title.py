from func import *
from game import GameScreen
from bullet import BulletScreen
import pygame, sys

# title screen can make the the player quit the game without pressing the red x
class TitleScreen(StateClass):
    def __init__(self, screen_size, stack):
        super().__init__(screen_size, stack)

        # buttons
        self.start_button = TextButton('Start game.', color=(255,255,255))
        self.start_button.rect.center = (self.screen_size[0]/2, self.screen_size[1]/3)
        self.quit_button = TextButton('Quit game.', color=(255,255,255))
        self.quit_button.rect.center = (self.screen_size[0]/2, self.screen_size[1]/3*2)

    def event(self, event):
        if self.start_button.cliked_once(event):
            SelectScreen(self.screen_size, self.stack).enter_state()
        if self.quit_button.cliked_once(event):
            pygame.quit()
            sys.exit()

    def draw(self, window):
        window.fill((0,255,0))
        self.start_button.draw(window)
        self.quit_button.draw(window)

# select screen used to select games (can be used to test diffrent types of games)
class SelectScreen(StateClass):
    def __init__(self, screen_size, stack):
        super().__init__(screen_size, stack)
        self.current_choice = 0
        self.change_choise()

        # images
        image_0 = pygame.image.load('images/game_select/game_1.png').convert()
        image_1 = pygame.image.load('images/game_select/game_2.png').convert()
        image_2 = pygame.image.load('images/game_select/game_3.png').convert()
        self.dark_image = pygame.Surface((image_0.get_width(), image_0.get_height()))
        self.dark_image.fill((0,0,0))
        self.dark_image.set_alpha(150)
        self.image_choise = [image_0, image_1, image_2]

    def event(self, event):
        if event.type == pygame.KEYDOWN:
            # changes the game selected
            if event.key == pygame.K_LEFT:
                self.change_choise(False)
            if event.key == pygame.K_RIGHT:
                self.change_choise(True)

            # selects the game
            if event.key == pygame.K_RETURN:
                if self.current_choice == 0:
                    GameScreen(self.screen_size, self.stack).enter_state()
                elif self.current_choice == 1:
                    BulletScreen(self.screen_size, self.stack).enter_state()
            
            if event.key == pygame.K_ESCAPE:
                self.exit_state()

    def draw(self, window):
        window.fill((0,255,0))

        # draws image
        image = self.image_choise[self.current_choice]
        if self.current_choice == 0:
            left_image = self.image_choise[2]
            right_image = self.image_choise[1]
        elif self.current_choice == 1:
            left_image = self.image_choise[0]
            right_image = self.image_choise[2]
        elif self.current_choice == 2:
            left_image = self.image_choise[1]
            right_image = self.image_choise[0]

        window.blit(left_image, (self.screen_size[0]/2-image.get_width(), self.screen_size[1]/2-image.get_height()/2))
        window.blit(right_image, (self.screen_size[0]/2, self.screen_size[1]/2-image.get_height()/2))
        # draws dark image
        window.blit(self.dark_image, (self.screen_size[0]/2-image.get_width(), self.screen_size[1]/2-image.get_height()/2))
        window.blit(self.dark_image, (self.screen_size[0]/2, self.screen_size[1]/2-image.get_height()/2))

        # main image
        window.blit(image, (self.screen_size[0]/2-image.get_width()/2, self.screen_size[1]/2-image.get_height()/2))

        window.blit(self.text_image, (self.screen_size[0]/2-self.text_image.get_width()/2, self.screen_size[1]/6))

    def change_choise(self, change=None): # put a bool to change self.current_choice + 1 or - 1 (can pass None to not change self.current_choise)
        if change == True:
            self.current_choice += 1
            if self.current_choice > 2:
                self.current_choice = 0
        elif change == False:
            self.current_choice -= 1
            if self.current_choice < 0:
                self.current_choice = 2

        if self.current_choice == 0:
            self.text_image = pygame.font.SysFont(None, 60).render('Nothing', True, (255,255,255)).convert_alpha()
        elif self.current_choice == 1:
            self.text_image = pygame.font.SysFont(None, 60).render('Bullet hell', True, (255,255,255)).convert_alpha()
        elif self.current_choice == 2:
            self.text_image = pygame.font.SysFont(None, 60).render('???', True, (255,255,255)).convert_alpha()