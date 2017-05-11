# -*- coding: utf-8 -*-

import math, sys
import pygame
from pygame.locals import *


class SensorSprite(pygame.sprite.Sprite):
    def __init__(self, img_file, position, start_rotation):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(img_file)
        self.user_position = position

        self.rect = self.image.get_rect()
        self.rect.center = self.user_position

        self.user_rotation = start_rotation
        self.user_speed = 0.0
        self.user_rotation_speed = 0.0
        self.lockFlag = False

    def update(self):
        # 속도, 회전 속도에 따라 위치 정보를 업데이트한다
        x, y = self.user_position
        rad = self.user_rotation * math.pi / 180
        x += -self.user_speed * math.sin(rad)
        y += -self.user_speed * math.cos(rad)
        self.user_position = (x, y)
        self.rect.center = self.user_position


class CarSprite(pygame.sprite.Sprite):
    def __init__(self, image, position):
        pygame.sprite.Sprite.__init__(self)
        self.user_src_image = pygame.image.load(image)
        self.user_position = position
        self.user_rotation = -90
        self.user_speed = 0
        self.user_rotation_speed = 0

    def update(self):
        # 속도, 회전 속도에 따라 위치 정보를 업데이트한다
        self.user_rotation += self.user_rotation_speed
        x, y = self.user_position
        rad = self.user_rotation * math.pi / 180
        x += -self.user_speed * math.sin(rad)
        y += -self.user_speed * math.cos(rad)
        self.user_position = (x, y)

        self.image = pygame.transform.rotate(self.user_src_image, self.user_rotation)
        self.rect = self.image.get_rect()
        self.rect.center = self.user_position


class BlockSprite(pygame.sprite.Sprite):
    def __init__(self, img_file, position, start_rotation, static=True):
        pygame.sprite.Sprite.__init__(self)
        self.user_image_normal = pygame.image.load(img_file)
        self.user_position = position
        self.isStatic = static
        self.image = self.user_image_normal
        self.rect = self.image.get_rect()
        self.rect.center = self.user_position

        self.user_rotation = start_rotation
        self.user_speed = 0
        self.user_rotation_speed = 0

    def update(self, hit_list):
        # 속도, 회전 속도에 따라 위치 정보를 업데이트한다
        self.user_rotation +=  self.user_rotation_speed
        x, y = self.user_position
        rad = self.user_rotation * math.pi / 180
        x += -self.user_speed * math.sin(rad)
        y += -self.user_speed * math.cos(rad)
        self.user_position = (x, y)

        if self in hit_list:
            pass
        self.rect.center = self.user_position


pygame.init()
screen = pygame.display.set_mode((1024, 768), DOUBLEBUF)
clock = pygame.time.Clock()

rect = screen.get_rect()
car_start_pos = [100, 70]

car = CarSprite('car.png', car_start_pos)

sensors = [
    SensorSprite('dot.png', car_start_pos, -90 - 90),
    SensorSprite('dot.png', car_start_pos, -90 - 45),
    SensorSprite('dot.png', car_start_pos, -90),
    SensorSprite('dot.png', car_start_pos, -90 + 45),
    SensorSprite('dot.png', (1024 / 2, 768 / 2), -90 + 90),
]

blocks = [
    BlockSprite("wall3.png", (1024 / 2, 768 / 2), 0, False),
    BlockSprite("wall2.png", (1024 / 2, 768 / 2), 120, False),
    BlockSprite("wall1.png", (1024 / 2, 768 / 2), 240, False),
    BlockSprite("w.png", (1024 / 2, 5), 0, True),
    BlockSprite("w.png", (1024 / 2, 761), 0, True),
    BlockSprite("h.png", (7, 768 / 2), 0, True),
    BlockSprite("h.png", (1017, 768 / 2), 0, True),
]

car_group = pygame.sprite.RenderPlain(car)
sensor_group = pygame.sprite.RenderPlain(*sensors)
block_group = pygame.sprite.RenderPlain(*blocks)

background = pygame.image.load('background.jpg')
background = pygame.transform.scale(background, (1280, 768))
screen.blit(background, (0, 0))

while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        # 키입력에 따라 속도, 회전 속도를 설정
        if hasattr(event, 'key'):
            down = event.type == KEYDOWN
            if event.key == K_RIGHT:
                car.user_rotation_speed = down * -10  # 시계 방향이 마이너스인 것에 유의
            elif event.key == K_LEFT:
                car.user_rotation_speed = down * 10
            elif event.key == K_UP:
                car.user_speed = down * 10
            elif event.key == K_DOWN:
                car.user_speed = down * -10
    deltat = clock.tick(30)

    # 움직이는 block 객체들의 이동 처리
    for index, block in enumerate(blocks):
        if not block.isStatic:
            block.user_rotation_speed = 1
            block.user_speed = -3

    # 차의 회전, 이동에 따라 방향,각도를 같게 처리
    for number, sensor in enumerate(sensors):
        sensor.user_position = car.user_position
        sensor.user_rotation = car.user_rotation - (45 * number) + 90
        sensor.user_speed = 0.0

    # 모든 센서들의 lockFlag값 False로 초기화
    for index, sens in enumerate(sensors):
        sens.user_speed = 1.0

    # 차의 위치로부터 거리가 200인
    distance = 200
    lock_count = [0,0]
    for i in range(distance):
        for block in block_group:
            if i != 0:
                collision_list = pygame.sprite.spritecollide(block, sensor_group,False)
                for sensor in collision_list:
                    sensor.user_speed = 0.0
                    pass
        for index, sen in enumerate(sensors):
            sen.update() # lockFlag가 False인 센서객체들은 이동


    car_group.update()
    collisions = pygame.sprite.spritecollide(car, block_group, False)
    block_group.update(collisions)

    sensor_group.clear(screen, background)
    car_group.clear(screen, background)
    block_group.clear(screen, background)

    sensor_group.draw(screen)
    car_group.draw(screen)
    block_group.draw(screen)
    pygame.display.flip()

