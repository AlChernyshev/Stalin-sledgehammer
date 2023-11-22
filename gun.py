import math
from random import choice
import random

import pygame


FPS = 30

RED = 0xFF0000
BLUE = 0x0000FF
YELLOW = 0xFFC91F
GREEN = 0x00FF00
MAGENTA = 0xFF03B8
CYAN = 0x00FFCC
BLACK = (0, 0, 0)
WHITE = 0xFFFFFF
GREY = 0x7D7D7D
GAME_COLORS = [BLUE, YELLOW, GREEN, MAGENTA, CYAN]

W = 1800
H = 900
W0 = W
H0 = H

class Main:
    def __init__(self):
        self.time = pygame.time.get_ticks()
    def add_target(self, keys):
        global targets
        if keys[pygame.K_9] and ((pygame.time.get_ticks() - self.time)//1000 > 1):
            new_target = choice([Target(), TargetTeleport(), TargetRandom(), TargetHorizontal(), TargetVertical()])
            targets.append(new_target)
            self.time = pygame.time.get_ticks()

    def delete_target(self, keys):
        if keys[pygame.K_0] and (len(targets)>0):
            targets.pop()

    def show_score(self):
        """Выводит счетчик очков на экран"""
        f1 = pygame.font.Font(None, 36)
        text1 = f1.render("Количество очков:" + str(points), 1, (90, 40, 250))
        screen.blit(text1, (10, 50))
class Ball:
    def __init__(self, screen: pygame.Surface, x=40, y= H-100):
        """ Конструктор класса ball

        Args:
        x - начальное положение мяча по горизонтали
        y - начальное положение мяча по вертикали
        """
        self.screen = screen
        self.x = x
        self.y = y
        self.r = 10
        self.vx = 0
        self.vy = 0
        self.color = choice(GAME_COLORS)
        self.live = 30

    def position(self, x, y):
        self.x = x
        self.y = y

    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        speed_lose = 0.8
        if (self.vy != 0) or (self.y < H - 2*self.r):
            self.vy = self.vy - 0.2
        if (self.vy == 0) and (self.y > H - 2*self.r):
            self.y = H - self.r
            self.vx *= speed_lose
        if abs(self.vx) < 2:
            self.vx = 0
        self.x += self.vx
        self.y -= self.vy
        if (self.x <= self.r) and (self.vx < 0):
            self.vx = -self.vx*speed_lose
            self.vy = self.vy * speed_lose
        elif  (self.x >= (W - self.r)) and (self.vx > 0):
            self.vx = -self.vx * speed_lose
            self.vy = self.vy * speed_lose
            if abs(self.vx) < 2:
                self.vx = 0
        if (self.y <= self.r) and (self.vy > 0):
            self.vy = -self.vy*speed_lose
            self.vx = self.vx * speed_lose
            if abs(self.vy) < 5:
                self.vy = 0
        elif (self.y >= (H - self.r)) and (self.vy < 0):
            self.vy = -self.vy * speed_lose
            self.vx = self.vx * speed_lose
            if abs(self.vy) < 5:
                self.vy = 0



    def draw(self):
        """Рисует снаряд"""
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )

    def delete(self):
        """Удаляет неподвижный снаряд"""
        if self.vy**2 +self.vx**2 == 0:
            self.live -= 1
        if self.live <= 0:
            balls.pop(balls.index(self))

    def hittest(self, obj):
        """Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.
        Args:
            obj: Обьект, с которым проверяется столкновение.
        Returns:
            Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
        """
        return ((((self.x - obj.x)**2 + (self.y - obj.y)**2)) < (self.r + obj.r)**2)

    def hitevent(self):
        """Описывает что происходит с снарядом при столкновение"""
        self.live -= 50 #Удаление снарядов при столкновении с мищенью

class ExplosiveBall(Ball):
    """Тип снарядов которые при столкновении с целью распадаются на несколько"""
    def hitevent(self):
        """Описывает что происходит с снарядом при столкновение"""
        self.live -= 50 #Удаление снарядов при столкновении с мищенью
        for i in [1, -1]:
            for j in [1, -1]:
                new_ball = Ball(self.screen)
                new_ball.vx = i*self.vx
                new_ball.vy = j*self.vy
                new_ball.x = self.x
                new_ball.y = self.y
                new_ball.r = 5
                balls.append(new_ball)

