import os
import shutil

from django.db.models.signals import post_delete
from django.dispatch import receiver

from .models import CSVUpload


@receiver(post_delete, sender=CSVUpload)
def delete_csv_dir(sender, instance, **kwargs):
    file_path = instance.csv_file.path
    if os.path.exists(file_path):
        dir_path = os.path.dirname(file_path)
        # rm files csv, vrt ...
        shutil.rmtree(dir_path, ignore_errors=True)
