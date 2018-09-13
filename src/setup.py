from cx_Freeze import setup, Executable
import os
import sys
# Dependencies are automatically detected, but it might need
# fine tuning.
buildOptions = dict(packages = [], excludes = [], includes = ['countdown_qrc_rc'], include_files = ["cd_ico.ico","controller_display_ui.ui","time_display_ui.ui","control_bg_img.jpg","countdown_icon.png","delete.png","delete_red.png","fullscreen.png","fullscreen_red.png","play_pause.png", "play_pause_red.png", "reset.png", "reset_red.png" ])

base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('C:\\Users\\Tmedl\\Documents\\Code\\Countdown\\bin\\Countdown.py', base=base, icon='cd_ico.ico', shortcutName = 'Countdown', shortcutDir = "DesktopFolder")
]

setup(name='Countdown',
      version = '1.0',
      description = 'Staging countdown timer.',
      options = dict(build_exe = buildOptions),
      executables = executables)
