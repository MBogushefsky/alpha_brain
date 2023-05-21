import pygame


class GameDraw:
  def __init__(self, screen, width, height):
    self.screen = screen
    self.width = width
    self.height = height
    self.GAME_FONT = pygame.font.Font(pygame.font.match_font('sfnsmono'), 32)

  def draw_circle(self, position, radius):
    pygame.draw.circle(self.screen, (255, 255, 255), position, radius)

  def draw_rect(self, position, width, height):
    pygame.draw.rect(self.screen, (0, 255, 0), pygame.Rect(position[0], position[1], width, height))
