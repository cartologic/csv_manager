import csv
import io
import os
import re
import shutil
import subprocess

from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.db import connections
from django.http import JsonResponse
from geonode.geoserver.helpers import gs_catalog
from geonode.geoserver.helpers import ogc_server_settings
from geonode.layers.models import Layer
from osgeo import ogr

from .constants import GeometryTypeChoices
from .models import CSVUpload
from .publishers import GeoserverPublisher, GeonodePublisher

LONGITUDE = 'longitude'
LATITUDE = 'latitude'


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


def xy_csv_create_postgres_table(csv_path, table_name, srs, X_POSSIBLE_NAMES, Y_POSSIBLE_NAMES):
    db_settings = get_db_settings()
    cmd = '''ogr2ogr -nln {} -f PostgreSQL PG:"dbname='{}' host='{}' port='{}'  user='{}' password='{}'" -oo AUTODETECT_TYPE=YES -oo X_POSSIBLE_NAMES={} -oo Y_POSSIBLE_NAMES={} -a_srs {} {}'''.format(
        table_name,
        db_settings['db_name'],
        db_settings['host'],
        db_settings['port'],
        db_settings['user'],
        db_settings['password'],
        X_POSSIBLE_NAMES,
        Y_POSSIBLE_NAMES,
        srs,
        csv_path,
    )
    return execute(cmd)


