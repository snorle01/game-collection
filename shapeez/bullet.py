from func import *
from bullet_back import TunnelBack
import pygame, sys, math, random, spline

dir = 'images/bullet_hell/'

def dist_between(pos1, pos2):
    lenght_x = pos1[0] - pos2[0]
    lenght_y = pos1[1] - pos2[1]
    return math.sqrt(lenght_x*lenght_x + lenght_y*lenght_y)

class RectEntity:
    def __init__(self, pos, width, height):
        self.rect = pygame.Rect(pos[0], pos[1], width, height)

    def get_pos(self):
        return self.rect.topleft

    def get_center(self):
        return self.rect.center

    def set_pos(self, new_pos):
        self.rect.topleft = new_pos

    def set_center(self, new_pos):
        self.rect.center = new_pos

    def outside(self, screen_size, offset=0):
        return self.rect.right + offset < 0 or self.rect.left - offset > screen_size[1] or self.rect.bottom + offset < 0 or self.rect.top - offset > screen_size[1]

class PointEntity:
    def __init__(self, pos):
        self.x = pos[0]
        self.y = pos[1]

    def get_pos(self) -> tuple:
        return self.x, self.y

    def set_pos(self, new_pos):
        self.x = new_pos[0]
        self.y = new_pos[1]

    def outside(self, screen_size, offset=0) -> bool:
        return self.x+offset < 0 or self.x-offset > screen_size[0] or self.y+offset < 0 or self.y-offset > screen_size[1]

    def dist_to(self, target) -> float:
        lenght_x = self.x - target.x
        lenght_y = self.y - target.y
        return math.sqrt(lenght_x*lenght_x + lenght_y*lenght_y)

class PlayerClass(PointEntity):
    def __init__(self, pos):
        super().__init__(pos)
        self.hurt_timer = 0
        self.images = (pygame.image.load(dir + 'player_ship.png').convert_alpha(), 
                       pygame.image.load(dir + 'player_ship_glow.png').convert_alpha())
        self.radius = 5
        self.shift = False

        # shot
        self.bullets = []
        self.cooldown_counter = 0

        # bomb
        self.bomb_on = False
        self.bomb_pos = None
        self.bomb_radius = 0

    def draw(self, window):
        if self.hurt_timer > 0:
            window.blit(self.images[1], (self.x - self.images[1].get_width() / 2, self.y - self.images[1].get_height() / 2))
        else:
            window.blit(self.images[0], (self.x - self.images[0].get_width() / 2, self.y - self.images[0].get_height() / 2))
        # shift
        if self.shift:
            pygame.draw.circle(window, (255,0,0), self.get_pos(), self.radius)
        
        # bomb
        if self.bomb_on:
            pygame.draw.circle(window, (255,255,255), self.bomb_pos, self.bomb_radius, 3)

    def update(self):
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
        if self.cooldown_counter > 0:
            self.cooldown_counter -= 1
        if self.bomb_on:
            self.bomb_radius += 10
            if self.bomb_radius > 300:
                self.bomb_on = False
                self.bomb_radius = 0
                self.bomb_pos = None

    def move(self, screen_size):
        keys = pygame.key.get_pressed()

        # shoot
        if keys[pygame.K_z]:
            if self.cooldown_counter == 0:
                self.bullets.append(PlayerBullet(self.get_pos()))
                self.cooldown_counter = 5

        # focus
        if keys[pygame.K_LSHIFT]:
            speed = 2
            self.shift = True
        else:
            speed = 4
            self.shift = False

        # move
        if keys[pygame.K_UP]:
            self.y -= speed
            if self.y - self.images[0].get_height() / 2 < 0:
                self.y = 0 + self.images[0].get_height() / 2
        if keys[pygame.K_DOWN]:
            self.y += speed
            if self.y + self.images[0].get_height() / 2 > screen_size[1]:
                self.y = screen_size[1] - self.images[0].get_height() / 2
        if keys[pygame.K_LEFT]:
            self.x -= speed
            if self.x - self.images[0].get_width() / 2 < 0:
                self.x = 0 + self.images[0].get_width() / 2
        if keys[pygame.K_RIGHT]:
            self.x += speed
            if self.x + self.images[0].get_width() / 2 > screen_size[0]:
                self.x = screen_size[0] - self.images[0].get_width() / 2

    def event(self, event):
        if event.type == pygame.KEYDOWN:
            # bomb
            if event.key == pygame.K_x:
                self.bomb_on = True
                self.bomb_pos = self.get_pos()

