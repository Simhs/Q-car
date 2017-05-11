# -*- coding: utf-8 -*-

import math, sys
import pygame
from pygame.locals import *
import operator
import random
import time
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
        self.distance = 200

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
        self.user_rotation = -135
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
        self.terminal = False

    def update(self, hit_list):
        # 속도, 회전 속도에 따라 위치 정보를 업데이트한다
        self.user_rotation +=  self.user_rotation_speed
        x, y = self.user_position
        rad = self.user_rotation * math.pi / 180
        x += -self.user_speed * math.sin(rad)
        y += -self.user_speed * math.cos(rad)
        self.user_position = (x, y)

        if self in hit_list:
            self.terminal = True
        self.rect.center = self.user_position



class RL:
    class Game:
        def __init__(self):
            pygame.init()
            self.screen = pygame.display.set_mode((1024, 768), DOUBLEBUF)
            self.clock = pygame.time.Clock()
            car_start_pos = [100, 70]

            self.car = CarSprite('car.png', car_start_pos)

            background = pygame.image.load('background.jpg')
            self.background = pygame.transform.scale(background, (1024, 768))
            self.screen.blit(self.background, (0, 0))

            self.sensors = [
                SensorSprite('dot.png', car_start_pos, -90 - 90),
                SensorSprite('dot.png', car_start_pos, -90 - 45),
                SensorSprite('dot.png', car_start_pos, -90),
                SensorSprite('dot.png', car_start_pos, -90 + 45),
                SensorSprite('dot.png', (1024 / 2, 768 / 2), -90 + 90),
            ]

            self.blocks = [
                BlockSprite("wall3.png", (1024 / 2, 768 / 2), 0, False),
                BlockSprite("wall2.png", (1024 / 2, 768 / 2), 120, False),
                BlockSprite("wall1.png", (1024 / 2, 768 / 2), 240, False),
                BlockSprite("w.png", (1024 / 2, 5), 0, True),
                BlockSprite("w.png", (1024 / 2, 761), 0, True),
                BlockSprite("h.png", (7, 768 / 2), 0, True),
                BlockSprite("h.png", (1017, 768 / 2), 0, True),
            ]

            self.car_group = pygame.sprite.RenderPlain(self.car)
            self.sensor_group = pygame.sprite.RenderPlain(self.sensors)
            self.block_group = pygame.sprite.RenderPlain(self.blocks)

        def objectMove(self):
            self.car_group.update()
            collisions = pygame.sprite.spritecollide(self.car, self.block_group, False)
            self.block_group.update(collisions)

            self.sensor_group.clear(self.screen, self.background)
            self.car_group.clear(self.screen, self.background)
            self.block_group.clear(self.screen, self.background)

            self.sensor_group.draw(self.screen)
            self.car_group.draw(self.screen)
            self.block_group.draw(self.screen)
            pygame.display.flip()

            # 움직이는 block 객체들의 이동 처리
            for index, block in enumerate(self.blocks):
                if not block.isStatic:
                    block.user_rotation_speed = 1
                    block.user_speed = -3

            # 차의 회전, 이동에 따라 방향,각도를 같게 처리
            for number, sensor in enumerate(self.sensors):
                sensor.user_position = self.car.user_position
                sensor.user_rotation = self.car.user_rotation - (45 * number) + 90

            # 모든 센서들의 lockFlag값 False로 초기화
            for index, sens in enumerate(self.sensors):
                sens.user_speed = 1.0
                sens.distance = 200

        def isTerminal(self):
            for block in self.blocks:
                if block.terminal:
                    return True
            return False

        def getObservedState(self):
            # 차의 위치로부터 거리가 200인
            distance = 200
            for i in range(distance):
                for index, block in enumerate(self.blocks):
                    if i != 0:
                        collision_list = pygame.sprite.spritecollide(block, self.sensor_group, False)
                        for sindex, sensor in enumerate(collision_list):
                            sensor.user_speed = 0.0
                            if sensor.distance > i:
                                sensor.distance = i
                for index, sen in enumerate(self.sensors):
                    sen.update()

            show_list = []
            for index, sen in enumerate(self.sensors):
                show_list.append(int((sen.distance - 20) / 20))
            #print show_list
            result = 0
            for index, num in enumerate(show_list):
                result += math.pow(10,index)*num
            return int(result)

        def selectAction2(self,Qtable):
            a = 0
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
                # 키입력에 따라 속도, 회전 속도를 설정
                if hasattr(event, 'key'):
                    down = event.type == KEYDOWN
                    if event.key == K_RIGHT:
                        a = 1
                        self.car.user_rotation_speed = down * -10  # 시계 방향이 마이너스인 것에 유의
                    elif event.key == K_LEFT:
                        a = 0
                        self.car.user_rotation_speed = down * 10
                    else:
                        a = 2
                        self.car.user_rotation_speed = 0
                        #elif event.key == K_UP:
                    #    pass
                    #elif event.key == K_DOWN:
                    #    self.car.user_speed = down * -10
            self.car.user_speed =  10
            return a
        def selectAction(self,Qtable,cur_s):
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            self.car.user_speed = 10
            if random.uniform(0, 1) < Qtable.e:
                a = random.randint(0,2)

                if a == 0:
                    self.car.user_rotation_speed =  10  # 시계 방향이 마이너스인 것에 유의
                elif a == 1:
                    self.car.user_rotation_speed =  -10
                else:
                    self.car.user_rotation_speed = 0

            else:
                #print cur_s
                if not ((Qtable.Q[cur_s].a[0] == Qtable.Q[cur_s].a[1]) == Qtable.Q[cur_s].a[2]):
                    a = random.randint(0,2)
                else:
                    a = Qtable.Q[cur_s].a.index(max(Qtable.Q[cur_s].a))
                if a == 0:
                    self.car.user_rotation_speed =  10  # 시계 방향이 마이너스인 것에 유의
                elif a == 1:
                    self.car.user_rotation_speed = -10
                elif a == 2 :
                    self.car.user_rotation_speed = 0
                print a
            #print a
            return  a

        def getReward(self):
            if self.isTerminal():
                return -100
            else:
                return 0

        def epoch(self,Qtable):
            self.__init__()
            self.objectMove()
            start_state = self.getObservedState()
            cur_s = start_state
            time = 0
            while True:
                #self.clock.tick(10000)

                #old_a = self.selectAction2(Qtable)
                old_a = self.selectAction(Qtable,cur_s)
                self.objectMove()
                old_s = cur_s
                cur_s = self.getObservedState()
                r = self.getReward()
                if r == -100:
                    time = 0
                    Qtable.update(old_s, cur_s, old_a, r, 0.5, 0.5)
                    self.__init__()
                    continue
                    #time.sleep(1)
                else :
                    time += 1
                if time%50 == 0:
                    r = 100
                Qtable.update(old_s,cur_s,old_a,r,0.5,0.9)


    class Qlearning:
        def __init__(self, state_num, action_num,e):
            self.Q = [ State(action_num) for _ in range(state_num)]
            self.e = e
            #객체 생성하면서 상태,행동 0 으로 초기화됨
        def update(self,old_s,cur_s,old_a,r,learning_rate,discount_num):
            #print old_s
            self.Q[old_s].a[old_a] += learning_rate * (r + discount_num * max(self.Q[cur_s].a)-self.Q[old_s].a[old_a])

class State:
    def __init__(self, numAction):
        self.a = [0.0 for _ in range(numAction)]


Qtable = RL.Qlearning(100000,3,0.4)
game = RL.Game()
game.epoch(Qtable)








