from Constants import *
import random
import pygame.math as gameMath
import math
import NN
import time

class Snake:
    def __init__(self, game, x, y, brain):
        self.game = game
        self.aiControlled = True
        self.brain = brain
        self.fitness = 0

        self.position = gameMath.Vector2(x,y)
        self.velocity = gameMath.Vector2(1, 0)
        self.sprinting = False
        self.speed = snakeSpeed
        self.length = snakeInitialLength
        self.traveled = 0
        self.saturation = snakeInitialLength
        self.newPartCost = 20
        self.body = []
        self.radius = 1
        self.color = [255, 0, 0]

        self.lastEatCheck = 0
        self.lastEaten = game.time
        self.lastFoodDropped = 0

        self.beamLength = beamLength
        self.beamAngle = sideBeamAngle
        self.senseLenght = senseLength

        self.beamEndPoints = []
        self.intersectionPoints = []
        self.sensedFoodPos = []
        self.sensedSnakes = []

        self.body.append(gameMath.Vector2(x,y))

        for i in range(numberOfBeams):
            self.beamEndPoints.append(gameMath.Vector2(0,0))
            self.intersectionPoints.append(gameMath.Vector2(0,0))
        
        for i in range(numberOfFoodSenses):
            self.sensedFoodPos.append(gameMath.Vector2(0,0))

        for i in range(numberOfSnakeSenses):
            self.sensedSnakes.append(gameMath.Vector2(0,0))

    def Update(self):
        # start = time.time()  

        # Get what snake can see
        self.GetSensorData() # TODO: most demanding function - optimize!
        
        # Controll (brain of the snake)
        rotateAngle = 0
        if self.aiControlled:
            inputList = self.SensorDataToInput()
            ouputList = self.brain.Forward(inputList)

            rotateAngle = self.ClampAngle((ouputList[0] - 0.5)*2*(turningAngle/self.game.fps/self.radius))
            if ouputList[1] > 0.5:
                self.sprinting = True
            else:
                self.sprinting = False
        else:
            self.SensorDataToInput()
            differenceAngle = self.velocity.angle_to(self.game.mousePosition - self.position)
            rotateAngle = self.ClampAngle(differenceAngle)               

        # Sprint behaviour
        if self.sprinting and self.length > 100:
            self.speed = snakeSpeed * 2.5
        else:
            self.speed = snakeSpeed
            self.sprinting = False        
        
        # Move the snake
        self.Move(rotateAngle)

        # Eat (only sometimes for better performance)
        if self.game.time - self.lastEatCheck > 50: #eat every X miliseconds
            self.Eat()
            self.lastEatCheck = self.game.time

        # kill snake if too hungry (in training)
        if self.game.training and self.game.time - self.lastEaten > (hungerTimeLimit + popHungerTimeScale * self.game.population.generation)*1000:
            if self.aiControlled and self.game.time - self.game.lastSnakeKilled > 500:
                self.game.killSnake(self)      
                self.game.lastSnakeKilled = self.game.time       
                return

        # Grow or shring the snake (based on current saturation)
        self.UpdateLength()
        # print(round((time.time() - start)*1000,3))         

    def Move(self, rotateAngle):   
        # Update velocity
        self.velocity = self.velocity.rotate(rotateAngle)
        self.velocity = self.velocity.normalize()*self.speed

        self.position += self.velocity/self.game.fps
        self.traveled += self.speed/self.game.fps
        self.Join()

        if self.sprinting:
            self.saturation -= sprintCost/self.game.fps
            self.length -= sprintCost/self.game.fps
            if self.game.time - self.lastFoodDropped > 250:
                self.game.world.DropFood(self.body[-1].x, self.body[-1].y, sprintCost/4)
                self.lastFoodDropped = self.game.time
        else:
                self.lastFoodDropped = self.game.time

        
    def Join(self):
        distanceBetweenParts = self.radius*.9
        for i in range(len(self.body)):
            velocity = None

            if i == 0:
                previous = self.position                
            else:
                previous = self.body[i-1]             

            offset = previous - self.body[i]
            offset.scale_to_length(distanceBetweenParts)
            self.body[i] = previous - offset

    def GetSensorData(self):
        self.beamLength = beamLength * self.radius
        self.senseLenght = senseLength*self.radius

        # sight        
        for i in range(numberOfBeams):
            lineVector = self.velocity.normalize().rotate(sideBeamAngle * (i - (numberOfBeams - 1)/2))
            self.beamEndPoints[i] = self.position + lineVector*self.beamLength
            self.intersectionPoints[i] = self.position + lineVector*self.beamLength

        # Check for boundaries with sight
        if abs(self.position.x) > self.game.world.width/2 - self.beamLength or abs(self.position.y) > self.game.world.height/2 - self.beamLength:            
            boundaries = []
            boundaries.append(gameMath.Vector2(-self.game.world.width/2, -self.game.world.height/2))
            boundaries.append(gameMath.Vector2(self.game.world.width/2, -self.game.world.height/2))
            boundaries.append(gameMath.Vector2(self.game.world.width/2, self.game.world.height/2))
            boundaries.append(gameMath.Vector2(-self.game.world.width/2, self.game.world.height/2))

            for i in range(len(self.beamEndPoints)):
                for j in range(4):
                    intersestion = self.FindIntersection(self.position, self.beamEndPoints[i], boundaries[j-1], boundaries[j])
                    if intersestion is not None:
                        break
                if intersestion is not None:        
                    self.intersectionPoints[i] = intersestion

        # Check for other snakes with sight
        for otherSnake in self.game.snakes:
            if otherSnake == self:
                continue
            if otherSnake.position.distance_squared_to(self.position) > (len(otherSnake.body)*otherSnake.radius*1.2 + self.beamLength)**2:
                continue
            for part in otherSnake.body:
                for i in range(len(self.beamEndPoints)):
                    Q = part                          # Centre of circle
                    r = otherSnake.radius             # Radius of circle
                    P1 = self.position                # Start of line segment
                    V = self.beamEndPoints[i] - P1    # Vector along line segment

                    a = V.dot(V)
                    b = 2 * V.dot(P1 - Q)
                    c = P1.dot(P1) + Q.dot(Q) - 2 * P1.dot(Q) - r**2

                    disc = b**2 - 4 * a * c
                    if disc < 0:
                        continue

                    sqrt_disc = math.sqrt(disc)
                    t1 = (-b + sqrt_disc) / (2 * a)
                    t2 = (-b - sqrt_disc) / (2 * a)

                    if not (0 <= t1 <= 1 or 0 <= t2 <= 1):
                        continue

                    t = min(t1, t2)
                    self.intersectionPoints[i] = P1 + t * V    


        # chek for snakes with sense
        snakesClose = []
        for snake in self.game.snakes:
            if snake == self: continue                
            if snake.position.distance_squared_to(self.position) < self.senseLenght**2:
                snakesClose.append(snake.position)
        for i in range(numberOfSnakeSenses):
            if i < len(snakesClose):
                self.sensedSnakes[i] = gameMath.Vector2(snakesClose[i].x, snakesClose[i].y)
            else:
                self.sensedSnakes[i] = gameMath.Vector2(self.position.x, self.position.y)

        # sense food
        # start = time.time()  
        foodClose = []
        for region in self.game.world.regions:
            if region.isInRegion(self.position.x, self.position.y, self.senseLenght):
                for food in region.food:
                    if food.position.distance_squared_to(self.position) < self.senseLenght**2:
                        foodClose.append(food)
        foodClose.sort(key=lambda x: x.nutritions, reverse=True)
        for i in range(numberOfFoodSenses):
            if i < len(foodClose):
                self.sensedFoodPos[i] = gameMath.Vector2(foodClose[i].position.x, foodClose[i].position.y)
            else:
                self.sensedFoodPos[i] = gameMath.Vector2(self.position.x, self.position.y)
        # print(round((time.time() - start)*1000,3))

    def SensorDataToInput(self):
        # input list: fist are normalized distances from beams: 0 - 1 (if cant see anything -> -1) then distances to best food with angles to them from current velocity vector
        inputList = []

        inputList.append(self.length/5000)

        for i in range(len(self.intersectionPoints)):            
            # Append the normalized distance to intesection
            if self.intersectionPoints[i] == self.beamEndPoints[i]:
                inputList.append(1)
            else:
                distSquared = self.position.distance_squared_to(self.intersectionPoints[i])
                inputList.append(distSquared/self.beamLength**2)
        
        for foodPos in self.sensedFoodPos:
            # Append the normalized distance and angle to food
            if foodPos == self.position:
                # inputList.append(-1) # distance
                inputList.append(0) # angle
            else:
                dist = self.position.distance_to(foodPos)
                angle = self.velocity.angle_to(foodPos - self.position)
                if angle  > 180: angle -= 360
                if angle  < -180: angle += 360

                # inputList.append(dist/self.senseLenght) # distance
                inputList.append(angle/180) # angle
                # if not self.aiControlled:
                #     print(angle/180)

        for snakePos in self.sensedSnakes:
            # Append the normalized distance and angle to food
            if snakePos == self.position:
                inputList.append(1) # distance
                inputList.append(0) # angle
            else:
                dist = self.position.distance_to(snakePos)
                angle = self.velocity.angle_to(snakePos - self.position)
                if angle  > 180: angle -= 360
                if angle  < -180: angle += 360

                inputList.append(dist/self.senseLenght) # distance
                inputList.append(angle/180) # angle
                # if not self.aiControlled:
                #     print(angle/180)

        return inputList



    def FindIntersection(self, p0, p1, p2, p3 ) :

        s10_x = p1.x - p0.x
        s10_y = p1.y - p0.y
        s32_x = p3.x - p2.x
        s32_y = p3.y - p2.y

        denom = s10_x * s32_y - s32_x * s10_y

        if denom == 0 : return None # collinear
        denom_is_positive = denom > 0

        s02_x = p0.x - p2.x
        s02_y = p0.y - p2.y

        s_numer = s10_x * s02_y - s10_y * s02_x
        if (s_numer < 0) == denom_is_positive : return None # no collision
        t_numer = s32_x * s02_y - s32_y * s02_x
        if (t_numer < 0) == denom_is_positive : return None # no collision
        if (s_numer > denom) == denom_is_positive or (t_numer > denom) == denom_is_positive : return None # no collision

        # collision detected
        t = t_numer / denom
        intersection_point = gameMath.Vector2(p0.x + (t * s10_x), p0.y + (t * s10_y))

        return intersection_point

    def Eat(self):
        for region in self.game.world.regions:
            if region.isInRegion(self.position.x, self.position.y, self.radius*1.2):
                for food in region.food:
                    if food.position.distance_squared_to(self.position) < (self.radius * 1.2 + food.nutritions/foodNutritions)**2:
                        self.saturation += food.nutritions
                        self.length += food.nutritions
                        self.game.world.food.remove(food)
                        food.region.food.remove(food)
                        self.lastEaten = self.game.time

    def Die(self):
        if not self.aiControlled:
            self.game.isHumanPlayer = False

        foodPerDrop = foodNutritions * 2
        partInd = 0

        while self.length + self.saturation > foodPerDrop/2:
            part = self.body[partInd]
            xPos = random.randrange(round(part.x - self.radius*1.41) * 100, round(part.x + self.radius*1.41)*100, 1)/100
            yPos = random.randrange(round(part.y - self.radius*1.41) * 100, round(part.y + self.radius*1.41)*100, 1)/100
            self.game.world.DropFood(xPos,yPos, foodPerDrop)
            self.saturation -= foodPerDrop

            partInd += 1
            if partInd >= len(self.body): partInd = 0
        
            
        

    def UpdateLength(self):
        if self.saturation >= self.newPartCost:
            self.body.append(gameMath.Vector2(self.body[-1].x, self.body[-1].y))
            self.saturation -= self.newPartCost
            self.newPartCost *= greedFactor
            self.radius *= sizeGrowFactor

        if self.saturation < 0:
            self.body.pop()
            self.newPartCost *= 1/greedFactor
            self.radius *= 1/sizeGrowFactor
            self.saturation += self.newPartCost*0.95
    

    def ClampAngle(self, angle):
        if angle  > 180: angle -= 360
        if angle  < -180: angle += 360
        return max(min(turningAngle/self.game.fps/self.radius, angle), -turningAngle/self.game.fps/self.radius)
            
    def CalculateFitness(self):
        self.fitness = (self.length - snakeInitialLength) * self.traveled/10
        return self.fitness

# class Part:
#     def __init__(self):
#         self.position


