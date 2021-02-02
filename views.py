import json
import os
import re
import uuid
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render
from geonode.layers.models import Layer

from . import APP_NAME
from .forms import CSVUploadForm, XYPublishForm, WKTPublishForm
from .logic import (
    delete_csv,
    get_rows_count,
    get_field_names,
    mkdirs,
    handle_uploaded_file,
    publish_in_geonode,
    publish_in_geoserver,
    table_exist,
    delete_layer,
    create_from_xy,
    create_from_wkt_csv,
    cascade_delete_layer,
    clean_csv_header,
    valid_headers_as_sql_attributes,
    get_publish_decision,
)
from .models import CSVUpload
from .utils import create_connection_string
from . import __version__ as csv_manager_version


@login_required
def index(request):
    return render(request, template_name="%s/index.html" % APP_NAME,
                  context={'message': 'Hello from %s' % APP_NAME, 'app_name': APP_NAME,
                           "app_version": csv_manager_version})


@login_required
def upload(request):
    error_message = ''
    if request.method == 'POST':
        if request.POST.get('_method') == 'DELETE':
            return delete_csv(request)
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            file_obj = request.FILES['csv_file']
            csv_name = file_obj.name
            today = datetime.now()
            date_as_path = today.strftime("%Y/%m/%d")
            csv_path = os.path.join(
                'csv_manager', request.user.username, date_as_path, str(uuid.uuid4()))
            full_path = os.path.join(settings.MEDIA_ROOT, csv_path)
            file_name_full_path = os.path.join(full_path, csv_name)
            mkdirs(full_path)
            # land the file peacefully in its path
            handle_uploaded_file(file_obj, file_name_full_path)

            # check if valid headers
            valid_headers = valid_headers_as_sql_attributes(
                file_name_full_path)
            # clean them if needed
            if not valid_headers:
                old_fp = file_name_full_path + '.tmp'
                os.rename(file_name_full_path, old_fp)
                clean_csv_header(old_fp, new_fp=file_name_full_path)
                os.remove(old_fp)

            features_count = get_rows_count(file_name_full_path)
            # TODO: make sure the csv has a header!
            # save the field names of a csv file!
            fields_names = json.dumps(get_field_names(file_name_full_path))
            # Save csv_instance
            csv_instance = CSVUpload.objects.create(
                csv_file=os.path.join(csv_path, csv_name),
                user=request.user,
                csv_file_name=csv_name,
                features_count=features_count,
                fields_names=fields_names
            )

            json_response = {
                "status": True,
                "message": "CSV uploaded successfully",
                "id": csv_instance.id,
                "field_names": get_field_names(file_name_full_path)
            }
            return JsonResponse(json_response, status=200)

        return JsonResponse(
            data={"error": "Error While uploading CSV"},
            status=400
        )
        json_response = {
            "status": True, "message": "Error While uploading CSV".format(error_message)}
        return JsonResponse(json_response, status=500)


@login_required
def publish(request):
    warnings = ''
    if request.method == 'POST':
        connection_string = create_connection_string()
        csv_upload_instance = CSVUpload.objects.get(pk=request.POST['id'])
        wkt = 'wkt' in request.POST
        if wkt:
            form = WKTPublishForm(request.POST, instance=csv_upload_instance)
        else:
            form = XYPublishForm(request.POST, instance=csv_upload_instance)
        if form.is_valid():
            # 1. save the model form
            form.save(commit=True)

            # 2. Check if table exist in the database
            table_name = form.cleaned_data['table_name']
            if table_exist(table_name):
                json_response = {"status": False,
                                 "error": "Table Already Exists!", }
                return JsonResponse(json_response, status=400)

            # 3. Create table in postgres using gdal ogr2ogr
            if wkt:
                out, err = create_from_wkt_csv(csv_upload_instance, table_name)
            else:
                out, err = create_from_xy(csv_upload_instance, table_name)

            if len(err) > 0:
                print('errors: ', err)
                print('out: ', out)
                if re.search(r'(\berror\b)|(\bError\b)|(\bERROR\b)|(\bFAILURE\b)', err):
                    # Roll back and delete the created table in database
                    delete_layer(connection_string, str(table_name))
                    json_response = {
                        "status": False, "error": "Error While Publishing to database: {}".format(err)}
                    if re.search(r'(\bUTF8\b)', err):
                        json_response = {
                            "status": False,
                            "error": "Seems that some data are not stored in UTF-8 format!".format(err)}
                    return JsonResponse(json_response, status=400)
                warnings = err

            # 4. GeoServer Publish
            gs_response = publish_in_geoserver(table_name)
            if gs_response.content.find('already exist') > -1:
                # TODO: refresh attrs and statistics
                pass
            elif gs_response.status_code != 201:
                # delete layer from database
                delete_layer(connection_string, str(table_name))
                if gs_response.status_code == 500:
                    # status code 500:
                    # layer exist in geoserver datastore and does not exist in database
                    # hence the database check is done in step 2
                    # cascade delete is a method deletes layer from geoserver and database
                    cascade_delete_layer(str(table_name))
                json_response = {
                    "status": False, "error": "Could not publish to GeoServer, Error Response Code:{}".format(
                        gs_response.status_code), 'warnings': warnings}
                return JsonResponse(json_response, status=400)

            # 5. GeoNode Publish
            try:
                layer = publish_in_geonode(table_name, owner=request.user)
            except Exception as e:
                # Roll back and delete the created table in database, geoserver and geonode if exist
                delete_layer(connection_string, str(table_name))
                cascade_delete_layer(str(table_name))
                try:
                    Layer.objects.get(name=str(table_name)).delete()
                except:
                    print(
                        'Layer {} could not be deleted or does not already exist'.format(table_name))
                print('Error while publishing {} in geonode: {}'.format(
                    table_name, e))
                json_response = {
                    "status": False, "error": "Could not publish in GeoNode", 'warnings': warnings}
                return JsonResponse(json_response, status=400)

            json_response = {"status": True, "message": "CSV Updated successfully",
                             'warnings': warnings, "layer_name": layer.alternate if layer else ""}
            return JsonResponse(json_response, status=200)
        else:
            return JsonResponse({'error': dict(form.errors.items())}, status=400)


