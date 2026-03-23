[app]

# (str) Title of your application
title = Events Reminder

# (str) Package name
package.name = eventsreminder

# (str) Package domain (needed for android/ios packaging)
package.domain = com.riddik0331

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,json,ttf,otf

# (str) Application versioning (method 1)
version = 1.0.0

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3,kivy==2.3.0,pystray,Pillow,plyer,APScheduler

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET,VIBRATE,RECEIVE_BOOT_COMPLETED,WAKE_LOCK

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 24

# (str) Android NDK version to use
android.ndk = 25b

# (bool) If True, then the app is supported by right-click menu (mouse only)
android.support_right_click_menu = True

# (str) Android logcat filters to use
android.logcat_filters = *:S python:D

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The Android arch to build for
android.archs = arm64-v8a,armeabi-v7a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) XML file to include as an Android app manifest
android.manifest.extra_xml_elements = 

# --- Gradle ---
# (bool) Enable or disable Gradle packager
android.gradle = True

# --- iOS ---
# (str) Name of the iOS project
ios.project_name = EventsReminder

# --- General ---
# (str) Path to your application icon
icon.filename = %(source.dir)s/data/icon.png

# (str) Path to your splash screen image (optional)
splash.filename = %(source.dir)s/data/splash.png

# (list) List of directory to exclude (let empty to not exclude anything)
exclude.dirs = __pycache__,.venv,.git,.qwen,plans,exports,modern-wellness-dashboard

# (bool) Allow to overwrite the generated files
allow_replace = True

# (bool) Do you want to launch the app in debug mode?
debug = False
