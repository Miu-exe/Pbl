# librarii
import pygame
import time
import random

# viteza

snake_speed = 15

# dimensiuni window

window_x = 720
window_y = 480

# rgb pt window

black = pygame.Color (0, 0, 0)
white = pygame.Color (255, 255, 255)
red = pygame.Color (255, 0, 0)
green = pygame.Color (0, 255, 0)
blue = pygame.Color (0, 0, 255)

# title screen
pygame.init()
pygame.display.set_caption('PBL Snake Game')
game_window = pygame.display.set_mode((window_x, window_y))
# fps manager
fps = pygame.time.Clock()

#start position for snake
snake_position = [100, 50]
#body, primile 4 blocuri
snake_body = [
    [100, 50],
    [90,50],
    [80,50],
    [70,50]
]
#pozitia pt fruit care o ia un loc random unde pare
fruit_position = [
    random.randrange(1, (window_x//10))*10,
    random.randrange(1, (window_y//10))*10
]
# dose friut spwan?
fruit_spwan = True
#directia in care se spwauneaza
direction = 'RIGHT'
change_to = direction
#score display
score = 0

#acual functi cu detalii si font
def show_score(choice, color, font, size):
    score_font = pygame.font.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, color)
    score_rect = score_surface.get_rect()
    game_window.blit(score_surface, score_rect)
    
# game over function
def game_over():
    my_font = pygame.font.SysFont('time new roman', 50)
    game_over_surface = my_font.render('Your score is : ' + str(score), True, red)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.mid_top = (window_x/2, window_y/2) # sa il puna la mijloc

    #blit sa faca textu
    game_window.blit(game_over_surface, game_over_rect)
    pygame.display.flip()

    #dupa 2 secude kaput
    time.sleep(2)

    #stop pygame
    pygame.quit()
    #actual exit
    quit()

# mai function
while True:
    # cum se conecteaza tastatura la joc
    #basicaly daca eu apasa K_ insert name tasta schimba change_to care e directia
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                change_to = 'UP'
            if event.key == pygame.K_DOWN:
                change_to = 'DOWN'
            if event.key == pygame.K_LEFT:
                change_to = 'LEFT'
            if event.key == pygame.K_RIGHT:
                change_to = 'RIGHT'
    
    #failsafe daca doua se apasa deodata
    if change_to == 'UP' and direction != 'DOWN':
        direction = 'UP'
    if change_to == 'DOWN' and direction != 'UP':
        direction = 'DOWN'
    if change_to == 'LEFT' and direction != 'RIGHT':
        direction = 'LEFT'
    if change_to == 'RIGHT' and direction != 'LEFT':
        direction ='RIGHT'
    
    #miscarile sharpelui
    if direction == 'UP':
        snake_position[1] -= 10
    if direction == 'DOWN':
        snake_position[1] += 10
    if direction == 'LEFT':
        snake_position[0] -= 10
    if direction == 'RIGHT':
        snake_position[0] += 10
    
    #sa creasca sharpele
    #si daca manca sa creasca scoreu
    snake_body.insert(0, list(snake_position))
    if snake_position[0] == fruit_position[0] and snake_position[1] == fruit_position[1]:
        score += 10
        fruit_spwan = False
    else:
        snake_body.pop()
    
    if not fruit_spwan:
        fruit = [random.randrange(1, (window_x//10)) * 10,
                 random.randrange(1, (window_y//10)) * 10]
    
    fruit_spwan = True
    game_window.fill(black)

    for pos in snake_body:
        pygame.draw.rect(game_window, green, pygame.Rect(pos[0], pos[1], 10, 10))
    pygame.draw.rect(game_window, white, pygame.Rect(fruit_position[0], fruit_position[1], 10, 10))

    #cand sa dea game over
    if snake_position[0] < 0 or snake_position[0] > window_x-10:
        game_over()
    if snake_position[1] < 0 or snake_position[1] > window_y-10:
        game_over()
    
    # daca se atinge singur
    for block in snake_body[1:]:
        if snake_position[0] == block[0] and snake_position[1] == block[1]:
            game_over()
    
    #sa scoata scoru constat
    show_score(1, white, 'times new roman', 20)

    # sa dea refresh la ecran
    pygame.display.update()

    #fps
    #literaly fps ii viteza de la sharpe
    fps.tick(snake_speed)
