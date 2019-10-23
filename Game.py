from World import *
from Snake import *
from Population import *
from Genome import *
import random
import NN
import pickle
import time
# import GA

class Game:
    def __init__(self):
        self.world = World(self)

        self.fps = 1
        self.mousePosition = None
        # time
        self.time = 0
        self.lastColisionCheck = 0
        self.lastGAcycle = 0
        self.lastSnakeKilled = 0
        # GA
        self.snakes = []
        self.snakeHistory = []
        self.isHumanPlayer = isHumanPlayer
        self.loadFromFile = loadFromFile
        self.training = training
        self.showBotView = showBotView
        self.population = Population()
    
    def init(self):
        # Spawn snakes
        try:
            if self.loadFromFile:
                brains = []
                filePath = "savedNeatBrains/1-" + str(numberOfBeams) + "-" + str(numberOfFoodSenses)
                with open(filePath + "/savedBrain.obj", 'rb') as file_brain:
                    brain = pickle.load(file_brain)
                if brain.size[0] != numberOfBeams + numberOfFoodSenses + numberOfSnakeSenses*2 + 1:
                    raise Exception

                for i in range(numberOfSnakes + self.isHumanPlayer):
                    brains.append(brain.Copy())

                self.SpawnSnakes(brains, firstSpawn=1)
            else:
                self.SpawnSnakes()  
        except:
            print("File not found, empty or not matching for current input vector, starting with random weights")
            self.SpawnSnakes()

        # Create human player
        if self.isHumanPlayer:
            self.snakes[0].aiControlled = False

        # Create population from ai Controlled snakes
        self.population.CreateGeneration(self.snakes[self.isHumanPlayer:]) 
        

    def Update(self, mousePos, fps):

       
        self.mousePosition = mousePos
        self.fps = max(fps, 1)
        self.time += 1000/self.fps   
        #  
        # start = time.time()  
        # Update snakes
        self.world.Update()
        for snake in self.snakes:
            snake.Update()
        
        # print(round((time.time() - start)*1000,3))

        # Check for collision
        if self.time - self.lastColisionCheck > 200: # check every X miliseconds
            self.CheckForCollisions()
            self.lastColisionCheck = self.time
        

        # GA cycle
        if self.training:
            if len(self.snakes) <= (noOfSnakesLimit + self.isHumanPlayer) or self.time - self.lastGAcycle > generationTimeLimit*1000:
                self.lastGAcycle = self.time
                genomes = self.population.GeneticCycle()
                del self.snakes[self.isHumanPlayer:] # delete previous snaked except the one who belongs to human player
                self.snakeHistory = [] # delete previous snaked except the one who belongs to human player
                self.SpawnSnakes(genomes)
                self.population.CreateGeneration(self.snakeHistory)
                self.world.RespawnFood()

                
    def SpawnSnakes(self, brains = None, firstSpawn = 0):
        # Create snakes
        if brains == None: # first spawn
            for region in random.sample(self.world.regions, numberOfSnakes + self.isHumanPlayer):
                inNodes = numberOfBeams + numberOfFoodSenses +  numberOfSnakeSenses*2 + 1
                outNodes = 2
                brain = Genome(inNodes, outNodes)
                brain.FullyConnect(self.population.innovations)
                tempSnake = Snake(self, region.position[0] + region.position[2]/2, region.position[1] + region.position[3]/2, brain)
                self.snakes.append(tempSnake)
                self.snakeHistory.append(tempSnake)
            if self.isHumanPlayer:
                self.snakeHistory.pop(0)
        else:
            i = 0
            for region in random.sample(self.world.regions, numberOfSnakes + firstSpawn):
                tempSnake = Snake(self, region.position[0] + region.position[2]/2, region.position[1] + region.position[3]/2, brains[i])
                self.snakes.append(tempSnake)
                self.snakeHistory.append(tempSnake)
                i += 1

    def CheckForCollisions(self):
        for snake in self.snakes:
            for otherSnake in self.snakes:
                if otherSnake == snake:
                    continue
                if otherSnake.position.distance_squared_to(snake.position) > (len(otherSnake.body)*otherSnake.radius*1.2)**2:
                    continue
                for part in otherSnake.body:
                    if snake.position.distance_squared_to(part) < (snake.radius + otherSnake.radius)**2:
                        snake.Die()
                        self.snakes.remove(snake)
                        break
            if snake.position.x - snake.radius < -self.world.width/2:
                self.killSnake(snake)
            if snake.position.x + snake.radius > self.world.width/2:
                self.killSnake(snake)
            if snake.position.y - snake.radius < -self.world.height/2:
                self.killSnake(snake)
            if snake.position.y + snake.radius > self.world.height/2:
                self.killSnake(snake)

    def killSnake(self, snake):
        snake.Die()
        try:
            self.snakes.remove(snake)
        except:
            pass
        
