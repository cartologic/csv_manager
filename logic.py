import csv
import os
import subprocess

from django.conf import settings
from django.db import connections
from django.http import JsonResponse
from geonode.geoserver.helpers import ogc_server_settings

from .models import CSVUpload
from .publishers import GeoserverPublisher, GeonodePublisher


def execute(cmd):
    p = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out, err


def get_db_settings():
    settings = ogc_server_settings.datastore_db
    return {
        'db_name': settings.get('NAME'),
        'user': settings.get('USER'),
        'password': settings.get('PASSWORD'),
        'host': settings.get('HOST', 'localhost'),
        'port': settings.get('PORT', 5432),
    }


def create_postgres_table(vrt_path, table_name):
    db_settings = get_db_settings()
    cmd = '''ogr2ogr -nln {} -f PostgreSQL PG:"dbname='{}' host='{}' port='{}'  user='{}' password='{}'" {}'''.format(
        table_name,
        db_settings['db_name'],
        db_settings['host'],
        db_settings['port'],
        db_settings['user'],
        db_settings['password'],
        vrt_path
    )
    return execute(cmd)


def handle_uploaded_file(f, path):
    with open(path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)


def mkdirs(path):
    try:
        os.makedirs(path)
    except:
        print('Path already exist, keep going to next steps...')


def get_field_names(path):
    field_names = []
    with open(path, "rb") as f:
        reader = csv.reader(f)
        i = reader.next()
        field_names.append(i)
    return field_names


def create_xy_vrt(csv_upload_instance):
    # csv layer name is the csv file name without extension
    csv_layer_name = os.path.splitext(csv_upload_instance.csv_name)[0]
    vrt_template = '''<OGRVRTDataSource>
    <OGRVRTLayer name="{}">
        <SrcDataSource>{}</SrcDataSource>
        <GeometryType>wkbPoint</GeometryType>
        <LayerSRS>{}</LayerSRS>
        <GeometryField encoding="PointFromColumns" x="{}" y="{}"/>
    </OGRVRTLayer>
</OGRVRTDataSource>
'''.format(
        csv_layer_name,
        csv_upload_instance.csv_file.path,
        csv_upload_instance.srs,
        csv_upload_instance.lon_field_name,
        csv_upload_instance.lat_field_name
    )
    csv_dir_path = os.path.dirname(csv_upload_instance.csv_file.path)
    path = os.path.join(settings.MEDIA_ROOT, csv_dir_path, '{}.vrt'.format(csv_layer_name))
    # remove file if exists and create another
    if os.path.exists(path):
        os.remove(path)
    with open(path, 'wb') as v:
        v.write(vrt_template)
    return path


def get_rows_count(path):
    with open(path) as f:
        no_of_rows = sum(1 for line in f)
        return no_of_rows - 1


def table_exist(name):
    data_db_name = settings.OGC_SERVER['default']['DATASTORE']
    connection = None
    for c in connections.all():
        if c.alias == data_db_name:
            connection = c
    table_names = connection.introspection.table_names()
    exist = name in table_names
    return exist


def publish_in_geoserver(table_name):
    gs_publisher = GeoserverPublisher()
    gs_publisher.publish_postgis_layer(table_name, table_name)


def publish_in_geonode(table_name, owner):
    gn_publisher = GeonodePublisher(owner=owner)
    return gn_publisher.publish(table_name)


def delete_csv(request):
    csv_instance = CSVUpload.objects.get(pk=request.POST['id'])
    csv_instance.delete()
    json_response = {"status": True, "message": "CSV Deleted successfully", }
    return JsonResponse(json_response, status=200)
