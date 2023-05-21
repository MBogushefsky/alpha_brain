import muselsl
from playsound import playsound
import dotenv


def connect_to_muse():
  muse_mac = dotenv.dotenv_values('resources/.env')['MUSE_MAC_ADDRESS']
  muses = muselsl.list_muses()
  if len(muses) == 0:
    connect_to_muse()
  else:
    muse = [x for x in muses if x['address'] == muse_mac][0]
    print(muse['name'])
    playsound("resources/audio/beep_medium.wav")
    muselsl.stream(muse['address'])
    playsound("resources/audio/beep_medium.wav")

if __name__ == '__main__':
  connect_to_muse()
