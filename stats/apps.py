from django.apps import AppConfig
import os

class StatsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stats'

    def ready(self):
        if os.environ.get('RUN_MAIN') == 'true':
            from . import tasks
            tasks.start()