class PlayerBullet(RectEntity):
    def __init__(self, pos):
        self.image = pygame.image.load(dir + 'player_bullet.png').convert_alpha()
        self.image_blur = pygame.image.load(dir + 'player_bullet_blur.png')
        super().__init__((pos[0] - self.image.get_width() / 2, pos[1] - self.image.get_height() / 2), self.image.get_width(), self.image.get_height())
        self.dying = False
        self.timer = 10

    def draw(self, window):
        if self.dying:
            window.blit(self.image_blur, self.rect)
        else:
            window.blit(self.image, self.rect)

    def move(self):
        if self.dying:
            self.rect.y -= 2
        else:
            self.rect.y -= 10

    def update(self):
        self.timer -= 1

class EnemyClass(RectEntity):
    def __init__(self, pos, walk_dir, ship_image, bullet):
        self.image = ship_image
        super().__init__(pos, self.image.get_width(), self.image.get_height())

        # shooting
        self.bullet = bullet
        self.start_shooting = False
        self.cooldown = 0

        # points
        self.spline_pos = 0.0
        self.point1 = self.get_pos()
        if walk_dir == 'right':
            self.point0 = (self.rect.x - 50, self.rect.y + random.randint(-20, 20))
            self.point2 = (self.rect.x + 50, self.rect.y + random.randint(-20, 20))
            self.point3 = (self.rect.x + 100, self.rect.y + random.randint(-20, 20))
        elif walk_dir == 'left':
            self.point0 = (self.rect.x + 50, self.rect.y + random.randint(-20, 20))
            self.point2 = (self.rect.x - 50, self.rect.y + random.randint(-20, 20))
            self.point3 = (self.rect.x - 100, self.rect.y + random.randint(-20, 20))

        self.speed = 5
        self.health = 20
        self.walk_dir = walk_dir

    def draw(self, window):
        window.blit(self.image, self.rect)
        # draw spline 
        '''pygame.draw.circle(window, (0,0,255), self.get_pos(), 5)
        pygame.draw.lines(window, (255,255,255), False, spline.make_spline(self.point0, self.point1, self.point2, self.point3))'''

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1

        self.spline_pos += 0.01
        if self.spline_pos > 1:
            self.spline_pos = 0
            self.point0 = self.point1
            self.point1 = self.point2
            self.point2 = self.point3
            if self.walk_dir == 'right':
                self.point3 = (self.rect.x + 100, self.rect.y + random.randint(-20, 20))
            elif self.walk_dir == 'left':
                self.point3 = (self.rect.x - 100, self.rect.y + random.randint(-20, 20))
        
    def move(self):
        self.set_pos(spline.point(self.point0, self.point1,self.point2,self.point3, self.spline_pos))

class SpiralEnemy(EnemyClass):
    def __init__(self, pos, walk_dir, ship_image, bullet):
        super().__init__(pos, walk_dir, ship_image, bullet)
        self.angle = 0
    
    def shoot(self, bullet_list, player_pos):
        if self.cooldown == 0:
            self.angle += 0.6
            bullet_list.append(EnemyBullet(self.get_center(), self.angle, self.bullet[1], self.bullet[0], 1))
            self.cooldown = 10

