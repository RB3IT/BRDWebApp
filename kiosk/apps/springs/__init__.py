"""
Package for the application.
"""

from django.apps import AppConfig

class KioskSpringsConfig(AppConfig):
    name = "kiosk.apps.springs"
    label = "kiosk.springs"

default_app_config = "kiosk.apps.springs.KioskSpringsConfig"