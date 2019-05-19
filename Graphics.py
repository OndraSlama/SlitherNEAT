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

        self.camX = 0
        self.camY = 0
        self.zoom = 1

        pygame.display.set_caption('Slither')


    def DrawEverything(self, game, cam, zoom, snakeInd, gameSpeed):
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

        if not game.showBotView:
            # Draw regions
            for region in game.world.regions:
                rect = [self.GetX(region.position[0]), self.GetY(region.position[1]), self.Scale(region.position[2]), self.Scale(region.position[3])]
                pygame.draw.rect(self.window, BLUE, rect , max(self.Scale(.1), 1))
            
            # Draw boundaries
            rect = [self.GetX(-game.world.width/2), self.GetY(-game.world.height/2), self.Scale(game.world.width), self.Scale(game.world.height)]
            pygame.draw.rect(self.window, RED, rect , max(self.Scale(1), 4))

            # Draw food
            for food in game.world.food:
                posX = self.GetX(food.position.x)
                posY = self.GetY(food.position.y)
                rad = self.Scale(food.nutritions/foodNutritions)
                if abs(posX - self.pixelWidth/2) < self.pixelWidth/2 and  abs(posY - self.pixelHeight/2) < self.pixelHeight/2:
                    pygame.gfxdraw.aacircle(self.window, posX, posY, rad, GREEN)
                    pygame.gfxdraw.filled_circle(self.window, posX, posY, rad, GREEN)

        # Draw snakes
        for snake in game.snakes:
            if not game.showBotView:
                rad = self.Scale(snake.radius)
                posX = self.GetX(snake.position.x)
                posY = self.GetY(snake.position.y)  
                pygame.gfxdraw.aacircle(self.window, posX, posY, rad, RED)
                pygame.gfxdraw.filled_circle(self.window, posX, posY, rad, RED)
                
                for part in snake.body:
                    posX = self.GetX(part.x)
                    posY = self.GetY(part.y)
                    if abs(posX - self.pixelWidth/2) < self.pixelWidth/2 and  abs(posY - self.pixelHeight/2) < self.pixelHeight/2:
                        pygame.gfxdraw.aacircle(self.window, posX, posY, rad, RED)
                        pygame.gfxdraw.filled_circle(self.window, posX, posY, rad, RED)

            # Draw snakes sensors (sense)
            if (not game.showBotView and not snake.aiControlled) or cam != snake.position: continue
            rad = self.Scale(snake.senseLenght)
            posX = self.GetX(snake.position.x)
            posY = self.GetY(snake.position.y)
            pygame.draw.circle(self.window, YELLOW, (posX, posY), rad, 1)

            for foodPos in snake.sensedFoodPos:
                foodPosX = self.GetX(foodPos.x)
                foodPosY = self.GetY(foodPos.y)
                # pygame.draw.circle(self.window, ORANGE, (posX, posY), 5, 0)
                # pygame.draw.circle(self.window, ORANGE, (foodPosX, foodPosY), 5, 0)
                pygame.draw.aaline(self.window, YELLOW, (posX, posY), (foodPosX, foodPosY))

            for snakePos in snake.sensedSnakes:
                snakePosX = self.GetX(snakePos.x)
                snakePosY = self.GetY(snakePos.y)
                # pygame.draw.circle(self.window, ORANGE, (posX, posY), 5, 0)
                # pygame.draw.circle(self.window, ORANGE, (snakePosX, snakePosY), 5, 0)
                pygame.draw.aaline(self.window, RED, (posX, posY), (snakePosX, snakePosY))

            for endPoint in snake.beamEndPoints:
                endPointX = self.GetX(endPoint.x)
                endPointY = self.GetY(endPoint.y)
                # pygame.draw.circle(self.window, ORANGE, (posX, posY), 5, 0)
                # pygame.draw.circle(self.window, ORANGE, (foodPosX, foodPosY), 5, 0)
                pygame.draw.line(self.window, ORANGE, (posX, posY), (endPointX, endPointY), 1)

            for intersection in snake.intersectionPoints:
                intersectionX = self.GetX(intersection.x)
                intersectionY = self.GetY(intersection.y)
                pygame.draw.circle(self.window, ORANGE, (intersectionX, intersectionY), self.Scale(1), 0)

        self.DrawInfo(game, snakeInd, gameSpeed)

        pygame.display.update()

    def GetX(self, x):
        return round((x * self.scale - self.camX * self.scale)*self.zoom + self.pixelWidth/2)

    def GetY(self, y):
        return round((y * self.scale - self.camY * self.scale)*self.zoom + self.pixelHeight/2)

    def Scale(self, dist):
        return round(dist*self.scale*self.zoom)

    def GetWorldMouse(self, mousePos):
        x = (mousePos[0] - self.pixelWidth/2)/(self.zoom * self.scale) + self.camX
        y = (mousePos[1] - self.pixelHeight/2)/(self.zoom * self.scale) + self.camY
        return gameMath.Vector2(x,y)

    def DrawInfo(self, game, snakeInd, gameSpeed):
        text = "FPS: " + str(round(game.fps, 2))
        self.ShowInfo(text, 30, WHITE, windowWidth*0.05, windowHeight*0.04)
        text = "GameSpeed: " + str(gameSpeed)
        self.ShowInfo(text, 20, WHITE, windowWidth*0.05, windowHeight*0.09)
        text = "Game time: " + str(round(game.time/1000,1)) + " sec"
        self.ShowInfo(text, 20, WHITE, windowWidth*0.05, windowHeight*0.12)
        text = "Generation: " + str(game.population.generation)
        self.ShowInfo(text, 20, WHITE, windowWidth*0.05, windowHeight*0.15)
        text = "Generation time: " + str(round(game.time/1000 - game.lastGAcycle/1000, 1))
        self.ShowInfo(text, 20, WHITE, windowWidth*0.05, windowHeight*0.18)
        
        try:
            text = "Best fitness of previous gen: " + str(round(game.population.bestPlayers[-1].absoluteFitness))
            self.ShowInfo(text, 20, WHITE, windowWidth*0.05, windowHeight*0.21)
            text = "Best fitness overall: " + str(round(game.population.globalBestPlayer.absoluteFitness))
            self.ShowInfo(text, 20, WHITE, windowWidth*0.05, windowHeight*0.24)
        except:
            text = "Best fitness of previous gen: " + str(0)
            self.ShowInfo(text, 20, WHITE, windowWidth*0.05, windowHeight*0.21)
            text = "Best fitness overall: " + str(0)
            self.ShowInfo(text, 20, WHITE, windowWidth*0.05, windowHeight*0.24)
        
        text = "Death of starvation in: " + str(hungerTimeLimit + popHungerTimeScale * game.population.generation) + " sec"
        self.ShowInfo(text, 20, WHITE, windowWidth*0.05, windowHeight*0.27)

        if snakeInd == -1:
            pass
        else:
            if game.snakes[snakeInd].aiControlled:
                self.ShowInfo("Snake number: " + str(snakeInd), 20, WHITE, windowWidth*0.05, windowHeight*0.83)
                
            else:
                self.ShowInfo("Human player", 20, WHITE, windowWidth*0.05, windowHeight*0.83)

            text = "Snake fitness: " + str(round((game.snakes[snakeInd].length - snakeInitialLength) * game.snakes[snakeInd].traveled/10))
            self.ShowInfo(text, 20, WHITE, windowWidth*0.05, windowHeight*0.86)
            text = "Snake length: " + str(round(game.snakes[snakeInd].length))
            self.ShowInfo(text, 20, WHITE, windowWidth*0.05, windowHeight*0.89)
            text = "Traveled distance: " + str(round(game.snakes[snakeInd].traveled))
            self.ShowInfo(text, 20, WHITE, windowWidth*0.05, windowHeight*0.92)
            text = "Last food eaten: " + str(round(game.time/1000 - game.snakes[snakeInd].lastEaten/1000, 1)) + " sec ago"
            self.ShowInfo(text, 20, WHITE, windowWidth*0.05, windowHeight*0.95)

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