@login_required
def data_management_publish(request):
    warnings = ''
    if request.method == 'POST':
        connection_string = create_connection_string()
        csv_upload_instance = CSVUpload.objects.get(pk=request.POST['id'])
        wkt = 'wkt' in request.POST
        if wkt:
            form = WKTPublishForm(request.POST, instance=csv_upload_instance)
        else:
            form = XYPublishForm(request.POST, instance=csv_upload_instance)
        if form.is_valid():
            # 1. save the model form
            form.save(commit=True)

            # 2. Check if table exist in the database
            table_name = form.cleaned_data['table_name']

            publish_decision = get_publish_decision(table_name)
            if publish_decision is 'LINK_WITH_EXCHANGE_LAYER':
                return JsonResponse({}, status=200)

            if publish_decision is 'PUBLISH_DB_TABLE':
                out, error = create_postgis_table_form_csv(
                    request,
                    connection_string,
                    csv_upload_instance,
                    table_name
                )
                if error:
                    return JsonResponse({'error': error}, status=400)
                return JsonResponse({}, status=200)

            if publish_decision is 'REPUBLISH':
                # 3. Create table in postgres using gdal ogr2ogr
                if wkt:
                    out, err = create_from_wkt_csv(
                        csv_upload_instance, table_name)
                else:
                    out, err = create_from_xy(csv_upload_instance, table_name)

                if len(err) > 0:
                    print('errors: ', err)
                    print('out: ', out)
                    if re.search(r'(\berror\b)|(\bError\b)|(\bERROR\b)|(\bFAILURE\b)', err):
                        # Roll back and delete the created table in database
                        delete_layer(connection_string, str(table_name))
                        json_response = {
                            "status": False, "error": "Error While Publishing to database: {}".format(err)}
                        if re.search(r'(\bUTF8\b)', err):
                            json_response = {
                                "status": False,
                                "error": "Seems that some data are not stored in UTF-8 format!".format(err)}
                        return JsonResponse(json_response, status=400)
                    warnings = err

            # 4. GeoServer Publish
            gs_response = publish_in_geoserver(table_name)
            if gs_response.content.find('already exist') > -1:
                # TODO: refresh attrs and statistics
                pass
            elif gs_response.status_code != 201:
                # delete layer from database
                delete_layer(connection_string, str(table_name))
                # if gs_response.status_code == 500:
                #     # status code 500:
                #     # layer exist in geoserver datastore and does not exist in database
                #     # hence the database check is done in step 2
                #     # cascade delete is a method deletes layer from geoserver and database
                #     cascade_delete_layer(str(table_name))
                json_response = {
                    "status": False, "error": "Could not publish to GeoServer, Error Response Code:{}".format(
                        gs_response.status_code), 'warnings': warnings}
                return JsonResponse(json_response, status=400)

            # 5. GeoNode Publish
            try:
                layer = publish_in_geonode(table_name, owner=request.user)
            except Exception as e:
                # Roll back and delete the created table in database, geoserver and geonode if exist
                delete_layer(connection_string, str(table_name))
                # cascade_delete_layer(str(table_name))
                try:
                    Layer.objects.get(name=str(table_name)).delete()
                except:
                    print(
                        'Layer {} could not be deleted or does not already exist'.format(table_name))
                print('Error while publishing {} in geonode: {}'.format(
                    table_name, e))
                json_response = {
                    "status": False, "error": "Could not publish in GeoNode", 'warnings': warnings}
                return JsonResponse(json_response, status=400)

            json_response = {"status": True, "message": "CSV Updated successfully",
                             'warnings': warnings, "layer_name": layer.alternate if layer else ""}
            return JsonResponse(json_response, status=200)
        else:
            return JsonResponse({'error': dict(form.errors.items())}, status=400)


def create_postgis_table_form_csv(request, connection_string, csv_upload_instance, table_name,  wkt=None, ):
    if wkt:
        form = WKTPublishForm(request.POST, instance=csv_upload_instance)
    else:
        form = XYPublishForm(request.POST, instance=csv_upload_instance)

    if form.is_valid():
        form.save()
    else:
        err = "invalid form data!"
        return None, err

    # 3. Create table in postgres using gdal ogr2ogr
    if wkt:
        out, err = create_from_wkt_csv(csv_upload_instance, table_name)
    else:
        out, err = create_from_xy(csv_upload_instance, table_name)

    if str(err).__len__ > 0:
        # TODO: log errors instead of print
        print('errors: ', err)
        print('out: ', out)
        if re.search(r'(\berror\b)|(\bError\b)|(\bERROR\b)|(\bFAILURE\b)', err):
            # Roll back and delete the created table in database
            delete_layer(connection_string, str(table_name))
            return out, err
    return out, err
