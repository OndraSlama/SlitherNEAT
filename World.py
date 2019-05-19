from Constants import *
import random
import pygame.math as gameMath
class World:
    def __init__(self, game):
        self.game = game
        self.width = worldWidth
        self.height = worldWidth
        self.food = []
        self.regions = []
        self.lastFoodCheck = 0

        xRegions = self.width//regionSize
        yRegions = self.height//regionSize

        for xi in range(xRegions):
            for yi in range(yRegions):
                regionWidth = self.width/xRegions
                regionHeight = self.height/yRegions
                regionRect = [xi*regionWidth - self.width/2, yi*regionHeight  - self.height/2, regionWidth, regionHeight]
                self.regions.append(Region(self, regionRect))

    def Update(self):
        if self.game.time - self.lastFoodCheck > resetFoodInterval*1000:
            self.lastFoodCheck = self.game.time
            for region in self.regions:
                region.CheckFood()

    def RespawnFood(self):
        self.food = []
        for region in self.regions:
            region.food = []
            region.CreateFood(random.randrange(round(foodInRegion*0.8), round(foodInRegion*1.2), 1))

    def DropFood(self, x, y, nutritions):
        for region in self.regions:            
            if region.isInRegion(x, y, 0):
                food = Food(region, x, y, nutritions)
                self.food.append(food)  
                region.food.append(food)              

class Food:
    def __init__(self, region, x, y, nut):
        self.region = region
        self.nutritions = nut
        self.position = gameMath.Vector2(x, y)
        

class Region:
    def __init__(self, world, position):
        self.world = world 
        self.position = position
        self.food = []
        self.CreateFood(random.randrange(round(foodInRegion*0.8), round(foodInRegion*1.2), 1))    
    
    def CreateFood(self, noOfFood):
        for i in range(noOfFood):
            foodXPos = random.randrange(round(self.position[0] * 100), round((self.position[0] + self.position[2])*100), 1)/100
            foodYPos = random.randrange(round(self.position[1] * 100), round((self.position[1] + self.position[3])*100), 1)/100
            food = Food(self, foodXPos, foodYPos, random.randrange(round(foodNutritions*0.5), round(foodNutritions*1.5), 1))
            self.food.append(food)
            self.world.food.append(food)

    def CheckFood(self):
        if len(self.food) < foodInRegion*0.8:
            self.CreateFood(random.randrange(1, round(foodInRegion*0.4), 1))

    def isInRegion(self, x, y, rad):
        if x + rad < self.position[0]: return False
        if x - rad > self.position[0] + self.position[2]: return False
        if y + rad < self.position[1]: return False
        if y - rad > self.position[1] + self.position[3]: return False
        return True

