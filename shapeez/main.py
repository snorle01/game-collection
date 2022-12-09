from title import TitleScreen
import pygame, sys
pygame.init()

screen_size = (700, 500)
game_display = pygame.display.set_mode(screen_size)
clock = pygame.time.Clock()
state_stack = []

# fade image
fade_image = pygame.Surface(screen_size)
fade_image.fill((0,0,0))
fade_opacity = 0
fade_in = False
fade_out = False

# sets the starting scene
TitleScreen(screen_size, state_stack).enter_state()

while True:
    pygame.display.set_caption(str(int(clock.get_fps())))

    for event in pygame.event.get():
        # defult events. these will happen on every screen
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # state event
        state_stack[-1].event(event)

    # state loop
    state_stack[-1].loop()

    # fade
    if fade_in:
        fade_opacity += 3
        if fade_opacity >= 255:
            fade_opacity = 255
            fade_in = False
        fade_image.set_alpha(fade_opacity)
    elif fade_out:
        fade_opacity -= 3
        if fade_opacity <= 0:
            fade_opacity = 0
            fade_out = False
        fade_image.set_alpha(fade_opacity)

    # state draw
    state_stack[-1].draw(game_display)
    if fade_in or fade_out:
        game_display.blit(fade_image, (0,0))

    pygame.display.update()
    clock.tick(60)