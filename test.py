import pygame
import time
import random

snake_speed = 15

window_x = 720
window_y = 480

black = pygame.Color (0, 0, 0)
white = pygame.Color (255, 255, 255)
red = pygame.Color (255, 0, 0)
green = pygame.Color (0, 255, 0)
blue = pygame.Color (0, 0, 255)

pygame.init()
pygame.display.set_caption('PBL Snake Game')
game_window = pygame.display.set_mode(window_x, window_y)
fps = pygame.time.clock()


snake_position = [100, 50]
snake_body = [
    [100, 50]
    [90,50]
    [80,50]
    [70,50]
]
fruit_position = [
    random.randrange(1, (window_x//10))*10,
    random.randrange(1, (window_y//10))*10
]
fruit_spwand = True
direction = 'RIGHT'
change_to = direction

score = 0
def show_score(choice, color, font, size):
    score_font = pygame.font.set.SysFont(font, size)
    score_surface = score_font.render('Score : ' + str(score), True, color)
    score_rect = score_surface.get_rect()
    game_window.blit(score_surface, score_rect)
def game_over():
    my_font = pygame.font.SysFont('time new roman', 50)
    game_over_surface = my_font.render('Your score is : ' + str(score), True, red)
    game_over_rect = game_over_surface.get_rect()
    game_over_rect.mid_top = (window_x/2, window_y/2) # sa il puna la mijloc
    