class FastshotEnemy(EnemyClass):
    def __init__(self, pos, walk_dir, ship_image, bullet):
        super().__init__(pos, walk_dir, ship_image, bullet)
        self.ammo = 0

    def shoot(self, bullet_list, player_pos):
        if self.cooldown == 0:
            self_pos = self.get_center()
            angle = math.atan2(player_pos[1] - self_pos[1], player_pos[0] - self_pos[0])
            bullet_list.append(EnemyBullet(self.get_center(), angle, self.bullet[1], self.bullet[0], 3))
            self.ammo += 1
            if self.ammo == 5:
                self.ammo = 0
                self.cooldown = 120
            else:
                self.cooldown = 5

class RingEnemy(EnemyClass):
    def __init__(self, pos, walk_dir, ship_image, bullet):
        super().__init__(pos, walk_dir, ship_image, bullet)

    def shoot(self, bullet_list, player_pos):
        if self.cooldown == 0:
            for i in range(20):
                angle = (math.tau / 20) * i
                bullet_list.append(EnemyBullet(self.get_center(), angle, self.bullet[1], self.bullet[0], 1))

            self.cooldown = 120

class EnemyBullet(PointEntity):
    def __init__(self, pos, angle, image, radius, speed):
        super().__init__(pos)
        self.speed = speed
        self.image = image
        self.radius = radius
        self.movement = (math.cos(angle), math.sin(angle))

    def draw(self, window):
        window.blit(self.image, (self.x - self.image.get_width() / 2, self.y - self.image.get_height() / 2))

    def move(self):
        self.x += self.movement[0] * self.speed
        self.y += self.movement[1] * self.speed

class GhostBullet(PointEntity):
    speed = 10
    def __init__(self, pos):
        super().__init__(pos)
        self.image = pygame.image.load(dir + 'ghost_point.png')

    def draw(self, window):
        window.blit(self.image, (self.x - self.image.get_width() / 2, self.y - self.image.get_height() / 2))

    def move(self, player_pos):
        angle = math.atan2(player_pos[1] - self.y, player_pos[0] - self.x)
        self.x += math.cos(angle) * self.speed
        self.y += math.sin(angle) * self.speed

class ExsplotionClass(PointEntity):
    def __init__(self, pos):
        super().__init__(pos)
        self.size = 0

    def draw(self, window):
        pygame.draw.circle(window, (255,255,255), self.get_pos(), self.size, 3)

    def update(self):
        self.size += 3



