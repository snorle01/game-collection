from func import *
from bullet_back import TunnelBack
import pygame, sys, math, random

def dist_between(pos1, pos2):
    lenght_x = pos1[0] - pos2[0]
    lenght_y = pos1[1] - pos2[1]
    return math.sqrt(lenght_x*lenght_x + lenght_y*lenght_y)

class EntityClass:
    def __init__(self, pos):
        self.x = pos[0]
        self.y = pos[1]

    def get_pos(self) -> tuple:
        return self.x, self.y

    def outside(self, screen_size, offset=0) -> bool:
        return self.x+offset < 0 or self.x-offset > screen_size[0] or self.y+offset < 0 or self.y-offset > screen_size[1]

    def dist_to(self, target) -> float:
        lenght_x = self.x - target.x
        lenght_y = self.y - target.y
        return math.sqrt(lenght_x*lenght_x + lenght_y*lenght_y)

class PlayerClass(EntityClass):
    def __init__(self, pos):
        super().__init__(pos)
        self.hurt_timer = 0

        # shot
        self.bullets = []
        self.cooldown_counter = 0

        # bomb
        self.bomb_on = False
        self.bomb_pos = None
        self.bomb_radius = 0

    def draw(self, window):
        if self.hurt_timer > 0:
            pygame.draw.circle(window, (255,0,0), self.get_pos(), 10)
        else:
            pygame.draw.circle(window, (255,255,0), self.get_pos(), 10)
        
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

    def event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                self.bomb_on = True
                self.bomb_pos = self.get_pos()

    def move(self, screen_size):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LSHIFT]:
            speed = 1
        else:
            speed = 3

        if keys[pygame.K_UP]:
            self.y -= speed
            if self.y < 0:
                self.y = 0
        if keys[pygame.K_DOWN]:
            self.y += speed
            if self.y > screen_size[1]:
                self.y = screen_size[1]
        if keys[pygame.K_LEFT]:
            self.x -= speed
            if self.x < 0:
                self.x = 0
        if keys[pygame.K_RIGHT]:
            self.x += speed
            if self.x > screen_size[0]:
                self.x = screen_size[0]

        if keys[pygame.K_z]:
            if self.cooldown_counter == 0:
                self.bullets.append(PlayerBullet(self.get_pos()))
                self.cooldown_counter = 5

class PlayerBullet(EntityClass):
    def __init__(self, pos):
        super().__init__(pos)

    def draw(self, window):
        pygame.draw.circle(window, (255,255,0), self.get_pos(), 5)

    def move(self):
        self.y -= 10

class EnemyClass(EntityClass):
    def __init__(self, pos):
        super().__init__(pos)
        # spawning ang going in frame
        self.just_spawed = True
        self.stoping = False
        self.stoping_cos = 0
        self.target_y = random.randint(0, 100)

        # shooting
        self.start_shooting = False
        self.cooldown = 0
        self.angle = 0

        self.speed = 5
        self.health = 20

    def draw(self, window):
        pygame.draw.circle(window, (255,0,0), self.get_pos(), 10)

    def update(self):
        if self.cooldown > 0:
            self.cooldown -= 1
        
    def move(self):
        if self.just_spawed:
            self.y += self.speed
            if self.y > self.target_y:
                self.stoping = True
                self.just_spawed = False
        elif self.stoping:
            cos = math.cos(self.stoping_cos)
            self.y += self.speed * cos
            self.stoping_cos += 0.05
            if self.stoping_cos >= math.pi/2:
                self.stoping = False
                self.start_shooting = True

    def shoot(self, bullet_list):
        if self.start_shooting and self.cooldown == 0:
            self.angle += 0.3
            bullet_list.append(BulletClass(self.get_pos(), self.angle))
            self.cooldown = 5

class BulletClass(EntityClass):
    speed = 1
    def __init__(self, pos, angle):
        super().__init__(pos)
        self.movement = (math.cos(angle), math.sin(angle))

    def draw(self, window):
        pygame.draw.circle(window, (255,255,255), self.get_pos(), 5)

    def move(self):
        self.x += self.movement[0] * self.speed
        self.y += self.movement[1] * self.speed

# bullet hell game screen
class BulletScreen(StateClass):
    def __init__(self, screen_size, stack):
        super().__init__(screen_size, stack)
        self.background = TunnelBack(screen_size, 200, 10)
        self.player = PlayerClass((self.screen_size[0]/2, self.screen_size[1]-20))
        self.bullets = []
        self.enemys = []

        self.enemy_cooldown = 0

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
            self.enemys.append(EnemyClass((random.randint(0, self.screen_size[0]), -10)))

        # player
        self.player.update()
        self.player.move(self.screen_size)
        if self.player.bomb_on:
            for bullet in self.bullets:
                if self.player.dist_to(bullet) < self.player.bomb_radius:
                    self.bullets.remove(bullet)
            for enemy in self.enemys:
                if self.player.dist_to(enemy) < self.player.bomb_radius:
                    self.enemys.remove(enemy)

        # player bullets
        for bullet in self.player.bullets:
            remove_bullet = False
            bullet.move()
            if bullet.y < 0:
                remove_bullet = True
            for enemy in self.enemys:
                if bullet.dist_to(enemy) < 15:
                    enemy.health -= 1
                    remove_bullet = True
                    break
            
            if remove_bullet:
                self.player.bullets.remove(bullet)
            

        # enemy bullets
        for bullet in self.bullets:
            bullet.move()
            if bullet.outside(self.screen_size, 10):
                self.bullets.remove(bullet)
            if bullet.dist_to(self.player) < 5:
                self.bullets.remove(bullet)
                self.player.hurt_timer = 10

        # enemy
        for enemy in self.enemys:
            enemy.update()
            enemy.shoot(self.bullets)
            enemy.move()
            if enemy.health <= 0:
                self.enemys.remove(enemy)

    def draw(self, window):
        window.fill((0,0,0))
        self.background.draw(window)

        # player bullets
        for bullet in self.player.bullets:
            bullet.draw(window)
        # enemy bullets
        for bullet in self.bullets:
            bullet.draw(window)
        # enemy
        for enemy in self.enemys:
            enemy.draw(window)
        # player
        self.player.draw(window)

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