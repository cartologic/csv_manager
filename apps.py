from django.apps import AppConfig


class CsvManagerConfig(AppConfig):
    name = 'csv_manager'
    verbose_name = "CSV Manager"

    def ready(self):
        from .signals import delete_csv_dir