def wkt_csv_create_postgres_table(csv_path, table_name, srs, geom_possible_names, geom_type):
    db_settings = get_db_settings()
    cmd = '''ogr2ogr -nln {} -f PostgreSQL PG:"dbname='{}' host='{}' port='{}'  user='{}' password='{}'" -lco GEOM_TYPE="geometry" -oo AUTODETECT_TYPE=YES -oo GEOM_POSSIBLE_NAMES={} -nlt {} -oo KEEP_GEOM_COLUMNS=NO -a_srs {} {}'''.format(
        table_name,
        db_settings['db_name'],
        db_settings['host'],
        db_settings['port'],
        db_settings['user'],
        db_settings['password'],
        geom_possible_names,
        geom_type,  # one of POINT MULTIPOINT POLYGON MULTIPOLYGON LINESTRING MULTILINESTRING
        srs,
        csv_path,
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


def convert_to_sql_column_name(name):
    name = name.strip()
    search_regex = r'[^a-zA-Z0-9]'
    replace_regex = '_'
    return re.sub(search_regex, replace_regex, name).lower()[:50]


def valid_attribute_name(name):
    """
    :param name:
    :return: None true if valid attribute name
    """
    pattern = r'^.*[^a-zA-Z0-9_].*$'
    return not re.match(pattern, name)


def valid_headers_as_sql_attributes(fp):
    field_names = get_field_names(path=fp)
    for name in field_names:
        if not valid_attribute_name(name):
            return False
    return True


def header_has_lon_lat(fp):
    field_names = get_field_names(path=fp)
    lon_exist = LONGITUDE in field_names
    lat_exist = LATITUDE in field_names
    return lon_exist & lat_exist


def clean_csv_header(old_fp, new_fp):
    """
    Convert CSV Columns headers into valid SQL columns headers
    :param old_fp: Old file path to clean headers from
    :param new_fp: New file path which will contain valid SQLheaders csv
    :return:
    """
    with io.open(old_fp, newline='') as f:
        # get the current field names and convert them to valid SQL col. names
        dialect = csv.Sniffer().sniff(f.readline())
        f.seek(0)
        reader = csv.reader(f, dialect)
        field_names = reader.next()
        valid_field_names = [convert_to_sql_column_name(
            name) for name in field_names]

        # convert to csv line string
        line_string = ''
        for name in valid_field_names:
            line_string += dialect.delimiter + name
        line_string = line_string[1:] + '\n'
        line_string = unicode(line_string)

        # delete first row
        f.seek(0)
        current_line = f.readline()
        current_line = ""

        # write to a new file
        with io.open(new_fp, 'w') as fw:
            # 1. write the first line
            fw.write(line_string)
            # 2. copy using shutil for better performance
            # TODO: increasing length in copyfileobj may lead to a better performance
            shutil.copyfileobj(f, fw)


def get_field_names(path):
    field_names = []
    try:
        with io.open(path, newline='') as f:
            dialect = csv.Sniffer().sniff(f.readline())
            f.seek(0)
            reader = csv.reader(f, dialect)
            field_names = reader.next()
    except Exception as e:
        print('Error while reading csv: {} at {}'.format(e, path))
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
    path = os.path.join(settings.MEDIA_ROOT, csv_dir_path,
                        '{}.vrt'.format(csv_layer_name))
    # remove file if exists and create another
    if os.path.exists(path):
        os.remove(path)
    with open(path, 'wb') as v:
        v.write(vrt_template)
    return path


def create_wkt_vrt(csv_upload_instance):
    # csv layer name is the csv file name without extension
    csv_layer_name = os.path.splitext(csv_upload_instance.csv_name)[0]
    csv_dir_path = os.path.dirname(csv_upload_instance.csv_file.path)
    vrt_template = '''<OGRVRTDataSource>
    <OGRVRTLayer name="{}">
        <SrcDataSource>{}</SrcDataSource>
        <GeometryType>{}</GeometryType>
        <LayerSRS>{}</LayerSRS>
        <GeometryField encoding="WKT" field="{}"/>
    </OGRVRTLayer>
</OGRVRTDataSource>
'''.format(
        csv_layer_name,
        csv_upload_instance.csv_file.path,
        GeometryTypeChoices[csv_upload_instance.geometry_type].value,
        csv_upload_instance.srs,
        csv_upload_instance.wkt_field_name,
    )
    path = os.path.join(settings.MEDIA_ROOT, csv_dir_path,
                        '{}.vrt'.format(csv_layer_name))
    # remove file if exists and create another
    if os.path.exists(path):
        os.remove(path)
    with open(path, 'wb') as v:
        v.write(vrt_template)
    return path


def create_from_xy(csv_upload_instance, table_name):
    # create vrt file
    create_xy_vrt(csv_upload_instance)
    X_POSSIBLE_NAMES = str(csv_upload_instance.lon_field_name)
    Y_POSSIBLE_NAMES = str(csv_upload_instance.lat_field_name)
    srs = str(csv_upload_instance.srs)
    csv_path = str(csv_upload_instance.csv_file.path)

    # 4. Create Table in Postgres using OGR2OGR
    out, err = xy_csv_create_postgres_table(
        csv_path, table_name, srs, X_POSSIBLE_NAMES, Y_POSSIBLE_NAMES)
    return out, err


def create_from_wkt_csv(csv_upload_instance, table_name):
    geom_type = str(csv_upload_instance.geometry_type)
    geom_possible_names = str(csv_upload_instance.wkt_field_name)
    srs = str(csv_upload_instance.srs)
    csv_path = str(csv_upload_instance.csv_file.path)
    out, err = wkt_csv_create_postgres_table(
        csv_path, table_name, srs, geom_possible_names, geom_type)
    return out, err


def create_from_wkt_vrt(csv_upload_instance, table_name):
    vrt_path = create_wkt_vrt(csv_upload_instance)
    out, err = create_postgres_table(vrt_path, table_name)
    return out, err


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
    db_exist = name in table_names
    # gs_exist = bool(gs_catalog.get_layer(name))
    try:
        Layer.objects.get(name=name)
        gn_exist = True
    except ObjectDoesNotExist:
        gn_exist = False
    layer_exist = db_exist or gn_exist
    if layer_exist:
        # TODO: using logger instead
        print('Table name \'{}\' is already exist in {}, {}, {}'.format(
            name,
            'database' if db_exist else '',
            # 'geoserver' if gs_exist else '',
            "",
            'geonode' if gn_exist else '',
        ))
    return layer_exist


def get_publish_decision(name):
    data_db_name = settings.OGC_SERVER['default']['DATASTORE']
    connection = None
    for c in connections.all():
        if c.alias == data_db_name:
            connection = c
    table_names = connection.introspection.table_names()
    db_exist = name in table_names

    gn_exist = True
    gn_layer = None
    try:
        gn_layer = Layer.objects.get(name=name)
    except ObjectDoesNotExist:
        gn_exist = False

    if db_exist and gn_exist:
        return 'LINK_WITH_EXCHANGE_LAYER'
    elif db_exist and not gn_exist:
        return 'PUBLISH_GEOSERVER_GEONODE'
    elif not db_exist and gn_exist:
         return 'PUBLISH_DB_TABLE'

    return 'REPUBLISH'


def publish_in_geoserver(table_name):
    gs_publisher = GeoserverPublisher()
    return gs_publisher.publish_postgis_layer(table_name, table_name)


def publish_in_geonode(table_name, owner):
    gn_publisher = GeonodePublisher(owner=owner)
    return gn_publisher.publish(table_name)


def cascade_delete_layer(layer_name):
    gs_publisher = GeoserverPublisher()
    return gs_publisher.delete_layer(layer_name)


def delete_csv(request):
    csv_instance = CSVUpload.objects.get(pk=request.POST['id'])
    csv_instance.delete()
    json_response = {"status": True, "message": "CSV Deleted successfully", }
    return JsonResponse(json_response, status=200)


def delete_layer(connection_string, layer, ):
    """ Deletes a layer in postgreSQL database"""
    # TODO: using logger instead of print
    print('Deleting Layer \'{}\' from database'.format(layer))
    conn = ogr.Open(connection_string)
    try:
        conn.DeleteLayer(layer)
    except ValueError as e:
        # Mostly the layer could not be found to delete!
        print('Error while deleting {}: {}'.format(layer, e.message))
        # Close Connection
    conn = None
