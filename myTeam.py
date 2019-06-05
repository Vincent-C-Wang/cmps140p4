# baselineTeam.py
# ---------------
# Licensing Information: Please do not distribute or publish solutions to this
# project. You are free to use and extend these projects for educational
# purposes. The Pacman AI projects were developed at UC Berkeley, primarily by
# John DeNero (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# For more info, see http://inst.eecs.berkeley.edu/~cs188/sp09/pacman.html

from captureAgents import CaptureAgent
import distanceCalculator
import random, time, util
from game import Directions
import game
from util import nearestPoint
import numpy as np


from game import Agent
import distanceCalculator
from util import nearestPoint
import util


#################
# Team creation #
#################


def createTeam(firstIndex, secondIndex, isRed,
               first = 'OffensiveReflexAgent', second = 'DefensiveReflexAgent'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):

  


  """
  A base class for reflex agents that chooses score-maximizing actions
  """
  def chooseAction(self, gameState):
    """
    Picks among the actions with the highest Q(s,a).
    """

    ####print "chooseAction Called"

    #self.lastEatenFood = None


    actions = gameState.getLegalActions(self.index)

    ##print "\nNEW ACTION\n--------"

    # You can profile your evaluation time by uncommenting these lines
    # start = time.time()
    values = [self.evaluate(gameState, a) for a in actions]
    # ###print 'eval time for agent %d: %.4f' % (self.index, time.time() - start)

    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]

    

    return random.choice(bestActions)

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def evaluate(self, gameState, action):
    """
    Computes a linear combination of features and feature weights
    """
    features = self.getFeatures(gameState, action)
    ####print "features ", features
    weights = self.getWeights(gameState, action)
    ####print "weights ", weights
    return features * weights


  def getFeatures(self, gameState, action):
    """
    Returns a counter of features for the state
    """
    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)
    return features

  def getWeights(self, gameState, action):
    """
    Normally, weights do not depend on the gamestate.  They can be either
    a counter or a dictionary.
    """
    return {'successorScore': 1.0}



class OffensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that seeks food. This is an agent
  we give you to get an idea of what an offensive agent might look like,
  but it is by no means the best or only way to build an offensive agent.
  """

  def getFeatures(self, gameState, action):

    features = util.Counter()
    successor = self.getSuccessor(gameState, action)
    features['successorScore'] = self.getScore(successor)

    # Compute distance to the nearest food
    foodList = self.getFood(successor).asList()#+self.getCapsules(successor)
    #print "all food ", foodList
    #foodList = foodList+pelletsList

    if len(foodList) > 0: # This should always be True,  but better safe than sorry
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in foodList])
   
      features['distanceToFood'] = minDistance-10

    
 




    ####print features
    return features

  def getWeights(self, gameState, action):
    return {'successorScore': 100, 'distanceToFood': -1, 'invaderDistance':1}

    #{'numGhosts': 1000, 'onDefense': 100, 'invaderDistance': 10, 'stop': -100, 'reverse': -2}





class DefensiveReflexAgent(ReflexCaptureAgent):
  """
  A reflex agent that keeps its side Pacman-free. Again,
  this is to give you an idea of what a defensive agent
  could be like.  It is not the best or only way to make
  such an agent.
  """


  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)
    """

    # stuff
    self.treeDepth = 4
    self.oldFood = []
    self.lastEatenFood = None
    self.i = 0



    #oldFood
    self.oldFood = self.getFoodYouAreDefending(gameState)


    self.red = gameState.isOnRedTeam(self.index)
    self.distancer = distanceCalculator.Distancer(gameState.data.layout)

    # comment this out to forgo maze distance computation and use manhattan distances
    self.distancer.getMazeDistances()



    

    
    # FIND PATROL POINTS



    x = gameState.data.layout.width/2-8
    #print "WIDTH ", x+4

    y1 = gameState.data.layout.height-4
    y2 = 0+4



    point1 = (x,y2)
    point2 = (x,y1)
    topPoints = []
    botPoints = []
    for i in range(0,6):
      xv = x+i
      if not gameState.data.layout.walls[xv][y1]:

        newBP = (xv, y1)
        botPoints.append(newBP)
      else:
        newBP = (xv, y1)
        #print newBP, " in wall"

      if not gameState.data.layout.walls[xv][y2]:
        newTP = (xv, y2)
        topPoints.append(newTP)
      else:
        newTP = (xv, y2)
        #print newTP, " in wall"





    # FIND PATROL POINTS WITH THE SHORTEST PATH
    bestTP = topPoints[0]
    bestBP = botPoints[0]

    bestPath = self.getMazeDistance(bestTP,bestBP)
    for tp in topPoints:
      bp = min(botPoints, key=lambda p: self.getMazeDistance(tp, p))
      tempPath = self.getMazeDistance(tp, bp)
      if (tempPath < bestPath):
        bestTP = tp
        bestBP = bp
        bestPath = tempPath

    #print "THE REAL BEST POINTS: ", bestBP, " ", bestTP, " ", bestPath

    self.patrolPoints = [bestTP,bestBP]






    import __main__
    if '_display' in dir(__main__):
      self.display = __main__._display






  


  def getFeatures(self, gameState, action):

    features = util.Counter()
    # successor states for all agents
    successor = self.getSuccessor(gameState, action)

    

    # your successor state
    myState = successor.getAgentState(self.index)
    # your pos
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [successor.getAgentState(i) for i in self.getOpponents(successor)]

    # find invadors on other team
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)


    allEnemies = [a for a in enemies if a.getPosition() != None]

    ##print "allEnemies ", allEnemies

    if allEnemies:
      ##print "I SEE U ", allEnemies
      pass

    
    ###print "invaders ", len(invaders)

    dists = []
    #lastEatenFood = None

    


    # if there are invaders
    if len(invaders) > 0:
      #get the maze distance to each one
      ###print self.scaredTimer

    


      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      closestPac = min(dists)



      if myState.scaredTimer:
        ###print myState.scaredTimer
        ###print gameState
        pass


      if myState.scaredTimer != 0 and myState.scaredTimer <= 25 and closestPac <2:
        #features['invaderDistance'] = 10
        pass
      else:
        features['invaderDistance'] = min(dists)
      self.lastEatenFood = None
      

      ###print "features['invaderDistance'] chase ", features['invaderDistance']
    
    # if there aren't any invaders
    else:
      


      #check yo food buddy
      oldFoodList = self.oldFood.asList()
      newFoodList = self.getFoodYouAreDefending(gameState).asList()

      # ##print "old"
      # ##print oldFoodList
      # ##print "new"
      # ##print newFoodList




      #if any piece has been eaten 
      if oldFoodList != newFoodList:
        eatenFoodList = list(set(oldFoodList) - set(newFoodList))
        self.lastEatenFood = eatenFoodList[0]

        self.oldFood = self.getFoodYouAreDefending(gameState)

      #move to the last eaten food
      if self.lastEatenFood:
        #print "TO FOOD"
        #print self.lastEatenFood


       



        distanceToFood = self.getMazeDistance(myPos, self.lastEatenFood)


        features['invaderDistance'] = distanceToFood

        # remove the last eaten food after you've been to it and bug fixing
        if myPos == self.lastEatenFood or self.lastEatenFood[0] >= gameState.data.layout.width/2-2 or gameState.data.layout.walls[self.lastEatenFood[0]][self.lastEatenFood[1]]:
          self.lastEatenFood = None

      #patrol behavior
      else:
        #print "PATROL"
        #print self.patrolPoints


        p = self.patrolPoints[self.i]





        if myPos == p:
          self.i+=1
          if self.i>=len(self.patrolPoints):
            self.i = 0

        distanceToPoint = self.getMazeDistance(myPos, p)

        features['invaderDistance'] = distanceToPoint




    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1





    return features

  def getWeights(self, gameState, action):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}


