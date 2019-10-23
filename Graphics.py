import pygame
import pygame.gfxdraw
import pygame.math as gameMath
from Constants import *

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
YELLOW = (255, 255, 0)
GREEN = (0, 255, 50)
BLUE = (50, 50, 255)
GREY = (200, 200, 200)
ORANGE = (200, 100, 50)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
TRANS = (1, 1, 1)

class Graphics:
    def __init__(self, w, h, s):
        self.pixelWidth = w 
        self.pixelHeight = h
        self.scale = s
        self.window = pygame.display.set_mode((self.pixelWidth, self.pixelHeight))
        self.infoSurface = None

        self.camX = 0
        self.camY = 0
        self.zoom = 1

        pygame.display.set_caption('Slither')


    def DrawEverything(self, game, cam, zoom, snakeInd):
        if snakeInd == -1:
            self.camX = 0
            self.camY = 0
            self.zoom = 0.2
        else:
            self.camX = cam.x
            self.camY = cam.y
            self.zoom = zoom        

        # Draw background
        self.window.fill(BLACK)   

        def GetX(x):
            return round((x * self.scale - self.camX * self.scale)*self.zoom + self.pixelWidth/2)     
        def GetY(y):
            return round((y * self.scale - self.camY * self.scale)*self.zoom + self.pixelHeight/2)
        def Scale(dist):
            return round(dist*self.scale*self.zoom)

        if not game.showBotView:
            # Draw regions
            for region in game.world.regions:
                rect = [GetX(region.position[0]), GetY(region.position[1]), Scale(region.position[2]), Scale(region.position[3])]
                pygame.draw.rect(self.window, BLUE, rect , max(Scale(.1), 1))
            
            # Draw boundaries
            rect = [GetX(-game.world.width/2), GetY(-game.world.height/2), Scale(game.world.width), Scale(game.world.height)]
            pygame.draw.rect(self.window, RED, rect , max(Scale(1), 4))

            # Draw food
            for food in game.world.food:
                posX = GetX(food.position.x)
                posY = GetY(food.position.y)
                rad = Scale(food.nutritions/foodNutritions)
                if abs(posX - self.pixelWidth/2) < self.pixelWidth/2 and  abs(posY - self.pixelHeight/2) < self.pixelHeight/2:
                    pygame.gfxdraw.aacircle(self.window, posX, posY, rad, GREEN)
                    pygame.gfxdraw.filled_circle(self.window, posX, posY, rad, GREEN)

        # Draw snakes
        for snake in game.snakes:
            color = snake.color
            if not game.showBotView:
                rad = Scale(snake.radius)
                posX = GetX(snake.position.x)
                posY = GetY(snake.position.y)  
                pygame.gfxdraw.aacircle(self.window, posX, posY, rad, color)
                pygame.gfxdraw.filled_circle(self.window, posX, posY, rad, color)
                
                for part in snake.body:
                    posX = GetX(part.x)
                    posY = GetY(part.y)
                    if abs(posX - self.pixelWidth/2) < self.pixelWidth/2 and  abs(posY - self.pixelHeight/2) < self.pixelHeight/2:
                        pygame.gfxdraw.aacircle(self.window, posX, posY, rad, color)
                        pygame.gfxdraw.filled_circle(self.window, posX, posY, rad, color)

            # Draw snakes sensors (sense)
            if (not game.showBotView and not snake.aiControlled) or cam != snake.position: continue
            rad = Scale(snake.senseLenght)
            posX = GetX(snake.position.x)
            posY = GetY(snake.position.y)
            pygame.draw.circle(self.window, YELLOW, (posX, posY), rad, 1)

            for foodPos in snake.sensedFoodPos:
                foodPosX = GetX(foodPos.x)
                foodPosY = GetY(foodPos.y)
                # pygame.draw.circle(self.window, ORANGE, (posX, posY), 5, 0)
                # pygame.draw.circle(self.window, ORANGE, (foodPosX, foodPosY), 5, 0)
                pygame.draw.aaline(self.window, YELLOW, (posX, posY), (foodPosX, foodPosY))

            for snakePos in snake.sensedSnakes:
                snakePosX = GetX(snakePos.x)
                snakePosY = GetY(snakePos.y)
                # pygame.draw.circle(self.window, ORANGE, (posX, posY), 5, 0)
                # pygame.draw.circle(self.window, ORANGE, (snakePosX, snakePosY), 5, 0)
                pygame.draw.aaline(self.window, RED, (posX, posY), (snakePosX, snakePosY))

            for endPoint in snake.beamEndPoints:
                endPointX = GetX(endPoint.x)
                endPointY = GetY(endPoint.y)
                # pygame.draw.circle(self.window, ORANGE, (posX, posY), 5, 0)
                # pygame.draw.circle(self.window, ORANGE, (foodPosX, foodPosY), 5, 0)
                pygame.draw.line(self.window, ORANGE, (posX, posY), (endPointX, endPointY), 1)

            for intersection in snake.intersectionPoints:
                intersectionX = GetX(intersection.x)
                intersectionY = GetY(intersection.y)
                pygame.draw.circle(self.window, ORANGE, (intersectionX, intersectionY), Scale(1), 0)
        
        if self.infoSurface != None:
            self.window.blit(self.infoSurface, (0,0))

        pygame.display.update()    

    def GetWorldMouse(self, mousePos):
        x = (mousePos[0] - self.pixelWidth/2)/(self.zoom * self.scale) + self.camX
        y = (mousePos[1] - self.pixelHeight/2)/(self.zoom * self.scale) + self.camY
        return gameMath.Vector2(x,y)    

    def ShowInfo(self, string, size, color, x, y):
        myfont = pygame.font.SysFont('Arial', size)        
        textsurface = myfont.render(string, False, color)
        self.window.blit(textsurface,(round(x),round(y)))
    
    def ShowText(self, string, size, color, x, y):
        myfont = pygame.font.SysFont('Arial', size)        
        textsurface = myfont.render(string, False, color)
        textRect = textsurface.get_rect(center=(round(x), round(y)))
        self.window.blit(textsurface,textRect)
        pygame.display.update(textRect)

    def CreateInfo(self, game, snakeInd, gameSpeed):
        self.infoSurface = pygame.Surface((self.pixelWidth, self.pixelHeight), pygame.SRCALPHA)
        # self.infoSurface = self.infoSurface.convert_alpha()

        text = "FPS: " + str(round(game.fps, 2))
        self.BlitText(self.infoSurface, text, 30, WHITE, windowWidth*0.05, windowHeight*0.04)
        text = "GameSpeed: " + str(gameSpeed)
        self.BlitText(self.infoSurface, text, 20, WHITE, windowWidth*0.05, windowHeight*0.09)
        text = "Game time: " + str(round(game.time/1000,1)) + " sec"
        self.BlitText(self.infoSurface, text, 20, WHITE, windowWidth*0.05, windowHeight*0.12)
        text = "Generation: " + str(game.population.generation)
        self.BlitText(self.infoSurface, text, 20, WHITE, windowWidth*0.05, windowHeight*0.15)
        text = "Generation time: " + str(round(game.time/1000 - game.lastGAcycle/1000, 1))
        self.BlitText(self.infoSurface, text, 20, WHITE, windowWidth*0.05, windowHeight*0.18)
        
        try:
            text = "Best fitness of previous gen: " + str(round(game.population.bestPlayers[-1].fitness))
            self.BlitText(self.infoSurface, text, 20, WHITE, windowWidth*0.05, windowHeight*0.21)
            text = "Best fitness overall: " + str(round(game.population.globalBestPlayer.fitness))
            self.BlitText(self.infoSurface, text, 20, WHITE, windowWidth*0.05, windowHeight*0.24)
        except:
            text = "Best fitness of previous gen: " + str(0)
            self.BlitText(self.infoSurface, text, 20, WHITE, windowWidth*0.05, windowHeight*0.21)
            text = "Best fitness overall: " + str(0)
            self.BlitText(self.infoSurface, text, 20, WHITE, windowWidth*0.05, windowHeight*0.24)
        
        text = "Death of starvation in: " + str(hungerTimeLimit + popHungerTimeScale * game.population.generation) + " sec"
        self.BlitText(self.infoSurface, text, 20, WHITE, windowWidth*0.05, windowHeight*0.27)
        text = "Number of species: " + str(round(len(game.population.species)))
        self.BlitText(self.infoSurface, text, 20, WHITE, windowWidth*0.05, windowHeight*0.30)

        if snakeInd == -1:
            pass
        else:
            if game.snakes[snakeInd].aiControlled:
                self.BlitText(self.infoSurface, "Snake number: " + str(snakeInd), 20, WHITE, windowWidth*0.05, windowHeight*0.83)
                
            else:
                self.BlitText(self.infoSurface, "Human player", 20, WHITE, windowWidth*0.05, windowHeight*0.83)

            text = "Snake fitness: " + str(game.snakes[snakeInd].CalculateFitness())
            self.BlitText(self.infoSurface, text, 20, WHITE, windowWidth*0.05, windowHeight*0.86)
            text = "Snake length: " + str(round(game.snakes[snakeInd].length))
            self.BlitText(self.infoSurface, text, 20, WHITE, windowWidth*0.05, windowHeight*0.89)
            text = "Traveled distance: " + str(round(game.snakes[snakeInd].traveled))
            self.BlitText(self.infoSurface, text, 20, WHITE, windowWidth*0.05, windowHeight*0.92)
            text = "Last food eaten: " + str(round(game.time/1000 - game.snakes[snakeInd].lastEaten/1000, 1)) + " sec ago"
            self.BlitText(self.infoSurface, text, 20, WHITE, windowWidth*0.05, windowHeight*0.95)

    def BlitText(self, surface, string, size, color, x, y):
        myfont = pygame.font.SysFont('Arial', size)        
        textsurface = myfont.render(string, False, color)
        textRect = textsurface.get_rect(topleft = (round(x), round(y)))
        surface.blit(textsurface, textRect)        
    
    def BlitCenteredText(self, surface, string, size, color, x, y):
        myfont = pygame.font.SysFont('Arial', size)        
        textsurface = myfont.render(string, False, color)
        textRect = textsurface.get_rect(center=(round(x), round(y)))
        surface.blit(textsurface, textRect)

    def BlitGenom(self, game, option = 2):
        genom = game
        self.genomRect = [round(self.pixelWidth * (option*0.3 - round(option/10))), self.pixelHeight*round(option/10) * 0.3, round(self.pixelWidth * 0.3), round(self.pixelHeight * 0.3)]
        
        def GetX(x):
            return round(self.genomRect[0] + self.genomRect[2] * x)

        def GetY(y):
            return round(self.genomRect[1] + self.genomRect[3] * y)

        def Scale(arg):
            return round(self.genomRect[3] * arg)

        pygame.draw.rect(self.infoSurface, CYAN, self.genomRect, 1)

        # Determine size of node and 
        maxLayerSize = 0
        layerSize = []
        verticalPos = []
        layerPos = []
        for layer in range(genom.layers): 
            layerSize.append(0)
            layerPos.append((layer + 1)/(genom.layers + 1))

        for layer in range(genom.layers):
            for node in genom.nodes:
                if node.layer == layer:
                    layerSize[layer] += 1
            
            if layerSize[layer] > maxLayerSize:
                maxLayerSize = layerSize[layer]

            verticalPos.append(1/(2*layerSize[layer]))

        rad = Scale(min(min(1/(2.2*maxLayerSize), 1/(2.2*genom.layers)), 1/10))

        # determine node position
        for node in genom.nodes:
            layer = node.layer
            posX = GetX(layerPos[layer])
            posY = GetY(verticalPos[layer])
            verticalPos[layer] += 1/layerSize[layer] 

            node.drawPos = gameMath.Vector2(posX, posY)

        for connection in genom.connections:
            if connection.enabled:
                startPosX = round(connection.fromNode.drawPos.x)
                startPosY = round(connection.fromNode.drawPos.y)
                endPosX = round(connection.toNode.drawPos.x)
                endPosY = round(connection.toNode.drawPos.y)
                thickness = max(round(rad * connection.weight / 4), 1)
                if connection.weight == 0: thickness = 0

                if connection.fromNode.layer < connection.toNode.layer:
                    pygame.draw.line(self.infoSurface, RED, (startPosX , startPosY), (endPosX , endPosY), thickness)
                    self.BlitCenteredText(self.infoSurface, str(connection.innovationNo), round(rad / 2), WHITE, (startPosX + endPosX)/2, (startPosY + endPosY)/2)
                else:
                    pygame.draw.line(self.infoSurface, GREEN, (startPosX, startPosY + round(rad / 4)), (endPosX , endPosY + round(rad / 4)), thickness)
                
                # self.BlitCenteredText(self.infoSurface, str(node.number), rad, WHITE, nodeX, nodeY)

        for node in genom.nodes:
            nodeX = round(node.drawPos.x)
            nodeY = round(node.drawPos.y)
            pygame.gfxdraw.aacircle(self.infoSurface, nodeX, nodeY, rad, ORANGE)
            pygame.gfxdraw.filled_circle(self.infoSurface, nodeX, nodeY, rad, ORANGE)
            self.BlitCenteredText(self.infoSurface, str(node.number), rad, WHITE, nodeX, nodeY)
            
