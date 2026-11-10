[app]
title = RetroLens CNN
package.name = retrolens
package.domain = org.offline.retrolens
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,tflite
version = 1.0.0
requirements = python3,kivy==2.3.0,kivymd==1.2.0,pillow,numpy,opencv,plyer
android.permissions = READ_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE
android.api = 33
android.minapi = 24
android.skip_update = False
android.accept_sdk_license = True
android.archs = arm64-v8a, armeabi-v7a

[buildozer]
log_level = 2
warn_on_root = 1
