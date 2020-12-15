# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csv_manager', '0005_csvupload_field_names'),
    ]

    operations = [
        migrations.RenameField(
            model_name='csvupload',
            old_name='field_names',
            new_name='fields_names',
        ),
    ]
