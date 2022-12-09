import pygame, sys, math

class TunnelBack:
    def __init__(self, screen_size, tunnel_lenght, speed):
        wall_image = pygame.image.load('images/raycast/rock_wall.png')
        self.wall_image = pygame.transform.scale(wall_image, (256, 256))
        wall_image_blur = pygame.image.load('images/raycast/rock_wall_blur.png')
        self.wall_image_blur = pygame.transform.scale(wall_image_blur, (256, 256))

        floor_image = pygame.image.load('images/raycast/floor.png')
        self.floor_image = pygame.transform.scale(floor_image, (256, 256))
        floor_image_blur = pygame.image.load('images/raycast/floor_blur.png')
        self.floor_image_blur = pygame.transform.scale(floor_image_blur, (256, 256))

        self.shadow = pygame.Surface(screen_size)
        self.shadow.fill((0,0,0))

        self.FOV = math.pi / 3
        self.HALF_FOV = self.FOV / 2
        self.MAX_DEPTH = 20
        self.TEXTURE_SIZE = 256
        self.HALF_TEXTURE_SIZE = self.TEXTURE_SIZE // 2
        self.player_angle = math.pi/2*3

        # screen X
        self.SCREEN_DIST_x = (screen_size[0]//2) / math.tan(self.HALF_FOV)
        self.NUM_RAYS_x = screen_size[0] // 2
        self.SCALE_x = screen_size[0] // self.NUM_RAYS_x                    
        self.HALF_NUM_RAYS_x = self.NUM_RAYS_x // 2                         
        self.DELTA_ANGLE_x = self.FOV / self.NUM_RAYS_x

        # screen Y
        self.SCREEN_DIST_y = (screen_size[1]//2) / math.tan(self.HALF_FOV)
        self.NUM_RAYS_y = screen_size[1] // 2 
        self.SCALE_y = screen_size[1] // self.NUM_RAYS_y                           
        self.HALF_NUM_RAYS_y = self.NUM_RAYS_y // 2                         
        self.DELTA_ANGLE_y = self.FOV / self.NUM_RAYS_y                        

        self.speed = speed
        self.screen_size = screen_size
        self.map, self.player_pos = self.get_tunel_and_player_pos(tunnel_lenght)
        self.rays_horisontal = self.get_rays_horisontal(self.player_pos, tunnel_lenght)
        self.rays_vertical = self.get_rays_vertical(self.player_pos, tunnel_lenght)
        self.texture_offset = 0

    def get_tunel_and_player_pos(self, lenght) -> tuple:
        map_raw = []
        for i in range(lenght):
            map_raw.append([1,0,1])

        player_pos = (1.5, len(map_raw) + 0.5)

        map = {}
        for y, row in enumerate(map_raw):
            for x, value in enumerate(row):
                if value:
                    map[(x,y)] = value
        return map, player_pos

    def get_rays_horisontal(self, player_pos, map_lenght) -> tuple:
        ray_angle = self.player_angle - self.HALF_FOV + 0.0001
        ox, oy = player_pos[0], player_pos[1]
        x_map, y_map = int(ox), int(oy)
        rays = []
        for ray in range(self.NUM_RAYS_x):
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)

            # horisontal
            y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)

            depth_hor = (y_hor - oy) / sin_a
            x_hor = ox + depth_hor * cos_a

            delta_depth = dy / sin_a
            dx = delta_depth * cos_a

            for i in range(map_lenght):
                tile_hor = int(x_hor), int(y_hor)
                if tile_hor in self.map:
                    break
                x_hor += dx
                y_hor += dy
                depth_hor += delta_depth

            # vertical
            x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

            depth_vert = (x_vert - ox) / cos_a
            y_vert = oy + depth_vert * sin_a

            delta_depth = dx / cos_a
            dy = delta_depth * sin_a

            for i in range(map_lenght):
                tile_vert = int(x_vert), int(y_vert)
                if tile_vert in self.map:
                    break
                x_vert += dx
                y_vert += dy
                depth_vert += delta_depth

            # depth offset
            if depth_vert < depth_hor:
                depth = depth_vert
                y_vert %= 1
                offset = y_vert if cos_a > 0 else (1 - y_vert)
            else:
                depth = depth_hor
                x_hor %= 1
                offset = (1 - x_hor) if sin_a > 0 else x_hor

            # remove fishbowl effect
            depth *= math.cos(self.player_angle - ray_angle)

            # projection
            proj_height = self.SCREEN_DIST_x / (depth + 0.0001)

            # draw walls
            if proj_height < self.screen_size[1]:
                wall_pos = (ray * self.SCALE_x, (self.screen_size[1]//2) - proj_height // 2)
            else:
                wall_pos = (ray * self.SCALE_x, 0)

            rays.append((offset, proj_height, wall_pos, depth))

            ray_angle += self.DELTA_ANGLE_x
        return rays

    def get_rays_vertical(self, player_pos, map_lenght):
        ray_angle = self.player_angle - self.HALF_FOV + 0.0001
        ox, oy = player_pos[0], player_pos[1]
        x_map, y_map = int(ox), int(oy)
        rays = []
        for ray in range(self.NUM_RAYS_y):
            sin_a = math.sin(ray_angle)
            cos_a = math.cos(ray_angle)

            # horisontal
            y_hor, dy = (y_map + 1, 1) if sin_a > 0 else (y_map - 1e-6, -1)

            depth_hor = (y_hor - oy) / sin_a
            x_hor = ox + depth_hor * cos_a

            delta_depth = dy / sin_a
            dx = delta_depth * cos_a

            for i in range(map_lenght):
                tile_hor = int(x_hor), int(y_hor)
                if tile_hor in self.map:
                    break
                x_hor += dx
                y_hor += dy
                depth_hor += delta_depth

            # vertical
            x_vert, dx = (x_map + 1, 1) if cos_a > 0 else (x_map - 1e-6, -1)

            depth_vert = (x_vert - ox) / cos_a
            y_vert = oy + depth_vert * sin_a

            delta_depth = dx / cos_a
            dy = delta_depth * sin_a

            for i in range(100):
                tile_vert = int(x_vert), int(y_vert)
                if tile_vert in self.map:
                    break
                x_vert += dx
                y_vert += dy
                depth_vert += delta_depth

            # depth offset
            if depth_vert < depth_hor:
                depth = depth_vert
                y_vert %= 1
                offset = y_vert if cos_a > 0 else (1 - y_vert)
            else:
                depth = depth_hor
                x_hor %= 1
                offset = (1 - x_hor) if sin_a > 0 else x_hor

            # remove fishbowl effect
            depth *= math.cos(self.player_angle - ray_angle) * 0.8

            # projection
            proj_height = self.SCREEN_DIST_y / (depth + 0.0001)

            # draw walls
            if proj_height < self.screen_size[0]:
                wall_pos = ((self.screen_size[0]//2) - proj_height // 2, ray * self.SCALE_y)
            else:
                wall_pos = (0, ray * self.SCALE_y)

            rays.append((offset, proj_height, wall_pos, depth))

            ray_angle += self.DELTA_ANGLE_y

        return rays

    def draw(self, window):
        # draws horisontal walls
        for index, ray in enumerate(self.rays_horisontal):
            if ray[3] > 5: # blur if depth is more then 5
                image = self.wall_image_blur
            else:
                image = self.wall_image

            if index < len(self.rays_horisontal)/2: # left side of screen
                # texture scroll
                x_pos = ray[0] * (self.TEXTURE_SIZE - self.SCALE_x) + self.texture_offset
                if x_pos > 255:
                    x_pos -= 255
            else: # right side of screen
                # texture scroll
                x_pos = ray[0] * (self.TEXTURE_SIZE - self.SCALE_x) - self.texture_offset
                if x_pos < 0:
                    x_pos += 255

            if ray[1] < self.screen_size[1]:
                wall_column = image.subsurface(x_pos, 0, self.SCALE_x, self.TEXTURE_SIZE)
                wall_column = pygame.transform.scale(wall_column, (self.SCALE_x, ray[1]))
            else:
                texture_height = self.TEXTURE_SIZE * self.screen_size[1] / ray[1]
                wall_column = image.subsurface(x_pos, self.HALF_TEXTURE_SIZE - texture_height // 2, self.SCALE_x, texture_height)
                wall_column = pygame.transform.scale(wall_column, (self.SCALE_x, self.screen_size[1]))

            window.blit(wall_column, ray[2])

        # draws vertical walls (the floor and ceiling)
        for index, ray in enumerate(self.rays_vertical):
            if ray[3] > 5: # blur if depth is more then 5
                blur = True
            else:
                blur = False

            if index < len(self.rays_vertical)/2: # left side of screen
                # texture scroll
                y_pos = ray[0] * (self.TEXTURE_SIZE - self.SCALE_y) + self.texture_offset
                if y_pos > 255:
                    y_pos -= 255
                if blur:
                    true_image = self.wall_image_blur
                else:
                    true_image = self.wall_image
            else: # right side of screen
                # texture scroll
                y_pos = ray[0] * (self.TEXTURE_SIZE - self.SCALE_y) - self.texture_offset
                if y_pos < 0:
                    y_pos += 255
                if blur:
                    true_image = self.floor_image_blur
                else:
                    true_image = self.floor_image

            if ray[1] < self.screen_size[0]:
                wall_column = true_image.subsurface(0, y_pos, self.TEXTURE_SIZE, self.SCALE_y)
                wall_column = pygame.transform.scale(wall_column, (ray[1], self.SCALE_y))
            else:
                # code below is broken
                print('tun')
                texture_height = self.TEXTURE_SIZE * self.screen_size[1] / ray[1]
                print(self.HALF_TEXTURE_SIZE - texture_height // 2, y_pos, texture_height, self.SCALE_y)
                # wall_column = image.subsurface(x_pos, self.HALF_TEXTURE_SIZE - texture_height // 2, self.SCALE_x, texture_height)
                wall_column = true_image.subsurface(self.HALF_TEXTURE_SIZE - texture_height // 2, y_pos, texture_height, self.SCALE_y)
                wall_column = pygame.transform.scale(wall_column, (self.screen_size[1], self.SCALE_x))

            window.blit(wall_column, ray[2])

        self.texture_offset += self.speed
        if self.texture_offset > 255:
            self.texture_offset = 0


if __name__ == '__main__':
    screen_size = (700, 500)
    background = TunnelBack(screen_size, 500, 10)
    game_display = pygame.display.set_mode(screen_size)
    clock = pygame.time.Clock()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        pygame.display.set_caption(str(int(clock.get_fps())))

        background.draw(game_display)

        clock.tick(0)    
        pygame.display.update()