#-*- coding: utf-8 -*

'''
자율운전 프로젝트
제작자 : 심형석
지도교수 : 김성우
알고리듬 : QLearnning
'''
# 자율 운전

# 행동(좌/우) 2개         조회전 +5거리, 우회전 +5거 가능

# 지각센서(레이더) 4개 3단계 20거리

# 상태 개수 : 4x4x4x4x2

# 보상 : 비충돌 +0.1, 충돌 -100

class state:
    def __init__(self, num_action):
        self.Q_value = [0 for i in range(num_action)]

class Q_Table:
    def __init__(self, num_state, num_action):
        self.states = []
        for i in range(num_state):
            self.states.append(state(num_action))



class Reward:
    pass

class World:
    def __init__(self):
        pass

class Agent:
    def __init__(self):
        self.num_state = 256
        self.num_each_state_action = 2
        self.Knowledge = Q_Table(self.num_state,self.num_each_state_action)

    def getWorld(self):
        return 0

    def getReward(self):
        return 0,0

    def Perception(self):
        state_number = self.getWorld()
        reward, done = self.getReward()
        return  (state_number, reward, done)


    def EEselectAction(self,now_state):
        a = argmax(Q(s, a) + random_values / (i + 1))

        self.Knowledge.states[now_state].Q_value
    def Learning(self,start_state):
        now_state = start_state
        new_state = 0
        new_reward = 0
        terminal = False

        while not terminal:

            selectAction()
            new_state,new_reward,terminal = self.Perception()
        pass

world = World()
agent = Agent()








class Agent:
    def __init__(self):
        state = State()
        action = Action()

        percept = Perception()
        knowledge = Knowledge()

class QLearning:
    def __init__(self):
        agent = Agent()

    def update(self):
        pass

    def train(self):
        pass

