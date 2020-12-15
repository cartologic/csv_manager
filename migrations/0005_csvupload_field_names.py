# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csv_manager', '0004_auto_20191229_1621'),
    ]

    operations = [
        migrations.AddField(
            model_name='csvupload',
            name='field_names',
            field=models.TextField(null=True, blank=True),
        ),
    ]
