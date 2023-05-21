# Alpha Brain
A game that trains your brain to increase your alpha brainwaves called neurofeedback. Alpha brainwaves signify a relaxed focus.

## Getting Started
- Run `sh setup.sh` in terminal pointed to your project folder
- Change the `MUSE_MAC_ADDRESS` to your current Muse's address in the `resources/.env` file
- (if the address is unknown, try commenting out `muse = [x for x in muses if x['address'] == muse_mac][0]` in the `stream.py` file)
- Run `stream.py` to connect to Muse and start streaming
- While `stream.py` is running and connected, run `start.py`
- Try to focus on the crosshairs. The smaller the circle, the more focus.

## Hotkeys
- `r` for start or restart
- `Up` and `Down` for adjusting the game time
- `s` for saving the data
- `Esc` for exiting the game