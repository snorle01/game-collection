from func import *
import pygame, sys, math
pygame.init()

def dist_between(pos1, pos2):
    lenght_x = pos1[0] - pos2[0]
    lenght_y = pos1[1] - pos2[1]
    return math.sqrt(lenght_x*lenght_x + lenght_y*lenght_y)

class PopupButton(ButtonClass):
    def __init__(self, text, return_word, size=30, color=(0,0,0), bg_color=(255,255,255)):
        super().__init__()
        self.text_image = pygame.font.SysFont(None, size).render(text, True, color, bg_color)
        self.rect = self.text_image.get_rect()
        self.return_word = return_word

    def draw(self, window):
        window.blit(self.text_image, self.rect)

class ObjectClass:
    def __init__(self, pos, image, size):
        self.static_image = image
        self.image = pygame.transform.scale(self.static_image, (size,size))
        self.x = pos[0]
        self.y = pos[1]
        self.popup_pos = (0,0)
        self.buttons = [PopupButton('Delete', 'delete')]

    def set_pos(self, new_pos):
        self.x = new_pos[0]
        self.y = new_pos[1]

    def get_pos(self):
        return self.x, self.y

    def resize(self, new_size):
        self.image = pygame.transform.scale(self.static_image, (new_size, new_size))

    def open_popup(self, world_mouse_pos):
        self.popup_pos = world_mouse_pos

    def popup_handling(self, event, list):
        if self.delete_button.cliked_once(event):
            list.remove(self)

class ImageObject(ObjectClass):
    def __init__(self, pos, image, size):
        super().__init__(pos, image, size)
        self.buttons.append(PopupButton('Change image', 'change image'))

class PosObject(ObjectClass):
    def __init__(self, pos, size):
        image = pygame.font.SysFont(None, 100).render(f'{pos[0]}.{pos[1]}', True, (0,0,0), (255,255,255))
        super().__init__(pos, image, size)



