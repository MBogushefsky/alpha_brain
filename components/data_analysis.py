import math
from datetime import datetime, timedelta


class DataAnalysis:
  def __init__(self, total_secs):
    self.is_running = False
    self.end_datetime = datetime.now() + timedelta(0, total_secs)
    self.secs_left = total_secs
    self.time_left = self.calc_time_left(self.secs_left)
    self.data = dict()
    self.deltas = []
    self.thetas = []
    self.alphas = []
    self.betas = []
    self.concentrations = []
    self.anxieties = []
    
    self.delta_sum = 0
    self.theta_sum = 0
    self.alpha_sum = 0
    self.beta_sum = 0
    self.concentration_sum = 0
    self.anxiety_sum = 0

    self.wave_total = 0

    self.delta_score = 0
    self.theta_score = 0
    self.alpha_score = 0
    self.beta_score = 0
    self.concentration_score = 0
    self.anxiety_score = 0
    
    self.delta_total_score = 0
    self.theta_total_score = 0
    self.alpha_total_score = 0
    self.beta_total_score = 0
    self.concentration_total_score = 0
    self.anxiety_total_score = 0

  def start_analysis(self):
    self.is_running = True

  def stop_analysis(self):
    self.is_running = False

  def reset_analysis(self, total_secs):
    self.__init__(total_secs)

  def calc_time_left(self, secs_left):
    if (self.secs_left % 60) < 9:
      return f'{math.floor(self.secs_left / 60)}:0{self.secs_left % 60}'
    else:
      return f'{math.floor(self.secs_left / 60)}:{self.secs_left % 60}'

  def analyze(self, data):
    if not self.is_running:
      return
    if self.end_datetime <= datetime.now():
      self.is_running = False
      self.secs_left = 0
      return
    self.secs_left = (self.end_datetime - datetime.now()).seconds
    self.time_left = self.calc_time_left(self.secs_left)
    self.data = data
    self.deltas = data['deltas']
    self.thetas = data['thetas']
    self.alphas = data['alphas']
    self.betas = data['betas']
    self.concentrations = data['concentrations']
    self.anxieties = data['anxieties']
    
    self.delta_sum = self.sum_waves(self.data['deltas'])
    self.theta_sum = self.sum_waves(self.data['thetas'])
    self.alpha_sum = self.sum_waves(self.data['alphas'])
    self.beta_sum = self.sum_waves(self.data['betas'])
    self.concentration_sum = self.sum_waves(self.data['concentrations'])
    self.anxiety_sum = self.sum_waves(self.data['anxieties'])

    self.wave_total = self.delta_sum + self.theta_sum + self.alpha_sum + self.beta_sum

    self.delta_score = self.score_wave(self.wave_total, self.delta_sum)
    self.theta_score = self.score_wave(self.wave_total, self.theta_sum)
    self.alpha_score = self.score_wave(self.wave_total, self.alpha_sum)
    self.beta_score = self.score_wave(self.wave_total, self.beta_sum)
    self.concentration_score = self.score_wave(1, self.concentration_sum)
    self.anxiety_score = self.score_wave(1, self.anxiety_sum)

    self.delta_total_score += self.delta_score
    self.theta_total_score += self.theta_score
    self.alpha_total_score += self.alpha_score
    self.beta_total_score += self.beta_score
    self.concentration_total_score += self.concentration_score
    self.anxiety_total_score += self.anxiety_score

  def sum_waves(self, values):
    wave = 0
    for val in values:
      wave += val
    return wave

  def score_wave(self, total, value):
    if total == 0 or value == 0:
      return 0
    return int((value / total) * 100)