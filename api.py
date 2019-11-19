import csv
import io
import os

from django.conf import settings
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.fields import ListField
from tastypie.resources import ModelResource

from .models import CSVUpload


def get_field_names(path):
    field_names = []
    with io.open(path, newline='') as f:
        dialect = csv.Sniffer().sniff(f.readline())
        f.seek(0)
        reader = csv.reader(f, dialect)
        i = reader.next()
        field_names.append(i)
    return field_names


class CSVUploadResource(ModelResource):
    fields_names = ListField()

    class Meta:
        queryset = CSVUpload.objects.all()
        resource_name = 'csv_upload'
        always_return_data = True
        allowed_methods = ['get', ]
        limit = 20
        filtering = {
            "id": ALL,
            "uploaded_at": ALL,
            "updated_at": ALL,
            "user": ALL_WITH_RELATIONS,
            'geometry_type': ALL,
        }
        excludes = ['csv_file', ]

    # modify to return only user's list
    def get_object_list(self, request):
        return super(CSVUploadResource, self).get_object_list(request).filter(user=request.user)

    def dehydrate_fields_names(self, bundle):
        csv_path = bundle.obj.csv_file.path
        full_path = os.path.join(settings.MEDIA_ROOT, csv_path)
        return get_field_names(full_path)
