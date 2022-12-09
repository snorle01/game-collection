from func import *
import pygame

class ObjectClass:
    def __init__(self, pos, image):
        self.x = pos[0]
        self.y = pos[1]
        self.image = image

    def draw(self, window, cam_offset):
        pos = self.x + cam_offset[0], self.y + cam_offset[1]
        window.blit(self.image, pos)

    def get_pos(self) -> tuple[int, int]:
        return self.x, self.y

class GameScreen(StateClass):
    def __init__(self, screen_size, stack):
        super().__init__(screen_size, stack)
        image = pygame.image.load('images/test.png').convert_alpha()
        self.image = pygame.transform.scale(image, (50,50))
        self.button0 = ImageButton(image, (5, self.screen_size[1]-55))

        self.mouse_item = None
        self.objects = []

        self.camera_x = 0
        self.camera_y = 0

    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                PausesCreen(self.screen_size, self.stack).enter_state()

        if self.button0.cliked_once(event):
            if self.mouse_item == 'metal_ball':
                self.mouse_item = None
            else:
                self.mouse_item = 'metal_ball'
        
        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[0]: # left click (create objects)
            map_pos = self.get_mouse_on_map(True)
            mouse_pos = pygame.mouse.get_pos()
            if mouse_pos[1] <self.screen_size[1]-60 and self.mouse_item == 'metal_ball':
                blocked = False
                for object in self.objects:
                    if object.get_pos() == map_pos:
                        blocked = True
                        break
                if blocked == False:
                    self.objects.append(ObjectClass(map_pos, self.image))

        if event.type == pygame.MOUSEBUTTONDOWN and pygame.mouse.get_pressed()[2]: # right click (remove objects)
            map_pos = self.get_mouse_on_map(True)
            for object in self.objects:
                if object.get_pos() == map_pos:
                    self.objects.remove(object)
                    break

    def loop(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.camera_y += 3
        if keys[pygame.K_s]:
            self.camera_y -= 3
        if keys[pygame.K_a]:
            self.camera_x += 3
        if keys[pygame.K_d]:
            self.camera_x -= 3

    def draw(self, window):
        window.fill((255,255,255))

        # lines
        camera_offset_y = self.camera_y % 50
        camera_offset_x = self.camera_x % 50
        for x in range(self.screen_size[0]//50):
            pygame.draw.line(window, (200,200,200), (x*50 + camera_offset_x, 0), (x*50 + camera_offset_x, self.screen_size[1]))
        for y in range(self.screen_size[1]//50):
            pygame.draw.line(window, (200,200,200), (0, y * 50 + camera_offset_y), (self.screen_size[0], y * 50 + camera_offset_y))

        for object in self.objects:
            object.draw(window, self.get_camera_pos())

        pygame.draw.rect(window, (100,100,100), (0, self.screen_size[1]-60, self.screen_size[0], 60))
        self.button0.draw(window)

        if self.mouse_item == 'metal_ball':
            window.blit(self.image, pygame.mouse.get_pos())

    def get_camera_pos(self) -> tuple[int, int]:
        return self.camera_x, self.camera_y
    
    def get_mouse_on_map(self, by_grid=False):
        mouse_x, mouse_y = pygame.mouse.get_pos()
        mouse_x -= self.camera_x
        mouse_y -= self.camera_y
        if by_grid:
            mouse_x -= mouse_x % 50
            mouse_y -= mouse_y % 50
        return mouse_x, mouse_y


if __name__ == '__main__':
    screen_size = (700, 500)
    game_display = pygame.display.set_mode(screen_size)
    game = GameScreen(screen_size, None)
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                lol = 80 / 0 # a funny way to force close the window

            game.event(event)

        game.loop()
        game.draw(game_display)
        pygame.display.update()
        clock.tick(60)