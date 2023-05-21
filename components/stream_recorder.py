import numpy as np
from pylsl import resolve_byprop, StreamInlet


# Modify these to change aspects of the signal processing
from components import lsl_utils


class Band:
  Delta = 0
  Theta = 1
  Alpha = 2
  Beta = 3
  Gamma = 4


class StreamRecorder:
  def __init__(self, dev_mode):
    self.dev_mode = dev_mode
    if self.dev_mode:
      return
    # Length of the EEG data buffer (in seconds)
    # This buffer will hold last n seconds of data and be used for calculations
    self.BUFFER_LENGTH = 1
    # Length of the epochs used to compute the FFT (in seconds)
    self.EPOCH_LENGTH = 1
    # Amount of overlap between two consecutive epochs (in seconds)
    self.OVERLAP_LENGTH = 0.8
    # Amount to 'shift' the start of each next consecutive epoch
    self.SHIFT_LENGTH = self.EPOCH_LENGTH - self.OVERLAP_LENGTH
    # Index of the channel(s) (electrodes) to be used
    # 0 = left ear, 1 = left forehead, 2 = right forehead, 3 = right ear
    self.INDEX_CHANNEL = [1, 2]
    """ 1. CONNECT TO EEG STREAM """
    # Search for active LSL streams
    print('Looking for an EEG stream...')
    self.streams = resolve_byprop('type', 'EEG', timeout=2)
    if len(self.streams) == 0:
      print('Can\'t find EEG stream.')
      self.__init__(dev_mode)
    # Set active EEG stream to inlet and apply time correction
    print("Start acquiring data")
    self.inlet = StreamInlet(self.streams[0], max_chunklen=12)
    eeg_time_correction = self.inlet.time_correction()
    # Get the stream info and description
    self.info = self.inlet.info()
    description = self.info.desc()
    # Get the sampling frequency
    # This is an important value that represents how many EEG data points are
    # collected in a second. This influences our frequency band calculation.
    # for the Muse 2016, this should always be 256
    self.fs = int(self.info.nominal_srate())
    """ 2. INITIALIZE BUFFERS """
    # Initialize raw EEG data buffer
    self.eeg_buffer = np.zeros((int(self.fs * self.BUFFER_LENGTH), 1))
    self.filter_state = None  # for use with the notch filter
    # Compute the number of epochs in "buffer_length"
    self.n_win_test = int(np.floor((self.BUFFER_LENGTH - self.EPOCH_LENGTH) /
                              self.SHIFT_LENGTH + 1))
    # Initialize the band power buffer (for plotting)
    # bands will be ordered: [delta, theta, alpha, beta]
    self.band_buffer = np.zeros((self.n_win_test, 4))

  def transform_wave(self, value):
    if value < 0:
      return 0
    if value > 1:
      return 1
    return value

  def pull_test_data(self):
    data_dict = dict()
    data_dict['deltas'] = [1]
    data_dict['thetas'] = [2]
    data_dict['alphas'] = [0.5, 0.5]
    data_dict['betas'] = [4]
    data_dict['concentrations'] = [5]
    data_dict['anxieties'] = [6]
    return data_dict

  def pull_data(self):
    if self.dev_mode:
      return self.pull_test_data()
    """ 3.1 ACQUIRE DATA """
    # Obtain EEG data from the LSL stream
    eeg_data, timestamp = self.inlet.pull_chunk(
      timeout=0.25, max_samples=int(self.SHIFT_LENGTH * self.fs))

    # Only keep the channel we're interested in
    deltas = []
    thetas = []
    alphas = []
    betas = []
    concentrations = []
    anxieties = []
    for channel in self.INDEX_CHANNEL:
      try:
        ch_data = np.array(eeg_data)[:, channel]
      except Exception:
        continue

      # Update EEG buffer with the new data
      self.eeg_buffer, self.filter_state = lsl_utils.update_buffer(
        self.eeg_buffer, ch_data, notch=True,
        filter_state=self.filter_state)

      """ 3.2 COMPUTE BAND POWERS """
      # Get newest samples from the buffer
      data_epoch = lsl_utils.get_last_data(self.eeg_buffer,
                                       self.EPOCH_LENGTH * self.fs)

      # Compute band powers
      band_powers = lsl_utils.compute_band_powers(data_epoch, self.fs)
      band_buffer, _ = lsl_utils.update_buffer(self.band_buffer,
                                           np.asarray([band_powers]))
      # Compute the average band powers for all epochs in buffer
      # This helps to smooth out noise
      smooth_band_powers = np.mean(band_buffer, axis=0)

      # print('Delta: ', band_powers[Band.Delta], ' Theta: ', band_powers[Band.Theta],
      #       ' Alpha: ', band_powers[Band.Alpha], ' Beta: ', band_powers[Band.Beta])

      """ 3.3 COMPUTE NEUROFEEDBACK METRICS """
      # These metrics could also be used to drive brain-computer interfaces

      delta = smooth_band_powers[Band.Delta]
      theta = smooth_band_powers[Band.Theta]
      alpha = smooth_band_powers[Band.Alpha]
      beta = smooth_band_powers[Band.Beta]
      concentration = smooth_band_powers[Band.Beta] / \
                      smooth_band_powers[Band.Theta]
      anxiety = smooth_band_powers[Band.Theta] / \
                smooth_band_powers[Band.Alpha]

      # delta = self.transform_wave(delta)
      # theta = self.transform_wave(theta)
      # alpha = self.transform_wave(alpha)
      # beta = self.transform_wave(beta)
      # concentration = self.transform_wave(concentration)
      # anxiety = self.transform_wave(anxiety)

      deltas.append(delta)
      thetas.append(theta)
      alphas.append(alpha)
      betas.append(beta)
      concentrations.append(concentration)
      anxieties.append(anxiety)
      print(f'Channel: {channel}, B: {beta}, A: {alpha}, T: {theta}, D: {delta}')

      # if beta_metric > 0.8:
      #     playsound('../sounds/beep_medium.wav')

      # Alpha Protocol:
      # Simple redout of alpha power, divided by delta waves in order to rule out noise
      # alpha_metric = smooth_band_powers[Band.Alpha] / \
      #     smooth_band_powers[Band.Delta]
      # print('Alpha Relaxation: ', alpha_metric)

      # Beta Protocol:
      # Beta waves have been used as a measure of mental activity and concentration
      # This beta over theta ratio is commonly used as neurofeedback for ADHD
      # beta_metric = smooth_band_powers[Band.Beta] / \
      #     smooth_band_powers[Band.Theta]
      # print('Beta Concentration: ', beta_metric)

      # Alpha/Theta Protocol:
      # This is another popular neurofeedback metric for stress reduction
      # Higher theta over alpha is supposedly associated with reduced anxiety
      # theta_metric = smooth_band_powers[Band.Theta] / \
      #     smooth_band_powers[Band.Alpha]
      # print('Theta Relaxation: ', theta_metric)
    data_dict = dict()
    data_dict['deltas'] = deltas
    data_dict['thetas'] = thetas
    data_dict['alphas'] = alphas
    data_dict['betas'] = betas
    data_dict['concentrations'] = concentrations
    data_dict['anxieties'] = anxieties
    return data_dict
