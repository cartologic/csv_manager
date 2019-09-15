import os
import re
import uuid
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.forms import ValidationError
from django.http import JsonResponse
from django.shortcuts import render

from . import APP_NAME
from .forms import CSVUploadForm, CSVPublishForm
from .logic import (
    delete_csv,
    get_rows_count,
    get_field_names,
    mkdirs,
    handle_uploaded_file,
    csv_create_postgres_table,
    create_xy_vrt,
    publish_in_geonode,
    publish_in_geoserver,
    table_exist,
    delete_layer
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
            csv_path = os.path.join('csv_manager', request.user.username, date_as_path, str(uuid.uuid4()))
            full_path = os.path.join(settings.MEDIA_ROOT, csv_path)
            mkdirs(full_path)
            handle_uploaded_file(request.FILES['csv_file'], os.path.join(full_path, csv_name))
            CSVUpload.objects.create(csv_file=os.path.join(csv_path, csv_name), user=request.user,
                                     csv_file_name=csv_name,
                                     features_count=get_rows_count(os.path.join(full_path, csv_name)))
            json_response = {"status": True, "message": "CSV uploaded successfully",
                             "field_names": get_field_names(os.path.join(full_path, csv_name))}
            return JsonResponse(json_response, status=200)
        json_response = {"status": True, "message": "Error While uploading CSV".format(error_message)}
        return JsonResponse(json_response, status=500)


@login_required
def publish(request):
    warnings = ''
    if request.method == 'POST':
        connection_string = create_connection_string()
        csv_upload_instance = CSVUpload.objects.get(pk=request.POST['id'])
        form = CSVPublishForm(request.POST, instance=csv_upload_instance)
        if form.is_valid():
            # 1. Check if the table name is valid
            try:
                table_name = form.cleaned_data['table_name']
            except ValidationError as e:
                json_response = {"status": False, "message": "{}".format(e.message), }
                return JsonResponse(json_response, status=500)
            form.save(commit=True)

            # 2. Check if table exist in the database
            if table_exist(table_name):
                json_response = {"status": False, "message": "Table Already Exists!", }
                return JsonResponse(json_response, status=500)

            # 3. create VRT
            # vrt_paht = create_xy_vrt(csv_upload_instance)
            X_POSSIBLE_NAMES = str(csv_upload_instance.lon_field_name)
            Y_POSSIBLE_NAMES = str(csv_upload_instance.lat_field_name)
            srs = str(csv_upload_instance.srs)
            csv_path = str(csv_upload_instance.csv_file.path)

            # 4. Create Table in Postgres using OGR2OGR
            out, err = csv_create_postgres_table(csv_path, table_name, srs, X_POSSIBLE_NAMES, Y_POSSIBLE_NAMES)
            if len(err) > 0:
                print('errors: ', err)
                print('out: ', out)
                if re.search(r'(\berror\b)|(\bError\b)|(\bERROR\b)|(\bFAILURE\b)', err):
                    # Roll back and delete the created table in database
                    delete_layer(connection_string, str(table_name))
                    json_response = {"status": False, "message": "Error While Publishing to PostgreSQL!", }
                    return JsonResponse(json_response, status=500)
                warnings = err

            # 5. GeoServer Publish
            try:
                publish_in_geoserver(table_name)
            except:
                # Roll back and delete the created table in database
                delete_layer(connection_string, str(table_name))
                json_response = {"status": False, "message": "Could not publish to GeoServer", 'warnings': warnings}
                return JsonResponse(json_response, status=500)

            # 6. GeoNode Publish
            try:
                layer = publish_in_geonode(table_name, owner=request.user)
            except:
                # Roll back and delete the created table in database
                delete_layer(connection_string, str(table_name))
                json_response = {"status": False, "message": "Could not publish in GeoNode", 'warnings': warnings}
                return JsonResponse(json_response, status=500)

            json_response = {"status": True, "message": "CSV Updated successfully", 'warnings': warnings, "layer_name": layer.alternate}
            return JsonResponse(json_response, status=200)
        json_response = {"status": False, "message": "Error While Publishing!", }
        return JsonResponse(json_response, status=500)
