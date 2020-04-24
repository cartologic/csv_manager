# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('csv_manager', '0003_auto_20191126_0603'),
    ]

    operations = [
        migrations.AlterField(
            model_name='csvupload',
            name='geometry_type',
            field=models.CharField(max_length=55, null=True, choices=[(b'POINTXY', b'AS_XY'), (b'POINTXYZ', b'AS_XYZ'), (b'POINTYX', b'AS_YX'), (b'LINESTARTEND', b'start_end'), (b'LINESTRING', b'wkbLineString'), (b'MULTILINESTRING', b'wkbMultiLineString'), (b'MULTIPOINT', b'wkbMultiPoint'), (b'MULTIPOLYGON', b'wkbMultiPolygon'), (b'POINT', b'wkbPoint'), (b'POLYGON', b'wkbPolygon'), (b'UNKNOWN', b'wkbUnknown')]),
        ),
    ]
