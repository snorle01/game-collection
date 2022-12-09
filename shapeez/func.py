import pygame

class StateClass: # parent state class
    def __init__(self, screen_size, stack):
        self.screen_size = screen_size
        self.stack = stack
        self.prev_state = None

    def enter_state(self):
        if len(self.stack) > 1:
            self.prev_state = self.stack[-1]
        self.stack.append(self)

    def exit_state(self):
        self.stack.pop()

    def go_to_first(self):
        while len(self.stack) > 1:
            self.stack.pop()

    # default events
    def loop(self):
        pass

    def event(self, event):
        pass

    def draw(self, window):
        window.fill((255,0,255))
        window.blit(pygame.font.SysFont(None, 60).render('ERROR', True, (0,0,0)), (0,0))

# pause screen pauses the game and has the options to unpause or to go back to title
class PausesCreen(StateClass):
    def __init__(self, screen_size, stack):
        super().__init__(screen_size, stack)

        self.gray_screen = pygame.Surface(self.screen_size)
        self.gray_screen.fill((100,100,100))
        self.gray_screen.set_alpha(200)

        self.unpause_button = TextButton('Go back to game.', color=(255,255,255))
        self.unpause_button.rect.center = (self.screen_size[0]/2, self.screen_size[1]/3)
        self.title_button = TextButton('To title.', color=(255,255,255))
        self.title_button.rect.center = (self.screen_size[0]/2, self.screen_size[1]/3*2)

    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.exit_state()
        if self.unpause_button.cliked_once(event):
            self.exit_state()
        if self.title_button.cliked_once(event):
            self.go_to_first()
        

    def draw(self, window):
        self.prev_state.draw(window)
        window.blit(self.gray_screen, (0,0))
        self.unpause_button.draw(window)
        self.title_button.draw(window)
                
class ButtonClass: # parent button class
    def cliked_once(self, event) -> bool:
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0] and event.type == pygame.MOUSEBUTTONDOWN

    def cliked_multiple(self) -> bool:
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouse_pos) and pygame.mouse.get_pressed()[0]

class TextButton(ButtonClass):
    def __init__(self, text, color=(0,0,0)):
        super().__init__()
        self.text_image = pygame.font.SysFont(None, 60).render(text, True, color)
        self.rect = self.text_image.get_rect()

    def draw(self, window):
        window.blit(self.text_image, self.rect)

class ImageButton(ButtonClass):
    def __init__(self, image, pos=(0,0)):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def draw(self, window):
        window.blit(self.image, self.rect)