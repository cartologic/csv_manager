import os
import re
import uuid
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

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
    create_from_wkt,
    cascade_delete_layer
)
from .models import CSVUpload
from .utils import create_connection_string


@login_required
def index(request):
    return render(request, template_name="%s/index.html" % APP_NAME,
                  context={'message': 'Hello from %s' % APP_NAME, 'app_name': APP_NAME})


@login_required
def upload(request):
    error_message = ''
    if request.method == 'POST':
        if request.POST.get('_method') == 'DELETE':
            return delete_csv(request)
        form = CSVUploadForm(request.POST, request.FILES)
        if form.is_valid():
            csv_name = request.FILES['csv_file'].name
            today = datetime.now()
            date_as_path = today.strftime("%Y/%m/%d")
            csv_path = os.path.join(
                'csv_manager', request.user.username, date_as_path, str(uuid.uuid4()))
            full_path = os.path.join(settings.MEDIA_ROOT, csv_path)
            mkdirs(full_path)
            handle_uploaded_file(
                request.FILES['csv_file'], os.path.join(full_path, csv_name))
            features_count = get_rows_count(os.path.join(full_path, csv_name))
            CSVUpload.objects.create(csv_file=os.path.join(csv_path, csv_name), user=request.user,
                                     csv_file_name=csv_name,
                                     features_count=features_count)
            json_response = {"status": True, "message": "CSV uploaded successfully",
                             "field_names": get_field_names(os.path.join(full_path, csv_name))}
            return JsonResponse(json_response, status=200)
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
                                 "message": "Table Already Exists!", }
                return JsonResponse(json_response, status=400)

            if wkt:
                out, err = create_from_wkt(csv_upload_instance, table_name)
            else:
                out, err = create_from_xy(csv_upload_instance, table_name)

            if len(err) > 0:
                print('errors: ', err)
                print('out: ', out)
                if re.search(r'(\berror\b)|(\bError\b)|(\bERROR\b)|(\bFAILURE\b)', err):
                    # Roll back and delete the created table in database
                    delete_layer(connection_string, str(table_name))
                    json_response = {
                        "status": False, "message": "Error While Publishing to database: {}".format(err)}
                    if re.search(r'(\bUTF8\b)', err):
                        json_response = {
                            "status": False,
                            "message": "Seems that some data are not stored in UTF-8 format!".format(err)}
                    return JsonResponse(json_response, status=400)
                warnings = err

            # 5. GeoServer Publish
            try:
                publish_in_geoserver(table_name)
            except Exception as e:
                # Roll back and delete the created table in database
                delete_layer(connection_string, str(table_name))
                cascade_delete_layer(str(table_name))
                json_response = {
                    "status": False, "message": "Could not publish to GeoServer", 'warnings': warnings}
                return JsonResponse(json_response, status=400)

            # 6. GeoNode Publish
            try:
                layer = publish_in_geonode(table_name, owner=request.user)
            except Exception as e:
                # Roll back and delete the created table in database
                # TODO: delete layer from geoserver and geonode if exist
                delete_layer(connection_string, str(table_name))
                cascade_delete_layer(str(table_name))
                json_response = {
                    "status": False, "message": "Could not publish in GeoNode", 'warnings': warnings}
                return JsonResponse(json_response, status=400)

            json_response = {"status": True, "message": "CSV Updated successfully",
                             'warnings': warnings, "layer_name": layer.alternate}
            return JsonResponse(json_response, status=200)
        else:
            return JsonResponse({'message': dict(form.errors.items())}, status=400)
