import pygame

class Square:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.x_pos = x * width  # Posição em pixels
        self.y_pos = y * height
        self.occupying_piece = None
        self.highlight = False

        self.abs_x = x * width
        self.abs_y = y * height
        self.abs_pos = (self.abs_x, self.abs_y)
        self.pos = (x, y)
        self.color = 'light' if (x + y) % 2 == 0 else 'dark'
        
       
        self.draw_color = ( 0 , 0 , 0 ) if self.color == 'light' else (200, 200, 255) # Bege + Vinho
        self.highlight_color = (255, 220, 100, 150)  # Amarelo dourado translúcido (para todos os quadrados)    
        self.border_color = (0 , 0 , 0)  # Dourado para bordas
        
        self.occupying_piece = None
        self.coord = self.get_coord()
        self.highlight = False

        self.rect = pygame.Rect(
            self.abs_x,
            self.abs_y,
            self.width,
            self.height
        )

    def get_coord(self):
        columns = 'abcdefgh'
        return columns[self.x] + str(self.y + 1)

    def draw(self, display):
        
        pygame.draw.rect(display, self.draw_color, self.rect)
        
        
        pygame.draw.rect(display, self.border_color, self.rect, 1)  # Borda 
        
        # Destaque de movimento
        if self.highlight:
            highlight_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            highlight_surface.fill(self.highlight_color)
            display.blit(highlight_surface, (self.abs_x, self.abs_y))
        
        # Peça 
        if self.occupying_piece:
            centering_rect = self.occupying_piece.img.get_rect()
            centering_rect.center = self.rect.center
            display.blit(self.occupying_piece.img, centering_rect.topleft)