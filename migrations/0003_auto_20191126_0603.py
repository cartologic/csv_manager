# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csv_manager', '0002_auto_20191118_0710'),
    ]

    operations = [
        migrations.AlterField(
            model_name='csvupload',
            name='the_geom_field_name',
            field=models.CharField(max_length=55, null=True),
        ),
    ]