class GameScreen(StateClass):
    def __init__(self, screen_size, stack):
        super().__init__(screen_size, stack)
        # images
        self.rock_image = pygame.image.load('images/rock.png').convert_alpha()
        self.metal_ball_image = pygame.image.load('images/metal_ball.png').convert_alpha()

        self.offset_x = 0
        self.offset_y = 0
        self.scale = 50
        self.start_pan_pos = (0,0)
        self.selected_object = None
        self.popup_object = None
        self.objects = []

    def event(self, event):
        # mouse
        if event.type == pygame.MOUSEBUTTONDOWN:
            # pan
            if pygame.mouse.get_pressed()[2]:
                self.start_pan_pos = pygame.mouse.get_pos()

            # mouse click
            elif pygame.mouse.get_pressed()[0]:
                cliked_popup = False

                # check if cliked button in popup
                if self.popup_object != None:
                    for button in self.popup_object.buttons:
                        if button.cliked_once(event):
                            # list of popup return words that runs commands that changes the object
                            if button.return_word == 'delete':
                                self.objects.remove(self.popup_object)
                                self.popup_object = None
                            if button.return_word == 'change image':
                                if self.popup_object.static_image == self.rock_image:
                                    self.popup_object.static_image = self.metal_ball_image
                                elif self.popup_object.static_image == self.metal_ball_image:
                                    self.popup_object.static_image = self.rock_image
                                self.popup_object.resize(self.scale)
                            
                            self.popup_object = None
                            cliked_popup = True
                            break

                # if popup buttons not pressed
                if cliked_popup == False:
                    self.popup_object = None
                    pos = self.screen_to_world(pygame.mouse.get_pos(), True)
                    # check if clicked on exsisting object
                    for object in self.objects:
                        if object.get_pos() == pos:
                            self.popup_object = object
                            object.open_popup(self.screen_to_world(pygame.mouse.get_pos()))
                            break

                    else:
                        # create new object
                        if self.selected_object != None:
                            if self.selected_object == 'rock':
                                self.objects.append(ImageObject(pos, self.rock_image, self.scale) )
                            elif self.selected_object == 'metal_ball':
                                self.objects.append(ImageObject(pos, self.metal_ball_image, self.scale) )
                            elif self.selected_object == 'pos':
                                self.objects.append(PosObject(pos, self.scale) )

        # keys
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                MenuScreen(self.screen_size, self.stack).enter_state()
                self.popup_object = None
            if event.key == pygame.K_ESCAPE:
                PausesCreen(self.screen_size, self.stack).enter_state()
                self.popup_object = None

    def loop(self):
        # pan with mouse
        if pygame.mouse.get_pressed()[2]:
            mouse_pos = pygame.mouse.get_pos()
            self.offset_x -= (mouse_pos[0] - self.start_pan_pos[0]) / self.scale
            self.offset_y -= (mouse_pos[1] - self.start_pan_pos[1]) / self.scale

            self.start_pan_pos = pygame.mouse.get_pos()

        keys = pygame.key.get_pressed()

        # zoom
        if keys[pygame.K_PLUS] or keys[pygame.K_MINUS]:
            before_zoom = self.screen_to_world(pygame.mouse.get_pos())
            if keys[pygame.K_PLUS]:
                self.scale *= 1.1
                self.scale *= 1.1
            if keys[pygame.K_MINUS]:
                self.scale *= 0.901
                self.scale *= 0.901
            after_zoom = self.screen_to_world(pygame.mouse.get_pos())

            self.offset_x += (before_zoom[0] - after_zoom[0])
            self.offset_y += (before_zoom[1] - after_zoom[1])

            for object in self.objects:
                object.resize(self.scale)

                

    def draw(self, window):
        window.fill((255,255,255))

        # infinete grid
        num_lines_x = int(self.screen_size[0] // self.scale)
        num_lines_y = int(self.screen_size[1] // self.scale)
        start_x, start_y = self.screen_to_world((0,0))
        end_x, end_y = self.screen_to_world(self.screen_size)
        # x
        for i in range(num_lines_x + 1):
            pygame.draw.line(window, (200,200,200), self.world_to_screen((int(start_x) + i, start_y)), self.world_to_screen((int(start_x) + i, end_y)) )
        # y
        for i in range(num_lines_y + 1):
            pygame.draw.line(window, (200,200,200), self.world_to_screen((start_x, int(start_y) + i)), self.world_to_screen((end_x, int(start_y) + i)) )

        # draw center lines
        pygame.draw.line(window, (200,200,200), self.world_to_screen((start_x, 0)), self.world_to_screen((end_x, 0)), 3) # x
        pygame.draw.line(window, (200,200,200), self.world_to_screen((0, start_y)), self.world_to_screen((0, end_y)), 3) # y

        # objects
        for object in self.objects:
            window.blit(object.image, self.world_to_screen(object.get_pos()))

        # popup object
        if self.popup_object != None:
            for index, button in enumerate(self.popup_object.buttons):
                x_pos, y_pos = self.world_to_screen(self.popup_object.popup_pos)
                if index > 0:
                    y_pos += (self.popup_object.buttons[index - 1].text_image.get_height() * index)
                button.rect.topleft = (x_pos, y_pos)
                button.draw(window)

    def world_to_screen(self, world_pos, turn_to_int=False) -> tuple[int, int]:
        screen_x = (world_pos[0] - self.offset_x) * self.scale
        screen_y = (world_pos[1] - self.offset_y) * self.scale
        if turn_to_int:
            if screen_x < 0:
                screen_x = int(screen_x) - 1
            else:
                screen_x = int(screen_x)
            if screen_y < 0:
                screen_y = int(screen_y) - 1
            else:
                screen_y = int(screen_y)
        return screen_x, screen_y

    def screen_to_world(self, screen_pos, turn_to_int=False) -> tuple[int, int]:
        world_x = screen_pos[0] / self.scale + self.offset_x
        world_y = screen_pos[1] / self.scale + self.offset_y
        if turn_to_int:
            if world_x < 0:
                world_x = int(world_x) - 1
            else:
                world_x = int(world_x)
            if world_y < 0:
                world_y = int(world_y) - 1
            else:
                world_y = int(world_y)
        return world_x, world_y



# menu screen where you can select items
class MenuScreen(StateClass):
    def __init__(self, screen_size, stack):
        super().__init__(screen_size, stack)
        self.gray_screen = pygame.Surface(self.screen_size)
        self.gray_screen.fill((100,100,100))
        self.gray_screen.set_alpha(200)

        # image
        rock_image = pygame.image.load('images/rock.png').convert_alpha()
        self.rock_image = pygame.transform.scale(rock_image, (50,50))
        metal_ball_image = pygame.image.load('images/metal_ball.png').convert_alpha()
        self.metal_ball_image = pygame.transform.scale(metal_ball_image, (50,50))

        pos_image = pygame.font.SysFont(None, 60).render('0.0', True, (0,0,0), (255,255,255))
        self.pos_image = pygame.transform.scale(pos_image, (50,50))

        self.object0_button = ImageButton(self.rock_image, (5, screen_size[1] - 55))
        self.object1_button = ImageButton(self.pos_image, (60, screen_size[1] - 55))

        # popup buttons
        self.show_popup = False
        self.popup0_button = ImageButton(self.rock_image, (5, screen_size[1] - 105))
        self.popup1_button = ImageButton(self.metal_ball_image, (5, screen_size[1] - 155))

    def event(self, event):
        # clicked rock button
        if self.object0_button.cliked_once(event):
            self.show_popup = not self.show_popup
        # clicked pos button
        elif self.object1_button.cliked_once(event):
            if self.prev_state.selected_object == 'pos':
                self.prev_state.selected_object = None
            else:
                self.prev_state.selected_object = 'pos'

        # popup
        if self.show_popup:
            if self.popup0_button.cliked_once(event):
                if self.prev_state.selected_object == 'rock':
                    self.prev_state.selected_object = None
                else:
                    self.prev_state.selected_object = 'rock'
            if self.popup1_button.cliked_once(event):
                if self.prev_state.selected_object == 'metal_ball':
                    self.prev_state.selected_object = None
                else:
                    self.prev_state.selected_object = 'metal_ball'

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                self.exit_state()

    def draw(self, window):
        self.prev_state.draw(window)
        window.blit(self.gray_screen, (0,0))

        # buttons
        self.object0_button.draw(window)
        if self.prev_state.selected_object == 'rock' or self.prev_state.selected_object == 'metal_ball':
            self.object0_button.draw_higlighted(window)
        self.object1_button.draw(window)
        if self.prev_state.selected_object == 'pos':
            self.object1_button.draw_higlighted(window)

        # popup
        if self.show_popup:
            self.popup0_button.draw(window)
            if self.prev_state.selected_object == 'rock':
                self.popup0_button.draw_higlighted(window)
            self.popup1_button.draw(window)
            if self.prev_state.selected_object == 'metal_ball':
                self.popup1_button.draw_higlighted(window)

    def resize(self, screen_size):
        self.screen_size = screen_size
        self.prev_state.resize(screen_size)
        # gray screen
        self.gray_screen = pygame.Surface(self.screen_size)
        self.gray_screen.fill((100,100,100))
        self.gray_screen.set_alpha(200)
        # buttons
        self.object0_button = ImageButton(self.rock_image, (5, screen_size[1] - 55))
        self.object1_button = ImageButton(self.pos_image, (60, screen_size[1] - 55))



# if this file is run only run the game
if __name__ == '__main__':
    pygame.init()

    screen_size = (700, 500)
    game_display = pygame.display.set_mode(screen_size)
    state_stack = []
    GameScreen(screen_size, state_stack).enter_state()
    clock = pygame.time.Clock()

    while True:
        pygame.display.set_caption(str(int(clock.get_fps())))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            state_stack[-1].event(event)

        state_stack[-1].loop()

        state_stack[-1].draw(game_display)
        pygame.display.update()

        clock.tick(60)