# bullet hell game screen
class BulletScreen(StateClass):
    def __init__(self, screen_size, stack):
        super().__init__(screen_size, stack)
        self.background = TunnelBack(screen_size, 200, 10)
        self.player = PlayerClass((self.screen_size[0]/2, self.screen_size[1]-30))
        self.bullets = []
        self.enemys = []
        self.ghost_points = []
        self.particals = []

        # enemy
        self.enemy_cooldown = 0
        self.enemy_images = {
            'red': pygame.image.load(dir + 'enemy_red.png').convert_alpha(),
            'green': pygame.image.load(dir + 'enemy_green.png').convert_alpha(),
            'blue': pygame.image.load(dir + 'enemy_blue.png').convert_alpha()
        }
        self.bullets_images = {
            'normal': (10, {
                'red': pygame.image.load(dir + 'bullet_red.png').convert_alpha(),
                'green': pygame.image.load(dir + 'bullet_green.png').convert_alpha(),
                'blue': pygame.image.load(dir + 'bullet_blue.png').convert_alpha()
            }),
            'small': (5, {
                'red': pygame.image.load(dir + 'bullet_red_small.png').convert_alpha(),
                'green': pygame.image.load(dir + 'bullet_green_small.png').convert_alpha(),
                'blue': pygame.image.load(dir + 'bullet_blue_small.png').convert_alpha()
            })
        }

    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                PausesCreen(self.screen_size, self.stack).enter_state()

        self.player.event(event)

    def loop(self):
        # spawn enemy
        self.enemy_cooldown += 1
        if self.enemy_cooldown > 120:
            self.enemy_cooldown = 0
            # walk dir
            walk_dir = random.choice(('right', 'left'))
            if walk_dir == 'right':
                x = -50
            elif walk_dir == 'left':
                x = self.screen_size[0] + 50
            # color
            color = random.choice(('red', 'green', 'blue'))

            # enemy type
            enemy_type = random.choice((SpiralEnemy, FastshotEnemy, RingEnemy))
            if enemy_type == SpiralEnemy or enemy_type == RingEnemy:
                bullet_size = self.bullets_images['small']
            elif enemy_type == FastshotEnemy:
                bullet_size = self.bullets_images['normal']

            self.enemys.append(enemy_type((x, random.randint(0, self.screen_size[1]//2)), walk_dir, self.enemy_images[color], (bullet_size[0], bullet_size[1][color])))

        # player
        self.player.move(self.screen_size)
        self.player.update()
        # player bomb
        if self.player.bomb_on:
            for bullet in self.bullets:
                if self.player.dist_to(bullet) < self.player.bomb_radius:
                    self.ghost_points.append(GhostBullet(bullet.get_pos()))
                    self.bullets.remove(bullet)
            for enemy in self.enemys:
                if dist_between(self.player.get_pos(), enemy.get_center()) < self.player.bomb_radius:
                    self.particals.append(ExsplotionClass(enemy.get_center()))
                    self.enemys.remove(enemy)

        # player bullets
        for bullet in self.player.bullets:
            bullet.move()
            if bullet.dying:
                bullet.update()
                if bullet.timer == 0:
                    self.player.bullets.remove(bullet)
            else:
                if bullet.rect.bottom < 0:
                    self.player.bullets.remove(bullet)
                for enemy in self.enemys:
                    if bullet.rect.colliderect(enemy.rect):
                        enemy.health -= 1
                        bullet.dying = True
                        break

        # enemy bullets
        for bullet in self.bullets:
            bullet.move()
            if bullet.outside(self.screen_size, 10):
                self.bullets.remove(bullet)
            if bullet.dist_to(self.player) < self.player.radius:
                self.bullets.remove(bullet)
                self.player.hurt_timer = 10

        # enemy
        for enemy in self.enemys:
            enemy.update()
            enemy.shoot(self.bullets, self.player.get_pos())
            enemy.move()
            if enemy.rect.left > self.screen_size[0] and enemy.walk_dir == 'right' or enemy.rect.right < 0 and enemy.walk_dir == 'left':
                self.enemys.remove(enemy)
            elif enemy.health <= 0:
                self.particals.append(ExsplotionClass(enemy.get_center()))
                self.enemys.remove(enemy)
            elif enemy.rect.collidepoint(self.player.get_pos()):
                self.particals.append(ExsplotionClass(enemy.get_center()))
                self.enemys.remove(enemy)
                self.player.hurt_timer = 10

        # ghost points
        for point in self.ghost_points:
            point.move(self.player.get_pos())
            if dist_between(point.get_pos(), self.player.get_pos()) < 10:
                self.ghost_points.remove(point)

        # particals
        for partical in self.particals:
            partical.update()
            if partical.size > 50:
                self.particals.remove(partical)

        self.background.update()

    def draw(self, window):
        window.fill((0,0,0))
        self.background.draw(window)

        # ghost points
        for point in self.ghost_points:
            point.draw(window)
        # particals
        for partical in self.particals:
            partical.draw(window)
        # player bullets
        for bullet in self.player.bullets:
            bullet.draw(window)
        # player
        self.player.draw(window)
        # enemy bullets
        for bullet in self.bullets:
            bullet.draw(window)
        # enemy
        for enemy in self.enemys:
            enemy.draw(window)

    def resize(self, screen_size):
        self.screen_size = screen_size
        self.background.resize(screen_size)



# if this file is run, run the game (other screens won't work anymore)
if __name__ == "__main__":
    pygame.init()
    screen_size = (700, 500)
    game_display = pygame.display.set_mode(screen_size)
    clock = pygame.time.Clock()
    state_stack = []
    game = BulletScreen(screen_size, state_stack)

    while True:
        pygame.display.set_caption('GAME TEST ' + str(int(clock.get_fps())))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            game.event(event)

        game.loop()

        game.draw(game_display)
        pygame.display.update()

        clock.tick(60)