class Bomb(Ball):
    def move(self):
        self.vy -= 0.2
        self.y -= self.vy
        if (self.y >= (H - self.r)) and (self.vy < 0):
            self.vy = self.vy * 0
            self.vx = self.vx * 0

    def delete(self):
        if self.y >= H-self.r:
            self.live -= 50
        if self.live <= 0:
            self.explosion()
            bombs.pop(bombs.index(self))
    def draw(self):
        self.surf = pygame.image.load('image/bomb.png')
        self.surf.set_colorkey((255, 255, 255))
        scale = pygame.transform.scale(self.surf, (20, 30))
        scale_rect = scale.get_rect(center=(self.x, self.y))
        screen.blit(scale, scale_rect)

    def explosion(self):
        global explosions
        new_explosion = Explosion()
        new_explosion.x = self.x
        new_explosion.y = self.y
        new_explosion.frame = 1
        explosions.append(new_explosion)


class Explosion:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.surf = pygame.image.load('image/explosion1.png')
        self.frame = 0
        self.r = 20
    def draw(self):
        if (self.frame > 0) and (self.frame < 24):
            self.frame += 24/30
            self.surf = pygame.image.load('image/explosion' + str(int(self.frame//(24/15))) + '.png')
            self.surf.set_colorkey((255, 255, 255))
            scale = pygame.transform.scale(self.surf, (40, 60))
            scale_rect = scale.get_rect(center=(self.x, self.y-scale.get_height()/2))
            screen.blit(scale, scale_rect)

    def delete(self):
        if self.frame > 24:
            explosions.pop(explosions.index(self))

    def hittest(self, obj):
        """Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.
        Args:
            obj: Обьект, с которым проверяется столкновение.
        Returns:
            Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
        """
        return ((((self.x - obj.x)**2 + (self.y - obj.y)**2)) < (self.r + obj.r)**2)


class Gun:
    def __init__(self, screen):
        self.screen = screen
        self.f2_power = 10
        self.f2_on = 0
        self.an = 1
        self.color = GREY
        self.x = 40
        self.y = H-20
        self.vx = 0
        self.type = 1
        self.r = 25
        self.live = 5
        self.max_live = self.live
        self.time = pygame.time.get_ticks()

    def fire2_start(self, event):
        self.f2_on = 1

    def fire2_end(self, event):
        """Выстрел мячом.

        Происходит при отпускании кнопки мыши.
        Начальные значения компонент скорости мяча vx и vy зависят от положения мыши.
        """
        global balls, bullet
        bullet += 1
        new_ball = Ball(self.screen)
        if self.type == 1:
            new_ball = Ball(self.screen)
            new_ball.position(self.x, self.y)
        if self.type == 2:
            new_ball = ExplosiveBall(self.screen)
            new_ball.position(self.x, self.y)
        new_ball.r += 5
        self.an = math.atan2((event.pos[1]-new_ball.y), (event.pos[0]-new_ball.x))
        new_ball.vx = self.f2_power * math.cos(self.an)
        new_ball.vy = - self.f2_power * math.sin(self.an)
        balls.append(new_ball)
        self.f2_on = 0
        self.f2_power = 10

    def targetting(self, event):
        """Прицеливание. Зависит от положения мыши."""
        if event:
            self.an = math.atan((event.pos[1]-450) / (event.pos[0]-20))
        if self.f2_on:
            self.color = RED
        else:
            self.color = GREY

    def draw(self):
        self.surf = pygame.image.load('image/tank1.png')
        self.surf.set_colorkey((255, 255, 255))
        scale = pygame.transform.scale(self.surf, (50, 50))
        scale = pygame.transform.flip(scale, (self.vx > 0), False)
        scale_rect = scale.get_rect(center=(self.x, self.y))
        screen.blit(scale, scale_rect)

    def power_up(self):
        if self.f2_on:
            if self.f2_power < 30:
                self.f2_power += 1
            self.color = RED
        else:
            self.color = GREY

    def typeBall(self, event):
        if event.key == pygame.K_1:
            self.type = 1
        if event.key == pygame.K_2:
            self.type = 2

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.x > 20:
            self.vx = 5
            self.x -= 5
        elif keys[pygame.K_RIGHT] and self.x < W-20:
            self.x += 5
            self.vx = -5

    def hit(self):
        if (pygame.time.get_ticks()-self.time) > 1200:
            self.live -= 1
            self.time = pygame.time.get_ticks()

    def game_over(self):
        if self.live <= 0:
            """Завершает игру если закончились жизни"""
            self.surf = pygame.image.load('image/death.jpg')
            scale = pygame.transform.scale(self.surf, (W, H))
            self.rect = scale.get_rect(center=(W/2, H/2))
            screen.blit(scale, self.rect)
            f1 = pygame.font.Font(None, 36)
            text1 = f1.render("Набранный счет: " + str(points), 1, (82,2,5))
            screen.blit(text1, (W*0.4, H*0.6))

    def hp_bar(self):
        pygame.draw.rect(self.screen, (0, 0, 0), (W - 221, 9, 202, 32), 1)
        pygame.draw.rect(self.screen, (242, 11, 7), (W-220, 10, (200//self.max_live)*self.live, 30))

class Target:
    def __init__(self):
        """ Конструктор класса target
        """
        self.screen = screen
        self.x = random.randint(W-300, W-50)
        self.y = random.randint(H-200, H-50)
        self.r = 20
        self.color = RED
        self.points = 0
        self.live = 1
        self.vx = 0
        self.vy = 0
        self.start_ticks = pygame.time.get_ticks()

    def new_target(self):
        """ Инициализация новой цели. """
        self.x = random.randint(W-300, W-50)
        self.y = random.randint(H-200, H-50)
        self.r = random.randint(5, 50)
        self.vx = 0
        self.vy = 0
        self.color = RED
        self.live = 1

    def hit(self):
        """Попадание шарика в цель."""
        global points
        points += 1

    def draw(self):
        """Отрисовка мишени с загруженного изображения"""
        self.surf = pygame.image.load('image/target6.png')
        scale = pygame.transform.scale(self.surf, (100, 50))
        scale = pygame.transform.flip(scale, (self.vx > 0), False)
        if self.vx == 0:
            if self.vy != 0:
                scale = pygame.transform.rotate(scale, 90)
        else:
            scale = pygame.transform.rotate(scale, math.atan(self.vy/self.vx)/(2*math.pi)*360)

        self.rect = scale.get_rect(center=(self.x, self.y))
        self.surf.set_colorkey((255, 255, 255))
        screen.blit(scale, self.rect)

    def move(self):
        """Движение мишеней с постоянными скоростями и отражение от стен
        """
        self.x += self.vx
        self.y -= self.vy
        if (self.x <= self.r) and (self.vx < 0):
            self.vx = -self.vx
        elif  (self.x >= (W - self.r)) and (self.vx > 0):
            self.vx = -self.vx
        if (self.y <= self.r) and (self.vy > 0):
            self.vy = -self.vy
        elif (self.y >= (H - self.r)) and (self.vy < 0):
            self.vy = -self.vy

    def targetbomb(self):
        """описывает сброс бомб мишенью"""
        pass


class TargetHorizontal(Target):
    def __init__(self):
        super().__init__()
        self.vx = random.randint(2, 10)

    def new_target(self):
        """ Инициализация новой цели. """
        super().new_target()
        self.vx = random.randint(2, 10)

    def targetbomb(self):
        """описывает сброс бомб мишенью"""
        global bombs
        new_bomb = Bomb(self.screen)
        new_bomb.position(self.x, self.y)
        bombs.append(new_bomb)
        self.start_ticks = pygame.time.get_ticks()

class TargetVertical(Target):
    def __init__(self):
        super().__init__()
        self.vy = random.randint(2, 10)
    def new_target(self):
        """ Инициализация новой цели. """
        super().new_target()
        self.vy = random.randint(2, 10)

class TargetRandom(Target):
    def __init__(self):
        super().__init__()
        self.vx = random.randint(2, 10)
        self.vy = random.randint(2, 10)

    def new_target(self):
        """ Инициализация новой цели. """
        super().new_target()
        self.vx = random.randint(2, 10)
        self.vy = random.randint(2, 10)

    def targetbomb(self):
        global bombs
        new_bomb = Bomb(self.screen)
        new_bomb.position(self.x, self.y)
        bombs.append(new_bomb)
        self.start_ticks = pygame.time.get_ticks()

class TargetTeleport(Target):
    def __init__(self):
        super().__init__()
        self.vx = random.randint(2, 10)
        self.vy = random.randint(2, 10)
        self.r = random.randint(5, 50)
        self.time = 0

    def move(self):
        a = pygame.time.get_ticks()/1000
        if a-self.time > 2:
            self.time += 1
            self.x += self.vx*FPS
            self.y -= self.vy*FPS
            if (self.x <= self.r) and (self.vx < 0):
                self.vx = -self.vx
            elif  (self.x >= (W - self.r)) and (self.vx > 0):
                self.vx = -self.vx
            if (self.y <= self.r) and (self.vy > 0):
                self.vy = -self.vy
            elif (self.y >= (H - self.r)) and (self.vy < 0):
                self.vy = -self.vy

    def new_target(self):
        """ Инициализация новой цели. """
        super().new_target()
        self.vx = random.randint(2, 10)
        self.vy = random.randint(2, 10)

    def draw(self):
        pygame.draw.circle(
                self.screen,
                self.color,
                (self.x, self.y),
                self.r
            )

class Plane():
    def __init__(self):
        """ Конструктор класса Plane
        """
        self.screen = screen
        self.x = random.randint(W-300, W-50)
        self.y = random.randint(H-200, H-50)
        self.r = 20
        self.color = RED
        self.points = 0
        self.live = 1
        self.vx = 0
        self.vy = 0
        self.time = pygame.time.get_ticks()

    def new_plane(self):
        """ Инициализация новой цели. """
        self.x = random.randint(W-300, W-50)
        self.y = random.randint(H-200, H-50)
        self.r = random.randint(5, 50)
        self.vx = 0
        self.vy = 0
        self.color = RED
        self.live = 1

    def hit(self):
        """Попадание шарика в цель."""
        global points
        points += 5

    def draw(self):
        self.surf = pygame.image.load('image/target6.png')
        scale = pygame.transform.scale(self.surf, (100, 50))
        scale = pygame.transform.flip(
            scale, (self.vx > 0), False)
        if self.vx == 0:
            if self.vy < 0:
                scale = pygame.transform.rotate(scale, 90)
            if self.vy > 0:
                scale = pygame.transform.rotate(scale, -90)
        else:
            scale = pygame.transform.rotate(scale, math.atan(self.vy/self.vx)/(2*math.pi)*360)

        self.rect = scale.get_rect(center=(self.x, self.y))
        self.surf.set_colorkey((255, 255, 255))
        screen.blit(scale, self.rect)

    def bomb(self, keys):
        """описывает сброс бомб мишенью"""
        global bombs
        if keys[pygame.K_SPACE] and ((pygame.time.get_ticks() - self.time)> 500):
            new_bomb = Bomb(self.screen)
            new_bomb.position(self.x, self.y)
            bombs.append(new_bomb)
            self.time = pygame.time.get_ticks()

    def move(self, keys):
        if keys[pygame.K_a]:
            self.vx -= 0.3
        elif keys[pygame.K_d]:
            self.vx += 0.3
        elif keys[pygame.K_w]:
            self.vy += 0.3
        elif keys[pygame.K_s]:
            self.vy -= 0.3
        self.x += self.vx
        self.y -= self.vy
        if (self.x <= self.r) and (self.vx < 0):
            self.vx = -self.vx
        elif  (self.x >= (W - self.r)) and (self.vx > 0):
            self.vx = -self.vx
        if (self.y <= self.r) and (self.vy > 0):
            self.vy = -self.vy
        elif (self.y >= (H - self.r)) and (self.vy < 0):
            self.vy = -self.vy


pygame.init()

BG_surf = pygame.image.load('image/BG8.jpg')
BG_scale = pygame.transform.scale(BG_surf, (W,H))
BG_scale_rect = BG_scale.get_rect(center=(W/2, H/2))

screen = pygame.display.set_mode((800, 600))
bullet = 0
points = 0
balls = []
bombs = []
explosions = []
targets = []
finished = False
menu = True

"""Настройка фона"""
while not finished:
    while menu:
        screen.fill(WHITE)
        f = pygame.font.Font(None, 56)
        text = f.render("Выберите фон:", 1, (90, 140, 250))
        screen.blit(text, (250, 50))
        for i, j in zip(["1.Аустерлиц", "2.Бородино", "3.Переход через Альпы", "4.Принцеса Греза"], range(1,5)):
            f1 = pygame.font.Font(None, 46)
            text1 = f1.render(i, 1, (0, 0, 0))
            screen.blit(text1, (50, 50 + j*50))
        for i, j in zip(["5.Апофеоз войны", "6.У крепостной стены", "7.Госдолг США", "8.Черный фон"], range(1,5)):
            f1 = pygame.font.Font(None, 46)
            text1 = f1.render(i, 1, (0, 0, 0))
            screen.blit(text1, (450, 50 + j*50))
        f1 = pygame.font.Font(None, 46)
        text1 = f1.render("0.Белый фон", 1, (0, 0, 0))
        screen.blit(text1, (450,  300))
        pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                finished = True
                menu = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_0]:
            BG_scale.fill(WHITE)
            W = 800
            H = 600
            menu = False
            finished = True
        for i, j in zip(range(1, 9), [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5, pygame.K_6, pygame.K_7, pygame.K_8]):
            if keys[j]:
                image = 'image/BG' + str(i) + '.jpg'
                BG_surf = pygame.image.load(image)
                BG_W = BG_surf.get_width()
                BG_H = BG_surf.get_height()
                scale = 1
                if (BG_W > W0) or (BG_H > H0):
                    scale = max(BG_W/W, BG_H/H)
                W = int(BG_W/scale)
                H = int(BG_H/scale)
                BG_scale = pygame.transform.scale(BG_surf, (W, H))
                BG_scale_rect = BG_scale.get_rect(center=(W / 2, H / 2))
                screen = pygame.display.set_mode((W, H), )
                menu = False
                finished = True
                #Изменить позицию окна

clock = pygame.time.Clock()
gun = Gun(screen)
main = Main()
plane = Plane()
finished = False

while not finished:
    screen.blit(BG_scale, BG_scale_rect)
    keys = pygame.key.get_pressed()
    main.add_target(keys)
    main.delete_target(keys)

    main.show_score()
    gun.draw()
    gun.hp_bar()
    plane.draw()
    for t in targets:
        t.draw()
    for b in balls:
        b.draw()
    for bm in bombs:
        bm.draw()
    for e in explosions:
        e.draw()
    pygame.display.update()

    if gun.live <= 0:
        gun.game_over()
        pygame.display.update()
        pygame.time.wait(5000)
        finished = True

    clock.tick(FPS)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            finished = True
        elif event.type == pygame.MOUSEBUTTONDOWN:
            gun.fire2_start(event)
        elif event.type == pygame.MOUSEBUTTONUP:
            gun.fire2_end(event)
        elif event.type == pygame.MOUSEMOTION:
            gun.targetting(event)
        elif event.type == pygame.KEYDOWN:
            gun.typeBall(event)

    gun.move(keys)
    gun.power_up()


    plane.move(keys)
    plane.bomb(keys)

    for t in targets:
        t.move()
        seconds = (pygame.time.get_ticks() - t.start_ticks) / 1000
        if seconds > 1 + random.randint(0, 100) / 10:
            t.targetbomb()

    for b in balls:
        b.move()
        b.delete()
        if b.hittest(plane):
            b.hitevent()
        if b.hittest(plane) and plane.live:
            plane.live = 0
            plane.hit()
            plane.new_plane()
        for t in targets:
            if b.hittest(t):
                b.hitevent()
            if b.hittest(t) and t.live:
                t.live = 0
                t.hit()
                t.new_target()

    for bm in bombs:
        bm.move()
        bm.delete()

    for e in explosions:
        if e.hittest(gun):
            gun.hit()

        e.delete()



pygame.quit()
