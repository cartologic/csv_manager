from django.conf.urls import url, include
from tastypie.api import Api

from . import views, APP_NAME
from .api import CSVUploadResource

v1_api = Api(api_name='csv_api')
v1_api.register(CSVUploadResource())

urlpatterns = [
    url(r'^$', views.index, name='%s.index' % APP_NAME),
    url(r'^upload/', views.upload, name='%s.upload' % APP_NAME),
    url(r'^publish/', views.publish, name='%s.publish' % APP_NAME),
    url(r'^api/', include(v1_api.urls)),
]
