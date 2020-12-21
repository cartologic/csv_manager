import json
import os

from django.conf import settings
from geonode.api.api import ProfileResource
from tastypie import fields
from tastypie.constants import ALL, ALL_WITH_RELATIONS
from tastypie.fields import ListField
from tastypie.resources import ModelResource

from .logic import get_field_names
from .models import CSVUpload


class CSVUploadResource(ModelResource):
    fields_names = ListField()
    # user = fields.ForeignKey(ProfileResource, 'user', full=True, verbose_name='owner')
    user = fields.DictField()
    source_file = fields.CharField()

    class Meta:
        queryset = CSVUpload.objects.all()
        resource_name = 'csv_upload'
        always_return_data = True
        allowed_methods = ['get', ]
        limit = 100
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
        fields_names = json.loads(bundle.obj.fields_names)
        return fields_names

    def dehydrate_user(self, bundle):
        user = bundle.obj.user
        return {
            'username': user.username,
            'id': user.id,
        }

    def dehydrate_source_file(self, bundle):
        return bundle.obj.csv_file.url
