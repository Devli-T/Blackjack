import random
import numpy as np   
import matplotlib.pyplot as plt
#from mpl_toolkits.mplot3d import mplot3d

#global variables
HIT = 1
STICK = 0
ACE = 1
NOACE = 0
WIN = 1
DRAW = 0
LOSE = -1

STATE_DIMS=(22, 11, 2) # player hand value, dealer card value, usable ace 
ACTION_DIMS = (2,)     # hit or stick

def randomExploringStart():
  state = [[random.randint(1, 10), random.randint(1, 10)],
           [random.randint(1, 10), random.randint(1, 10)]]
  actionA = random.randint(0, 1)
  actionB = random.randint(0, 1)
  return state, actionA, actionB

def dealCard(state):
  cards = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 10, 10, 10]
  newcard = random.choice(cards)
  state.append(newcard)
  return state


def playerState(state):
  totalA = 0
  totalB = 0
  aceA = 0
  aceB = 0
  for x in state[0]:
    totalA += x
  for y in state[1]:
    totalB += y
  if 1 in state[0]:
    if totalA <= 11:
      totalA += 10
      aceA = 1
  if 1 in state[1]:
    if totalB <= 11:
      totalB += 10
      aceB = 1
  stateA = [totalA, state[1][0], aceA]
  stateB = [totalB, state[0][0], aceB]
  return stateA, stateB
            

def hit(state, player):
  if player == 'A':
    dealCard(state[0])
  elif player == 'B':
    dealCard(state[1])
  return state


def finish(state):
  #checkwinner
  stateA, stateB = playerState(state)
  totalA = stateA[0]
  totalB = stateB[0]

  if totalA > 21:
    rewardA = LOSE
  elif totalB > 21:
    rewardA = WIN
  elif totalA > totalB:
    rewardA = WIN
  elif totalA < totalB:
    rewardA = LOSE
  elif totalA == totalB:
    rewardA = DRAW
  return rewardA


def player(state, player, action, policy, q):
  stateA, stateB = playerState(state)
  
  episodelist = []
  reward = 'pending'

  while reward == 'pending':
    if player == 'A':
      episodelist.append([stateA.copy(), action])
    elif player == 'B':
      episodelist.append([stateB.copy(), action])

    if action == HIT:
      if player == 'A':
        state[0] = dealCard(state[0])
        stateA, stateB = playerState(state)
      elif player == 'B':
        state[1] = dealCard(state[1])
        stateA, stateB = playerState(state)

    elif action == STICK:
      return episodelist, state
    
    if player == 'A':
      if stateA[0] > 21:
        return episodelist, state
    elif player == 'B':
      if stateB[0] > 21:
        return episodelist, state

    if player == 'A':
      action = policy(q, stateA)
    elif player == 'B':
      action = policy(q, stateB)     


def episode(policy, qA, qB):
  state, actionA, actionB = randomExploringStart()

  episodelistA, state = player(state, 'A', actionA,greedy_policy_action, qA)
  stateA, stateB = playerState(state)
  if stateA[0] > 21:
    return episodelistA, LOSE, [], WIN
  
  episodelistB, state = player(state, 'B', actionB, greedy_policy_action, qB)
  stateA, stateB = playerState(state)
  if stateB[0] > 21:
    return episodelistA, WIN, episodelistB, LOSE
  
  rewardA = finish(state)
  if rewardA == WIN:
    rewardB = LOSE
  elif rewardA == DRAW:
    rewardB = DRAW
  elif rewardA == LOSE:
    rewardB = WIN
  
  return episodelistA, rewardA, episodelistB, rewardB


def create_empty_q():
  q = np.zeros((*STATE_DIMS, *ACTION_DIMS))
  return q


def greedy_policy_action(q, state):
  sl = q[state[0], state[1], state[2]]
  action = sl.argmax()
  return action


def update_q_from_episode(q, returns, episode, reward):
  for pair in episode:
    pairlist = pair[0]
    pairlist.append(pair[1])
    pairlist = tuple(pairlist)
  
    if pairlist not in returns:
      returns[pairlist] = []
    returns[pairlist].append(reward)

    q[pairlist[0], pairlist[1], pairlist[2], pairlist[3]] = np.mean(returns[pairlist]) 
    return q


returns1 = dict()
returns2 = dict()
q1 = create_empty_q()
q2 = create_empty_q()


#player1 always goes first, player2 always goes second
for i in range(100000): 
  episodelistA, rewardA, episodelistB, rewardB = episode(greedy_policy_action, q1, q2)

  q1 = update_q_from_episode(q1, returns1, episodelistA, rewardA)
  if episodelistB != []:
    q2 = update_q_from_episode(q2, returns2, episodelistB, rewardB)

print(q1)


#player1 goes first half the time, player2 goes first half the time
'''
for i in range(100000):
  if i % 2 == 0:
    episodelistA, rewardA, episodelistB, rewardB = episode(greedy_policy_action, q1, q2)

    q1 = update_q_from_episode(q1, returns1, episodelistA, rewardA)
    if episodelistB != []:
      q2 = update_q_from_episode(q2, returns2, episodelistB, rewardB)
  else:
    episodelistA, rewardA, episodelistB, rewardB = episode(greedy_policy_action, q2, q1)

    q2 = update_q_from_episode(q2, returns2, episodelistA, rewardA)
    if episodelistB != []:
      q1 = update_q_from_episode(q1, returns1, episodelistB, rewardB)
'''

def plot_blackjack(q, ax1, ax2):
  playersum = np.arange(12, 21 + 1)
  dealercard = np.arange(1, 10 + 1)         
  useableace = np.array([NOACE, ACE])
  state_values = np.zeros((len(playersum), len(dealercard), len(useableace)))
  for i, player in enumerate(playersum):
    for j, dealer in enumerate(dealercard):
      for k, ace in enumerate(useableace):
        bestactionindex = q[player, dealer, ace].argmax()
        state_values[i, j, k] = q[player, dealer, ace, bestactionindex]
  X, Y = np.meshgrid(playersum, dealercard)
  ax1.plot_wireframe(X, Y, state_values[:, :, 0])   
  ax2.plot_wireframe(X, Y, state_values[:, :, 1])
  for ax in ax1, ax2:    
    ax.set_zlim(-1, 1)
    ax.set_ylabel('player sum')
    ax.set_xlabel('opponent card')
    ax.set_zlabel('state-value')
  plt.show()


fig, axes = plt.subplots(nrows=2, figsize=(5, 8),subplot_kw={'projection': '3d'})
axes[0].set_title('state-value distribution w/o usable ace')
axes[1].set_title('state-value distribution w/ usable ace')

plot_blackjack(q1, axes[1], axes[0])
#plot_blackjack(q2, axes[1], axes[0])
