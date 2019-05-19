# Author: Ondrej Slama

import pygame
from Game import *
from Graphics import *
from Constants import *
import pygame.math as gameMath 
import pickle
import os.path

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

pygame.init()

cameraPosition = gameMath.Vector2(0, 0)
zoom = 1
relativeZoom = 1
cameraOnSnake = 0
menuScreen = True
infoScreen = False
startGameTime = 0
lastInfo = 0

graphics = Graphics(windowWidth, windowHeight, pixelScale)
game = Game()
clock = pygame.time.Clock()
font = pygame.font.SysFont("Arial", 12)

gameSpeed = 1
realTime = 0
fps = 0

running = True
while running: 
    # ----------------- EVENTS ------------------------
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False   
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()

            if len(game.snakes) != 0 and game.isHumanPlayer:
                game.snakes[0].sprinting = True
            if event.button == 4: zoom = min(zoom * 1.1, maxZoom)
            if event.button == 5: zoom = max(zoom * 1/1.1, minZoom)
        
        if event.type == pygame.MOUSEBUTTONUP:
            if len(game.snakes) != 0 and game.isHumanPlayer:
                game.snakes[0].sprinting = False 

        if event.type == pygame.KEYDOWN:
            if len(game.snakes) != 0:                
                if event.key == pygame.K_LEFT: cameraOnSnake -= 1
                if event.key == pygame.K_RIGHT: cameraOnSnake += 1
                if cameraOnSnake < -1: cameraOnSnake = len(game.snakes) - 1
                if cameraOnSnake > len(game.snakes) - 1: cameraOnSnake = -1

            if event.key == pygame.K_s and game.population.globalBestPlayer.gameEntity.brain is not None:  # saves best player to file      
                bestPlayer = game.population.globalBestPlayer
                filePath = "savedDeepBrains/1-" + str(numberOfBeams) + "-" + str(numberOfFoodSenses)
                fileName = filePath + "/brain_fitness-" + str(round(bestPlayer.absoluteFitness)) + ".obj"
                if not os.path.exists(filePath):
                    os.makedirs(filePath)
                with open(fileName, 'wb') as f:
                    pickle.dump(bestPlayer.gameEntity.brain, f)
                with open(filePath + "/savedBrain.obj", 'wb') as f:
                    pickle.dump(bestPlayer.gameEntity.brain, f)

                print("Best player saved")
            

    keys = pygame.key.get_pressed()  # currently pressed keys

    if len(game.snakes) == 0:        
        if keys[pygame.K_LEFT]: cameraPosition.x -= 1/zoom
        if keys[pygame.K_RIGHT]: cameraPosition.x += 1/zoom
        if keys[pygame.K_UP]: cameraPosition.y -= 1/zoom
        if keys[pygame.K_DOWN]: cameraPosition.y += 1/zoom     
    else:
        if keys[pygame.K_UP]: gameSpeed = min(gameSpeed + 1, maxGameSpeed)
        if keys[pygame.K_DOWN]: gameSpeed = max(gameSpeed - 1, minGameSpeed)

    if menuScreen:        
        if not infoScreen:
            graphics.ShowText("Neuroevoluting Slither", 50, RED, windowWidth/2, windowHeight*0.2)
            graphics.ShowText("For change in settings press number 1-9:", 30, WHITE, windowWidth/2, windowHeight*0.3)   

            graphics.ShowText("Human player", 20, WHITE, windowWidth*0.2, windowHeight*0.4)
            graphics.ShowText("1: Yes", 20, RED if game.isHumanPlayer else WHITE, windowWidth*0.2, windowHeight*0.5)
            if keys[pygame.K_1]: game.isHumanPlayer = True
            graphics.ShowText("2: No", 20, WHITE if game.isHumanPlayer else RED, windowWidth*0.2, windowHeight*0.55)
            if keys[pygame.K_2]: game.isHumanPlayer = False

            graphics.ShowText("First population", 20, WHITE, windowWidth*0.4, windowHeight*0.4)
            graphics.ShowText("3: From file", 20, RED if game.loadFromFile else WHITE, windowWidth*0.4, windowHeight*0.5)
            if keys[pygame.K_3]: game.loadFromFile = True
            graphics.ShowText("4: Random", 20, WHITE if game.loadFromFile else RED, windowWidth*0.4, windowHeight*0.55)
            if keys[pygame.K_4]: game.loadFromFile = False

            graphics.ShowText("Training", 20, WHITE, windowWidth*0.6, windowHeight*0.4)
            graphics.ShowText("5: Yes", 20, RED if game.training else WHITE, windowWidth*0.6, windowHeight*0.5)
            if keys[pygame.K_5]: game.training = True
            graphics.ShowText("6: No", 20, WHITE if game.training else RED, windowWidth*0.6, windowHeight*0.55)
            if keys[pygame.K_6]: game.training = False

            graphics.ShowText("Show how bots see", 20, WHITE, windowWidth*0.8, windowHeight*0.4)
            graphics.ShowText("7: Yes", 20, RED if game.showBotView else WHITE, windowWidth*0.8, windowHeight*0.5)
            if keys[pygame.K_7]: game.showBotView = True                
            graphics.ShowText("8: No", 20, WHITE if game.showBotView else RED, windowWidth*0.8, windowHeight*0.55)
            if keys[pygame.K_8]: 
                game.showBotView = False
                graphics.window.fill(BLACK)
                pygame.display.update()

            if game.showBotView:
                graphics.ShowText("Warning! When \"Show how bots see\" is enabled, you will not see anything else except your sensor data (input to NN)." , 20, RED, windowWidth*0.5, windowHeight*0.7)
            
            graphics.ShowText("9: Aditional info", 20, WHITE, windowWidth*0.5, windowHeight*0.85)                            

            graphics.ShowText("Press ENTER to continue..." , 30, WHITE, windowWidth*0.5, windowHeight*0.9)
            if keys[pygame.K_KP_ENTER] or keys[pygame.K_RETURN]:
                graphics.window.fill(BLACK)
                pygame.display.update()
                graphics.ShowText("Neuroevoluting Slither", 70, RED, windowWidth/2, windowHeight*0.5)
                menuScreen = False
                if not game.isHumanPlayer:
                    game.killSnake(game.snakes[0])
                startGameTime = pygame.time.get_ticks()
            if keys[pygame.K_9]:
                infoScreen = True
                graphics.window.fill(BLACK)
                pygame.display.update()

        else:
            graphics.ShowText("Created as a seminar project in Applied Computer Science and Control field of study on Brno University of Technology", 15, WHITE, windowWidth/2, windowHeight*0.1)
            graphics.ShowText("Aditional settings can be changed in the Constants file (don't change them too much, didn't have to to test all cases", 15, WHITE, windowWidth/2, windowHeight*0.13)
            graphics.ShowText("Controls", 30, WHITE, windowWidth/2, windowHeight*0.25)
            text = "Snake controled by humam will always try to follow the mouse. By clicking any mouse button, snake will go faster but loose food (length) along the way."
            graphics.ShowText(text, 15, WHITE, windowWidth/2, windowHeight*0.3)
            text = "You can zoom in and out too see larger area or more details (mouse wheel)"
            graphics.ShowText(text, 15, WHITE, windowWidth/2, windowHeight*0.33)
            text = "UP/DOWN arrows will speed up/slow down the game (usefull for long training sesions). LEFT/RIGHT arrows will iterate through snakes (focus camera on them)"
            graphics.ShowText(text, 15, WHITE, windowWidth/2, windowHeight*0.36)
            text = "You can save the best ever snake brain in the current training sesion by pressing \"s\". Feedback should print in console."
            graphics.ShowText(text, 15, WHITE, windowWidth/2, windowHeight*0.39)
            text = "Saved files are divided in folders based on their input configurations (if snake can see with 5 beams and sense with 2 vectors, folder will be named: 1-5-2)."
            graphics.ShowText(text, 15, WHITE, windowWidth/2, windowHeight*0.42)

            graphics.ShowText("About", 30, WHITE, windowWidth/2, windowHeight*0.51)
            text = "Snake bots move on their own based on what they can \"see\" (beams) and \"sense\" (lines to food)."
            graphics.ShowText(text, 15, WHITE, windowWidth/2, windowHeight*0.56)
            text = "The beam controls if there is obstacle in the way by computing intersections with other snakes body and world boundaries"
            graphics.ShowText(text, 15, WHITE, windowWidth/2, windowHeight*0.59)
            text = "and sense are basicaly vectors to the X most nutritious food blobs in defined area around snake."
            graphics.ShowText(text, 15, WHITE, windowWidth/2, windowHeight*0.62)
            text = "Those informations along with the current snake's length are fed to snakes brain (neural network) and its output evaulated as snake movement (see source code)."
            graphics.ShowText(text, 15, WHITE, windowWidth/2, windowHeight*0.65)
            text = "Weights and biases of the neural network evolve as more fit snakes (longer -> more fit) are selected to live in the next generations (see Neuroevolution algorithms)."
            graphics.ShowText(text, 15, WHITE, windowWidth/2, windowHeight*0.68)

            graphics.ShowText("ESC: Back to settings", 20, WHITE, windowWidth*0.5, windowHeight*0.85)
            
            if keys[pygame.K_ESCAPE]: 
                infoScreen = False
                graphics.window.fill(BLACK)
                pygame.display.update()

    # try:
    # ------------------- GAME LOGIC------------------------
    if not menuScreen:
        for g in range(gameSpeed):        
            realTime = pygame.time.get_ticks() - startGameTime 
            if realTime > 2000:    
                mousePosition = graphics.GetWorldMouse(pygame.mouse.get_pos())
                fps = clock.get_fps()
                try:
                    game.Update(mousePosition, fps)
                except Exception as e:
                    print(e)  
                
                if len(game.snakes) != 0:
                    if cameraOnSnake >= len(game.snakes): cameraOnSnake = len(game.snakes)-1
                    cameraPosition = game.snakes[cameraOnSnake].position
        
    
# ------------------- GRAPHICS------------------------
    if not menuScreen:
        if realTime > 2000:
            if len(game.snakes) is not 0:
                relativeZoom = zoom*2/game.snakes[0].radius
            else:
                relativeZoom = zoom

            graphics.DrawEverything(game, cameraPosition, relativeZoom, cameraOnSnake, gameSpeed)  

            # if realTime - lastInfo > 250:
            #     graphics.DrawInfo(game, cameraOnSnake)
            #     lastInfo = realTime
    
    # except Exception as e:
    #     print(e)    


    

        clock.tick(60)

pygame.quit()





