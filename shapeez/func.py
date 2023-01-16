import pygame

class StateClass: # parent state class
    def __init__(self, screen_size, stack):
        self.screen_size = screen_size
        self.stack = stack
        self.prev_state = None

    def enter_state(self):
        if len(self.stack) > 0:
            self.prev_state = self.stack[-1]
        self.stack.append(self)

    def exit_state(self):
        self.prev_state.resize(self.screen_size)
        self.stack.pop()

    def go_to_first(self):
        while len(self.stack) > 1:
            self.stack.pop()

    def loop(self):
        pass

    def event(self, event):
        pass

    def draw(self, window):
        window.fill((255,0,255))
        window.blit(pygame.font.SysFont(None, 60).render('ERROR', True, (0,0,0)), (0,0))

    def resize(self, screen_size):
        self.screen_size = screen_size

# pause screen pauses the game and has the options to unpause or to go back to title
class PausesCreen(StateClass):
    def __init__(self, screen_size, stack):
        super().__init__(screen_size, stack)
        self.selected_index = 0
        self.key_select = False

        self.gray_screen = pygame.Surface(self.screen_size)
        self.gray_screen.fill((100,100,100))
        self.gray_screen.set_alpha(200)

        self.unpause_button = TextButton('Go back to game.', (255,255,255), (225,225,225))
        self.unpause_button.rect.center = (self.screen_size[0]/2, self.screen_size[1]/3)
        self.title_button = TextButton('To title.', (255,255,255), (225,225,225))
        self.title_button.rect.center = (self.screen_size[0]/2, self.screen_size[1]/3*2)

    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.exit_state()

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

            if self.key_select and event.key == pygame.K_RETURN:
                if self.selected_index == 0:
                    self.exit_state()
                if self.selected_index == 1:
                    self.go_to_first()

        if self.unpause_button.cliked_once(event):
            self.exit_state()
        if self.title_button.cliked_once(event):
            self.go_to_first()

        if event.type == pygame.MOUSEMOTION:
            self.key_select = False

    def draw(self, window):
        self.prev_state.draw(window)
        window.blit(self.gray_screen, (0,0))

        self.unpause_button.draw(window)
        self.title_button.draw(window)

        if self.key_select:
            if self.selected_index == 0:
                self.unpause_button.draw_higlighted(window)
            elif self.selected_index == 1:
                self.title_button.draw_higlighted(window)
        else:
            if self.unpause_button.hover():
                self.unpause_button.draw_higlighted(window)
            elif self.title_button.hover():
                self.title_button.draw_higlighted(window)

    def resize(self, screen_size):
        self.screen_size = screen_size
        self.prev_state.resize(screen_size)
        # gray screen
        self.gray_screen = pygame.Surface(self.screen_size)
        self.gray_screen.fill((100,100,100))
        self.gray_screen.set_alpha(200)
        # buttons
        self.unpause_button.rect.center = (self.screen_size[0]/2, self.screen_size[1]/3)
        self.title_button.rect.center = (self.screen_size[0]/2, self.screen_size[1]/3*2)
                
class ButtonClass: # parent button class
    def hover(self) -> bool:
        mouse_pos = pygame.mouse.get_pos()
        return self.rect.collidepoint(mouse_pos)

    def cliked_once(self, event) -> bool:
        return self.hover() and pygame.mouse.get_pressed()[0] and event.type == pygame.MOUSEBUTTONDOWN

    def cliked_multiple(self) -> bool:
        return self.hover() and pygame.mouse.get_pressed()[0]

    def draw_higlighted(self, window):
        pygame.draw.rect(window, (255,255,255), self.rect, 3)

class TextButton(ButtonClass):
    def __init__(self, text, color=(0,0,0), highlight_color=(0,0,0), size=60):
        super().__init__()
        self.text = text
        self.size = size
        self.text_image = pygame.font.SysFont(None, self.size).render(self.text, True, color)
        self.higlighted_image = pygame.font.SysFont(None, self.size).render(self.text, True, highlight_color)
        self.rect = self.text_image.get_rect()

    def change_color(self, new_color):
        self.text_image = pygame.font.SysFont(None, self.size).render(self.text, True, new_color)

    def draw(self, window):
        window.blit(self.text_image, self.rect)

    def draw_higlighted(self, window):
        window.blit(self.higlighted_image, self.rect)

class ImageButton(ButtonClass):
    def __init__(self, image, pos=(0,0)):
        super().__init__()
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = pos

    def draw(self, window):
        window.blit(self.image, self.rect)