import pygame
from data.classes.Board import Board

pygame.init()

# Define a resolução fixa
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600

# Cria a tela com resolução 800x600 (sem fullscreen)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

board = Board(SCREEN_WIDTH, SCREEN_HEIGHT)  # Ajusta o tabuleiro para a resolução

def draw(display):
    display.fill('white')
    board.draw(display)
    pygame.display.update()

running = True
while running:
    mx, my = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:  # Permite sair com ESC
                running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                board.handle_click(mx, my)

    if board.is_in_checkmate('black'):
        print('White wins!')
        running = False
    elif board.is_in_checkmate('white'):
        print('Black wins!')
        running = False

    draw(screen)