import numpy as np

HIT = 1
STAND = 0
class BlackJackSolution:

    def __init__(self, lr=0.1, exp_rate=0.3):
        self.Q_Values = {}
        for i in range(12, 22): #Card totals, beginning with 12
            for j in range(1, 11): #Choosing card
                for k in [True, False]: #Usable ace or not
                    self.Q_Values[(i, j, k)] = {}
                    for a in [1, 0]:
                        if (i == 21) and (a == 0):
                            self.Q_Values[(i, j, k)][a] = 1
                        else:
                            self.Q_Values[(i, j, k)][a] = 0

        self.state_action = []
        self.state = (0, 0, False)  # initial state
        self.actions = [HIT, STAND] 
        self.end = False
        self.lr = lr #The learning rate of algorithm
        self.exp_rate = exp_rate #The expected probability of a state

    # give card
    @staticmethod #Enables the use of class in functions
    def newCard():
        cards = [1,2,3,4,5,6,7,8,9,10,10,10,10] #Lists cards
        return np.random.choice(cards)

    def dealerPolicy(self, current_value, usable_ace, is_end):
        if current_value > 21:
            if usable_ace:
                current_value -= 10
                usable_ace = False
            else:
                return current_value, usable_ace, True
        # HIT17
        if current_value >= 17:
            return current_value, usable_ace, True
        else:
            card = self.newCard()
            if card == 1:
                if current_value <= 10:
                    return current_value + 11, True, False
                return current_value + 1, usable_ace, False
            else:
                return current_value + card, usable_ace, False

    def Action(self):
        current_value = self.state[0]
        if current_value <= 11: #Always hit if total less than 12
            return 1

        if np.random.uniform(0, 1) <= self.exp_rate:
            action = np.random.choice(self.actions)
        else:
            #Greedy
            v = -999
            action = 0
            for a in self.Q_Values[self.state]:
                if self.Q_Values[self.state][a] > v: #Actions get more greedy
                    action = a
                    v = self.Q_Values[self.state][a]
        return action

    def nextState(self, action):
        current_value = self.state[0]
        show_card = self.state[1]
        usable_ace = self.state[2]

        if action: #When action = HIT
            card = self.newCard()
            if card == 1:
                if current_value <= 10:
                    current_value += 11
                    usable_ace = True
                else:
                    current_value += 1
            else:
                current_value += card
        else:
            self.end = True
            return (current_value, show_card, usable_ace)

        if current_value > 21:
            if usable_ace:
                current_value -= 10
                usable_ace = False
            else:
                self.end = True
                return (current_value, show_card, usable_ace)

        return (current_value, show_card, usable_ace)

    def winner(self, p_value, d_value):
        #PlayerWin = 1
        #Draw = 0
        #DealerWin = -1
        winner = 0
        if p_value > 21:
            if d_value > 21:
                # draw
                winner = 0
            else:
                winner = -1
        else:
            if d_value > 21:
                winner = 1
            else:
                if p_value < d_value:
                    winner = -1
                elif p_value > d_value:
                    winner = 1
                else:
                    # draw
                    winner = 0
        return winner

    def stateReward(self, p_value, d_value):
        reward = self.winner(p_value, d_value)
        # Starting from the last state
        for s in reversed(self.state_action):
            state, action = s[0], s[1]
            reward = self.Q_Values[state][action] + self.lr*(reward - self.Q_Values[state][action])
            self.Q_Values[state][action] = round(reward, 3) # 3dp

    def initial(self):
        self.state_action = []
        self.state = (0, 0, False)  # Initial state
        self.end = False

    def deal2cards(self, show=False):
        # return value after 2 cards and usable ace
        value, usable_ace = 0, False
        cards = [self.newCard(), self.newCard()]
        if 1 in cards:
            value = sum(cards) + 10
            usable_ace = True
        else:
            value = sum(cards)
            usable_ace = False

        if show:
            return value, usable_ace, cards[0]
        else:
            return value, usable_ace

    def play(self, rounds=1000):
        for i in range(rounds):
            if i % 10000 == 0:
                print("round", i)
                

            # give 2 cards
            d_value, d_usable_ace, show_card = self.deal2cards(show=True)
            p_value, p_usable_ace = self.deal2cards(show=False)

            self.state = (p_value, show_card, p_usable_ace)
            #print("init", self.state)

            # judge winner after 2 cards
            if p_value == 21 or d_value == 21:
                # game end
                next
            else:
                while True:
                    action = self.Action()  # state -> action
                    if self.state[0] >= 12:
                        state_action_pair = [self.state, action]
                        self.state_action.append(state_action_pair)
                    # update next state
                    self.state = self.nextState(action)
                    if self.end:
                        break

                        # dealer's turn
                is_end = False
                while not is_end:
                    d_value, d_usable_ace, is_end = self.dealerPolicy(d_value, d_usable_ace, is_end)

                # judge winner
                # give reward and update Q value
                p_value = self.state[0]
                #print("player value {} | dealer value {}".format(p_value, d_value))
                self.stateReward(p_value, d_value)
  
            self.initial()

    def savePolicy(self):
        Holder = self.Q_Values
        return Holder

    def loadPolicy(self, Holder):
        self.Q_Values = Holder
    

    # AI vs Dealer
    def playWithDealer(self, Holder, rounds=1000):
        self.initial()
        self.loadPolicy(Holder)
        self.exp_rate = 0

        result = np.zeros(3)  # player [win, draw, lose]
        for _ in range(rounds):
            # hit 2 cards each
            # give 2 cards
            d_value, d_usable_ace, show_card = self.deal2cards(show=True)
            p_value, p_usable_ace = self.deal2cards(show=False)

            self.state = (p_value, show_card, p_usable_ace)

            # judge winner after 2 cards
            if p_value == 21 or d_value == 21:
                if p_value == d_value:
                    result[1] += 1
                elif p_value > d_value:
                    result[0] += 1
                else:
                    result[2] += 1
            else:
                # player's turn
                while True:
                    action = self.Action()
                    # update next state
                    self.state = self.nextState(action)
                    if self.end:
                        break

                        # dealer's turn
                is_end = False
                while not is_end:
                    d_value, d_usable_ace, is_end = self.dealerPolicy(d_value, d_usable_ace, is_end)

                # judge
                p_value = self.state[0]
                w = self.winner(p_value, d_value)
                if w == 1:
                    result[0] += 1
                elif w == 0:
                    result[1] += 1
                else:
                    result[2] += 1
            self.initial()
        return result


if __name__ == "__main__":
    # training
    b = BlackJackSolution()
    b.play(100000)
    print("Done training")

    # save policy
    Holder = b.savePolicy()

    # play
    result = b.playWithDealer(Holder, rounds=10000)
    print(result)
