# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import csv_manager.models


class Migration(migrations.Migration):

    dependencies = [
        ('csv_manager', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='csvupload',
            name='geometry_type',
            field=models.CharField(max_length=55, null=True, choices=[(b'POINTXY', b'AS_XY'), (b'POINTXYZ', b'AS_XYZ'), (b'POINTYX', b'AS_YX'), (b'LINESTARTEND', b'start_end'), (b'LINE', b'wkbLineString'), (b'MULTILINE', b'wkbMultiLineString'), (b'MULTIPOINT', b'wkbMultiPoint'), (b'MULTIPOLYGON', b'wkbMultiPolygon'), (b'POINT', b'wkbPoint'), (b'POLYGON', b'wkbPolygon'), (b'UNKNOWN', b'wkbUnknown')]),
        ),
        migrations.AlterField(
            model_name='csvupload',
            name='the_geom_field_name',
            field=models.CharField(max_length=55, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='csvupload',
            name='wkt_field_name',
            field=models.CharField(max_length=55, null=True, validators=[csv_manager.models.valid_column_name]),
        ),
    ]
