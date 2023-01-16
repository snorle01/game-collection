from title import TitleScreen
import pygame, sys
pygame.init()

screen_size = (700, 500)
game_display = pygame.display.set_mode(screen_size, pygame.RESIZABLE)
clock = pygame.time.Clock()
state_stack = []

# sets the starting scene
TitleScreen(screen_size, state_stack).enter_state()

while True:
    pygame.display.set_caption(str(int(clock.get_fps())))

    for event in pygame.event.get():
        # defult events. these will happen on every screen
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.VIDEORESIZE:
            screen_size = (event.w, event.h)
            state_stack[-1].resize(screen_size)

        # state event
        state_stack[-1].event(event)

    # state loop
    state_stack[-1].loop()

    # state draw
    state_stack[-1].draw(game_display)

    pygame.display.update()
    clock.tick(60)