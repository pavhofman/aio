# make symlink:
# ln -s config-devel.py config.py

# machine-specific config
ALSA_CARD_INDEX = 0
# AUDIO_DEV = "alsa/plughw:CARD=PCH,DEV=0"
# system with pulseaudio
AUDIO_DEV = "alsa/default"

IPC_SERVER_OPTION = "--input-unix-socket"
VOLUME_PROPERTY = "volume"

# enabling mpv.log file
MPV_LOG_FILE = "/tmp/mpv.log"
# MPV_LOG_FILE = None
