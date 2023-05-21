import json
import pygame
import sys
from datetime import datetime
from enum import Enum

from playsound import playsound

from components.data_analysis import DataAnalysis
from components.game_draw import GameDraw
from components.stream_recorder import StreamRecorder


class GameStates(Enum):
  STARTING = 'Starting',
  PAUSED = 'Paused',
  RUNNING = 'Running',
  FINISHED = 'Finished'


pygame.init()
size = width, height = 1080, 720
screen = pygame.display.set_mode((1080, 720))
GAME_LENGTH_SECS = 30
GAME_FONT = pygame.font.Font(pygame.font.match_font('sfnsmono'), 32)
GAME_STATE = GameStates.PAUSED


def draw_state_text():
  text = GAME_FONT.render(f'State: {GAME_STATE.value[0]}', True, (0, 255, 0))
  text_rect = text.get_rect()
  text_rect.center = (width - (text_rect.width / 2) - 10, 20)
  screen.blit(text, text_rect)


def draw_level_text(wave, index, value):
  text = GAME_FONT.render(f'{wave}: {value}', True, (0, 255, 0))
  text_rect = text.get_rect()
  text_rect.center = (width / 2, (height / 4) + (index * 40))
  screen.blit(text, text_rect)


def draw_level_rect(wave, value):
  color = (0, 0, 0)
  order = 0
  if wave == 'delta':
    color = (255, 0, 0)
    order = 1
  elif wave == 'theta':
    color = (255, 140, 0)
    order = 2
  elif wave == 'alpha':
    color = (255, 255, 0)
    order = 3
  elif wave == 'beta':
    color = (0, 255, 0)
    order = 4
  elif wave == 'concentration':
    color = (255, 255, 255)
    order = 6
  elif wave == 'anxiety':
    color = (0, 0, 255)
    order = 7
  pygame.draw.rect(screen, color, pygame.Rect((order * 10), 10, 10, value))


def draw_action_button(text):
  text = GAME_FONT.render(text, True, (0, 255, 0))
  text_rect = text.get_rect()
  text_rect.center = (width / 2, (5 * height) / 6)
  screen.blit(text, text_rect)


def open_game_stats():
  try:
    file = open('game_stats.json', 'r')
    return json.load(file)
  except:
    return {}


def save_game_stats():
  da.stop_analysis()
  game_stats_session['end_date'] = datetime.now()
  game_stats_session['duration_secs'] = GAME_LENGTH_SECS
  game_stats_session['total_score']['delta'] = da.delta_total_score
  game_stats_session['total_score']['theta'] = da.theta_total_score
  game_stats_session['total_score']['alpha'] = da.alpha_total_score
  game_stats_session['total_score']['beta'] = da.beta_total_score
  game_stats_session['total_score']['concentration'] = da.concentration_total_score
  game_stats_session['total_score']['anxiety'] = da.anxiety_total_score
  game_stats['sessions'].append(game_stats_session)
  with open("game_stats.json", "w+") as outfile:
    json.dump(game_stats, outfile, indent=4, default=str)
  playsound("../resources/audio/beep_medium.wav")


if __name__ == "__main__":
  sr = StreamRecorder(False)

  game_stats = open_game_stats()
  if 'sessions' not in game_stats:
    game_stats['sessions'] = []
  game_stats_session = {
    'start_date': datetime.now(),
    'end_date': datetime.now(),
    'duration_secs': 0,
    'total_score': {
      'delta': 0,
      'theta': 0,
      'alpha': 0,
      'beta': 0,
      'concentration': 0,
      'anxiety': 0
    }
  }
  playsound("../resources/audio/beep_medium.wav")
  da = DataAnalysis(GAME_LENGTH_SECS)
  gd = GameDraw(screen, width, height)
  try:
    while True:
      for event in pygame.event.get():
        if event.type == pygame.QUIT:
          sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
          if GAME_STATE == GameStates.PAUSED:
            GAME_STATE = GameStates.RUNNING
            da.reset_analysis(GAME_LENGTH_SECS)
            da.start_analysis()
          elif GAME_STATE == GameStates.RUNNING:
            GAME_STATE = GameStates.PAUSED
            da.reset_analysis(GAME_LENGTH_SECS)
            da.stop_analysis()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_UP:
          if GAME_STATE == GameStates.PAUSED:
            GAME_LENGTH_SECS += 30
            da.reset_analysis(GAME_LENGTH_SECS)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
          if GAME_STATE == GameStates.PAUSED:
            GAME_LENGTH_SECS -= 30
            da.reset_analysis(GAME_LENGTH_SECS)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_s:
          save_game_stats()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
          save_game_stats()
          exit(0)
          break

      data = sr.pull_data()
      da.analyze(data)
      screen.fill((0, 0, 0))

      max_radius = width / 2
      alpha_average = ((data['alphas'][0] + data['alphas'][1]) / 2) / 2
      gd.draw_circle((width / 2, height / 2), max_radius - (max_radius * 0.95 * alpha_average))
      gd.draw_rect((width / 2 - 15, height / 2 - 2.5), 30, 5)
      gd.draw_rect((width / 2 - 2.5, height / 2 - 15), 5, 30)

      if alpha_average >= 0.8:
        playsound('../resources/audio/beep_high.wav')


      draw_state_text()
      text = GAME_FONT.render(f'Time Left: {da.time_left}', True, (255, 255, 255))
      text_rect = text.get_rect()
      text_rect.center = (width - 200, height - 40)
      screen.blit(text, text_rect)

      if da.is_running and (da.secs_left <= 0 or da.secs_left > GAME_LENGTH_SECS):
        game_stats_session['end_date'] = datetime.now()
        game_stats_session['duration_secs'] = GAME_LENGTH_SECS
        game_stats_session['total_score']['delta'] = da.delta_total_score
        game_stats_session['total_score']['theta'] = da.theta_total_score
        game_stats_session['total_score']['alpha'] = da.alpha_total_score
        game_stats_session['total_score']['beta'] = da.beta_total_score
        game_stats_session['total_score']['concentration'] = da.concentration_total_score
        game_stats_session['total_score']['anxiety'] = da.anxiety_total_score
        game_stats['sessions'].append(game_stats_session)
        with open("game_stats.json", "w+") as outfile:
          json.dump(game_stats, outfile, indent=4, default=str)
        playsound("../resources/audio/beep_medium.wav")
        GAME_STATE = GameStates.PAUSED
        da.stop_analysis()
      pygame.display.flip()
  except KeyboardInterrupt:
    print('Closing!')