class OffensiveAgent(ReflexCaptureAgent):

  def chooseAction(self, gameState):
    actions = gameState.getLegalActions(self.index)
    
    agentIndexes = []
    agentIndexes.append(self.index)
    # code to fill list with currently seen enemies
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    allEnemies = [a for a in enemies if a.getPosition() != None]
    
    for i in self.getOpponents(gameState):
      if gameState.getAgentState(i) in allEnemies: 
        agentIndexes.append(i)

    #(score, action)
    values = [(self.expectimax( 0, 0, gameState.generateSuccessor(self.index, a) , agentIndexes), a) for a in actions]
    maxValue = max(values)[0]
    bestActions = []
    for action in values:
      if action[0] ==maxValue:
        bestActions.append(action[1])
    return random.choice(bestActions)

  def expectimax(self, pos , depth, gameState, *agentIndexes):
    #python puts the list in a tuple everytime so we unpack it here
    if (isinstance(agentIndexes, tuple)):
      agentIndexes = agentIndexes[0]

    length = len(agentIndexes)
    print "pos" , pos
    print agentIndexes
    print length

    if pos == length:
      pos =0 
      depth =depth +1
    print "new pos" ,pos


    actions = gameState.getLegalActions(agentIndexes[pos])
    scores=[]

    if depth == 5 or not actions:
      if(agentIndexes in self.getOpponents(gameState)):
        print "enemy evaluation"
        return self.enemyEvaluation(gameState, agentIndexes[pos])
      else:
        print"self evaluation"
        return self.maxevaluation(gameState)

    for a in actions:
      successor = gameState.generateSuccessor(agentIndexes[pos], a)
      scores.append(self.expectimax(pos+1, depth, successor, agentIndexes))

    if(self.index in self.getOpponents(gameState)):
      return max(scores)
    return sum(scores)


  #simple eval assumng reflexive enemy trying to close distance
  def enemyEvaluation(self, gameState, enemyIndex):
   
    features = self.getFeatures(gameState, enemyIndex)
    weights = self.getWeights(gameState, enemyIndex)
    return features * weights
    """
    prevState = getPreviousObservation(self.index)
    State = getCurrentObservation(self.index)
    prevPos = prevState.getAgentState(enemyIndex).getPosition()
    enemyPos = State.getAgentState(enemyIndex).getPosition()
    targetPos = gameState.getAgentState(self.index).getPosition()
    prevDist = self.getMazeDistance(prevPos, targetPos)
    curDist = self.getMazeDistance(enemyPos , targetPos)
    if prevDist > curDist:
      return -1
    return 1
  """

  #edit to not use next successor or actions
  #reworked baseline agent code to model enemy movement
  def getFeatures(self, gameState, enemyIndex):
    features = util.Counter()
    myState = gameState.getAgentState(enemyIndex)
    myPos = myState.getPosition()

    # Computes whether we're on defense (1) or offense (0)
    features['onDefense'] = 1
    if myState.isPacman: features['onDefense'] = 0

    # Computes distance to invaders we can see
    enemies = [gameState.getAgentState(i) for i in self.getTeam(gameState)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    features['numInvaders'] = len(invaders)
    if len(invaders) > 0:
      dists = [self.getMazeDistance(myPos, a.getPosition()) for a in invaders]
      features['invaderDistance'] = min(dists)

    if action == Directions.STOP: features['stop'] = 1
    rev = Directions.REVERSE[gameState.getAgentState(self.index).configuration.direction]
    if action == rev: features['reverse'] = 1

    return features

  def getWeights(self, gameState, enemyIndex):
    return {'numInvaders': -1000, 'onDefense': 100, 'invaderDistance': -10, 'stop': -100, 'reverse': -2}


  #modify this to not suck
  def maxevaluation(self, gameState):

    
    myPos = gameState.getAgentState(self.index).getPosition()
    foodList = self.getFood(gameState).asList()
    minFoodDistance = min([self.getMazeDistance(myPos, food) for food in foodList])


    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    allEnemies = [a for a in enemies if a.getPosition() != None]
    if allEnemies:
      minEnemyDist = min([self.getMazeDistance(myPos, b.getPosition()) for b in allEnemies])
      return 1/minFoodDistance - 1/minEnemyDist
    return minFoodDistance


