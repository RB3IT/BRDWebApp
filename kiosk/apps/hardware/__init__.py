"""
Package for the application.
"""

from django.apps import AppConfig

class KioskHardwareConfig(AppConfig):
    name = "kiosk.apps.hardware"
    label = "kiosk.hardware"

default_app_config = "kiosk.apps.hardware.KioskHardwareConfig"