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
GAME_COLORS = [RED, BLUE, YELLOW, GREEN, MAGENTA, CYAN]

W = 800
H = 600


class Ball:
    def __init__(self, screen: pygame.Surface, x=40, y=450):
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


    def move(self):
        """Переместить мяч по прошествии единицы времени.

        Метод описывает перемещение мяча за один кадр перерисовки. То есть, обновляет значения
        self.x и self.y с учетом скоростей self.vx и self.vy, силы гравитации, действующей на мяч,
        и стен по краям окна (размер окна 800х600).
        """
        speed_lose = 0.9
        if self.vy != 0:
            self.vy = self.vy - 0.2
        if self.vy == 0:
            self.y = H - self.r
            self.vx *= speed_lose
        self.x += self.vx
        self.y -= self.vy
        if (self.x <= self.r) and (self.vx < 0):
            self.vx = -self.vx*speed_lose
            self.vy = self.vy * speed_lose
            if abs(self.vx) < 2:
                self.vx = 0
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
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )

    def hittest(self, obj):
        """Функция проверяет сталкивалкивается ли данный обьект с целью, описываемой в обьекте obj.

        Args:
            obj: Обьект, с которым проверяется столкновение.
        Returns:
            Возвращает True в случае столкновения мяча и цели. В противном случае возвращает False.
        """
        return ((((self.x - obj.x)**2 + (self.y - obj.y)**2)) < (self.r + obj.r)**2)



class Gun:
    def __init__(self, screen, x=40, y=450):
        self.screen = screen
        self.f2_power = 10
        self.f2_on = 0
        self.an = 1
        self.color = GREY
        self.x = x
        self.y = y

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
        r = pygame.Rect(40, 450, 10, 5)
        pygame.draw.rect(
            self.screen,
            self.color,
            r
        )
        # FIXIT don't know how to do it

    def power_up(self):
        if self.f2_on:
            if self.f2_power < 100:
                self.f2_power += 1
            self.color = RED
        else:
            self.color = GREY


class Target:
    def __init__(self):
        """ Конструктор класса target
        """
        self.screen = screen
        self.x = random.randint(600, 780)
        self.y = random.randint(300, 550)
        self.r = random.randint(2, 50)
        self.color = RED
        self.points = 0
        self.live = 1

    def new_target(self):
        """ Инициализация новой цели. """
        x = self.x = random.randint(600, 780)
        y = self.y = random.randint(300, 550)
        r = self.r = random.randint(2, 50)
        color = self.color = RED
        self.live = 1

    def hit(self, points=1):
        """Попадание шарика в цель."""
        self.points += points

    def draw(self):
        pygame.draw.circle(
            self.screen,
            self.color,
            (self.x, self.y),
            self.r
        )

    def show_points(self):
        """Выводит счетчик очков на экран"""
        f1 = pygame.font.Font(None, 36)
        text1 = f1.render("Количество очков:" + str(self.points), 1, (90, 40, 250))
        screen.blit(text1, (10, 50))



pygame.init()
screen = pygame.display.set_mode((W, H))
bullet = 0
balls = []

clock = pygame.time.Clock()
gun = Gun(screen)
target = Target()
target2 = Target()
finished = False

while not finished:
    screen.fill(WHITE)
    gun.draw()
    target.draw()
    target.show_points()
    target2.draw()
    target2.show_points()
    for b in balls:
        b.draw()
    pygame.display.update()

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

    for b in balls:
        b.move()
        if b.hittest(target) and target.live:
            target.live = 0
            target.hit()
            target.new_target()
        if b.hittest(target2) and target2.live:
            target2.live = 0
            target2.hit()
            target2.new_target()
    gun.power_up()

pygame.quit()