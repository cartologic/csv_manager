# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import csv_manager.models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='CSVUpload',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('csv_file_name', models.CharField(max_length=63)),
                ('csv_file', models.FileField(max_length=500, upload_to=b'', validators=[csv_manager.models.validate_file_extension])),
                ('uploaded_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('lon_field_name', models.CharField(max_length=55, validators=[csv_manager.models.valid_column_name])),
                ('lat_field_name', models.CharField(max_length=55, validators=[csv_manager.models.valid_column_name])),
                ('wkt_field_name', models.CharField(max_length=55, validators=[csv_manager.models.valid_column_name])),
                ('geometry_type', models.CharField(max_length=55, choices=[(b'POINTXY', b'AS_XY'), (b'POINTXYZ', b'AS_XYZ'), (b'POINTYX', b'AS_YX'), (b'LINESTARTEND', b'start_end'), (b'LINE', b'wkbLineString'), (b'MULTILINE', b'wkbMultiLineString'), (b'MULTIPOINT', b'wkbMultiPoint'), (b'MULTIPOLYGON', b'wkbMultiPolygon'), (b'POINT', b'wkbPoint'), (b'POLYGON', b'wkbPolygon'), (b'UNKNOWN', b'wkbUnknown')])),
                ('the_geom_field_name', models.CharField(max_length=55)),
                ('srs', models.CharField(default=b'WGS84', max_length=30)),
                ('features_count', models.IntegerField(default=0)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ['-uploaded_at'],
                'permissions': (('view_csv', 'View CSV'), ('download_csv', 'Download CSV'), ('delete_csv', 'Delete CSV'), ('publish_csv', 'Publish CSV')),
            },
        ),
    ]
